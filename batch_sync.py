#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TongzhouSpace 批量同步工具 (Batch Edition)
用法:
1. python batch_sync.py export  -> 扫描云端未整理文件，生成 pending.json
2. (人工/AI) 编辑 pending.json，填入 course_path 和 type，保存为 resolved.json
3. python batch_sync.py import  -> 读取 resolved.json，自动分发并更新网站
"""

import os
import json
import sys
import datetime
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from modelscope.hub.api import HubApi

# 复用 smart_sync.py 的部分配置，确保一致性
from smart_sync import (
    CONTENT_DIR, MEMORY_FILE, BLACKLIST_FILE, RESOURCES_FILE, INDEX_FILE,
    CATEGORY_MAP, FILE_TYPES, Memory, render_index_md, load_blacklist,
    load_existing_urls, update_local_json_and_render
)

# 初始化记忆库
memory = Memory()

PENDING_FILE = "pending.json"
RESOLVED_FILE = "resolved.json"

def get_file_size_str(size_in_bytes):
    if size_in_bytes > 1024*1024: return f"{size_in_bytes/1024/1024:.1f}MB"
    if size_in_bytes > 1024: return f"{size_in_bytes/1024:.1f}KB"
    return f"{size_in_bytes}B"

def do_export():
    load_dotenv()
    token = os.getenv('MODELSCOPE_TOKEN')
    repo_id = os.getenv('MODELSCOPE_REPO_ID')
    
    if not token or not repo_id:
        print("❌ 错误: 未配置 .env")
        return

    print("🚀 连接 ModelScope (Export Mode)...")
    api = HubApi()
    api.login(token)
    
    try:
        all_files = api.get_model_files(model_id=repo_id, revision='master', recursive=True)
    except Exception as e:
        print(f"❌ API 错误: {e}")
        return

    print("🔍 读取本地状态...")
    existing_urls = load_existing_urls()
    blacklist = load_blacklist()
    
    pending_list = []
    
    print("📦 扫描云端文件...")
    for file_info in all_files:
        if file_info.get('Type') == 'tree': continue
        cloud_path = file_info['Path']
        file_name = cloud_path.split('/')[-1]
        
        # 过滤逻辑
        if cloud_path in blacklist: continue
        
        encoded_path = quote(cloud_path)
        url = f"https://modelscope.cn/models/{repo_id}/resolve/master/{encoded_path}"
        if url in existing_urls: continue
        
        # 忽略系统文件
        if file_name.startswith('.') or file_name in ['README.md', 'resources.json', 'index.md']: continue

        # 尝试智能推荐（辅助 AI 判断）
        suggested_course_path = ""
        suggested_course_name = ""
        
        # 1. 尝试从记忆库匹配文件名
        guess_code = memory.guess_course(file_name)
        if guess_code:
            info = memory.data['courses'][guess_code]
            suggested_course_path = info['path']
            suggested_course_name = info['name']
        
        # 2. 尝试从云端文件夹结构匹配本地文件夹
        if not suggested_course_path:
            cloud_folder = "/".join(cloud_path.split('/')[:-1])
            # 简单的模糊匹配逻辑，可根据需要增强
            pass 

        pending_list.append({
            "filename": file_name,
            "url": url,
            "size": get_file_size_str(file_info['Size']),
            "cloud_path": cloud_path, # 仅供参考
            "suggested_course_name": suggested_course_name, # 仅供参考
            # --- 待填项 ---
            "target_course_path": suggested_course_path, # 关键：填入 content/xxx/xxx 的相对路径
            "type_id": "6" # 关键：填入 1-6
        })

    if not pending_list:
        print("✨ 没有发现待整理的新文件。")
        return

    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(pending_list, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 导出完成！共 {len(pending_list)} 个文件。")
    print(f"📄 请将 '{PENDING_FILE}' 发送给 AI 进行分析处理。")


def do_import():
    if not os.path.exists(RESOLVED_FILE):
        print(f"❌ 找不到 '{RESOLVED_FILE}'。请将 AI 处理后的内容保存为该文件。")
        return
        
    print(f"🚀 开始导入 '{RESOLVED_FILE}'...")
    
    try:
        with open(RESOLVED_FILE, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except Exception as e:
        print(f"❌ JSON 格式错误: {e}")
        return

    success_count = 0
    fail_count = 0
    
    for item in items:
        # 必须字段检查
        target_rel_path = item.get('target_course_path')
        if not target_rel_path:
            print(f"⚠️  跳过: {item['filename']} (未指定 target_course_path)")
            fail_count += 1
            continue
            
        target_dir = CONTENT_DIR / target_rel_path
        
        # 自动创建目标文件夹（修正：不再跳过，直接创建）
        if not target_dir.exists():
            print(f"🔨 创建目录: {target_rel_path}")
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception as e:
                print(f"❌ 无法创建目录 {target_rel_path}: {e}")
                fail_count += 1
                continue
            
        # 执行写入
        try:
            # 关键修正：int(item['type_id'])
            # 这里必须强制转为整数，否则底层排序会崩溃
            type_val = int(item['type_id'])
            
            update_local_json_and_render(
                target_dir, 
                item['filename'], 
                item['url'], 
                item['size'], 
                type_val 
            )
            print(f"✅ 归档: {item['filename']}")
            success_count += 1
        except Exception as e:
            print(f"❌ 写入失败 {item['filename']}: {e}")
            fail_count += 1

    print("-" * 30)
    print(f"🎉 导入完成: 成功 {success_count}, 失败/跳过 {fail_count}")

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python batch_sync.py export  -> 导出未整理文件")
        print("  python batch_sync.py import  -> 导入已处理文件 (resolved.json)")
        return
    
    cmd = sys.argv[1].lower()
    if cmd == 'export':
        do_export()
    elif cmd == 'import':
        do_import()
    else:
        print("❌ 未知命令")

if __name__ == "__main__":
    main()