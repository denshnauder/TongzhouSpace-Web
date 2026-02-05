#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Link Fixer (链接修复工具)
功能：批量修正 resources.json 中的 ModelScope 链接为 resolve 直链格式
"""

import os
import json
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

# ================= 配置 =================
CONTENT_DIR = Path('content')
RESOURCES_FILE = 'resources.json'
INDEX_FILE = 'index.md'

# 资料类型配置 (用于重新生成 Markdown)
FILE_TYPES = {
    "1": "教材 (Textbooks)",
    "2": "课件 (Slides)",
    "3": "笔记 (Notes)",
    "4": "作业 (Assignments)",
    "5": "期末模拟题 (Mock Exams)",
    "6": "其他 (Resources)"
}
# =======================================

def fix_and_render():
    load_dotenv()
    repo_id = os.getenv('MODELSCOPE_REPO_ID')
    
    if not repo_id:
        print("❌ 错误：找不到 .env 配置，请确保你有 MODELSCOPE_REPO_ID")
        return

    print(f"🔧 开始修复链接，目标仓库: {repo_id}")
    
    # 遍历 content 下的所有子文件夹
    count = 0
    for course_dir in CONTENT_DIR.rglob('*'):
        json_path = course_dir / RESOURCES_FILE
        
        if json_path.exists():
            print(f"   处理: {course_dir.name}")
            
            # 1. 读取数据
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 2. 修正链接
            modified = False
            for item in data.get('files', []):
                file_name = item['name']
                # 强制重新生成 URL
                encoded_name = quote(file_name)
                new_url = f"https://modelscope.cn/models/{repo_id}/resolve/master/{encoded_name}"
                
                # 如果 URL 不一样，就更新
                if item.get('url') != new_url:
                    item['url'] = new_url
                    modified = True
                    count += 1
            
            # 3. 如果有修改，写入 JSON
            if modified:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 4. 重新渲染该课程的 Markdown (顺手刷新页面)
                render_markdown(course_dir, data, course_dir.name) # 暂时用文件夹名当标题，不影响使用

    print(f"\n✅ 修复完成！共修正了 {count} 个文件的链接。")
    print("🚀 请运行 python manage.py 再次刷新一下全局索引，然后 git push。")

def render_markdown(course_dir, data, title):
    """(简化版) 重新生成 Index.md"""
    # 尝试从 memory 找真实标题太麻烦，这里为了修复链接，
    # 我们保留 Frontmatter，只更新下面的列表部分
    
    index_path = course_dir / INDEX_FILE
    existing_content = ""
    file_header = ""
    
    # 读取现有的 Frontmatter (保留原标题)
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 简单提取 --- title: xxx ---
            header_lines = []
            in_header = False
            h1_title = f"# {title}" 
            
            for line in lines:
                header_lines.append(line)
                if line.strip() == '---':
                    if in_header: break # 结束
                    in_header = True
                if line.startswith("# "): h1_title = line.strip()
            
            file_header = "".join(header_lines) + f"\n\n{h1_title}\n\n"
    else:
        file_header = f"---\ntitle: {title}\n---\n\n# {title}\n\n"

    # 生成列表
    grouped = {}
    for f in data['files']:
        t = f.get('type', '6')
        if t not in grouped: grouped[t] = []
        grouped[t].append(f)
        
    md_content = file_header
    for t_key in sorted(grouped.keys()):
        t_name = FILE_TYPES.get(t_key, "其他").split('(')[0]
        md_content += f"## {t_name}\n"
        for item in grouped[t_key]:
            icon = "📄"
            fname = item['name'].lower()
            if fname.endswith('pdf'): icon = "📕"
            elif fname.endswith('zip'): icon = "📦"
            elif fname.endswith('ppt') or fname.endswith('pptx'): icon = "📺"
            
            md_content += f"- {icon} **{item['name']}** <small>({item['size']})</small> [☁️ 点击下载]({item['url']})\n"
        md_content += "\n"
        
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    fix_and_render()