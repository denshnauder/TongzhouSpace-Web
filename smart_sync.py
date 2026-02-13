#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TongzhouSpace 存量链接回收工具 (Final Fix Edition v2.5)
解决痛点：
1. 修复类型错误：兼容传入字符串类型的 size (如 "4.9MB")。
2. 保持路径标准化和黑名单功能。
"""

import os
import json
import datetime
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from modelscope.hub.api import HubApi

# ================= 配置 =================
CONTENT_DIR = Path('content')
MEMORY_FILE = Path('scripts/memory.json')
BLACKLIST_FILE = Path('scripts/blacklist.json') 
RESOURCES_FILE = 'resources.json'
INDEX_FILE = 'index.md'

CATEGORY_MAP = {
    "00 - 通识必修": "00-general-compulsory",
    "01 - 通识选修": "01-general-elective",
    "02 - 公共基础": "02-public-basic",
    "03 - 专业基础": "03-prof-basic",
    "04 - 专业必修": "04-prof-compulsory",
    "05 - 专业选修": "05-prof-elective",
    "06 - 实践环节": "06-practical-training",
    "99 - 其他资源": "99-others"
}

FILE_TYPES = {
    "1": "教材",
    "2": "课件",
    "3": "笔记",
    "4": "作业",
    "5": "试卷",
    "6": "其他"
}
# =======================================

class Memory:
    def __init__(self):
        self.data = self._load()
    
    def _load(self):
        data = {"keywords": {}, "courses": {}}
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except: pass
        
        dirty = False
        for code, info in data['courses'].items():
            if '\\' in info['path']:
                info['path'] = info['path'].replace('\\', '/')
                dirty = True
        if dirty:
            print("🔧 [Auto-Fix] 已修正 memory.json 中的 Windows 路径分隔符")
            self._save_direct(data)
            
        return data

    def _save_direct(self, data):
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self):
        self._save_direct(self.data)

    def register_course(self, standard_name, display_name, category_folder):
        clean_path = f"{category_folder}/{standard_name}"
        self.data['courses'][standard_name] = {
            "name": display_name,
            "category": category_folder,
            "path": clean_path
        }
        self.save()

    def add_keyword(self, keyword, standard_name):
        self.data['keywords'][keyword] = standard_name
        self.save()

    def guess_course(self, filename):
        for k, v in self.data['keywords'].items():
            if k in filename: return v
        for code, info in self.data['courses'].items():
            if info['name'] in filename or code in filename:
                return code
        return None

    def get_display_name_by_path(self, relative_path_str):
        relative_path_str = relative_path_str.replace("\\", "/")
        for code, info in self.data['courses'].items():
            if info['path'] == relative_path_str:
                return info['name']
        return Path(relative_path_str).name

memory = Memory()

def load_blacklist():
    if BLACKLIST_FILE.exists():
        try:
            with open(BLACKLIST_FILE, 'r') as f: return set(json.load(f))
        except: pass
    return set()

def add_to_blacklist(path):
    bl = load_blacklist()
    bl.add(path)
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(list(bl), f)

def safe_guess_type(filename):
    name = filename.lower()
    if any(k in name for k in ['期末', '期中', '试卷', '试题', 'exam', 'quiz', 'test', '真题', '模拟']):
        return '5' 
    return '6' 

def create_new_course_interactive():
    print("\n   🏗️  新建课程向导")
    cats = list(CATEGORY_MAP.keys())
    for i, cat in enumerate(cats):
        print(f"   [{i}] {cat}")
    
    try:
        c_idx = int(input("   序号: "))
        display_key = cats[c_idx]
        cat_folder_name = CATEGORY_MAP[display_key]
    except:
        cat_folder_name = "99-others"
    
    cn_name = input("   课程中文名: ").strip()
    en_name = input("   文件夹英文名: ").strip().replace(" ", "-")
    
    memory.register_course(en_name, cn_name, cat_folder_name)
    full_path = CONTENT_DIR / cat_folder_name / en_name
    full_path.mkdir(parents=True, exist_ok=True)
    return en_name, full_path

def render_index_md(course_dir, course_name, data):
    grouped = {}
    for f in data['files']:
        # 确保 type 是字符串，防止 int 导致的 key error
        t = str(f.get('type', '6'))
        if t not in grouped: grouped[t] = []
        grouped[t].append(f)
        
    md_content = f"---\ntitle: {course_name}\n---\n\n# {course_name}\n\n"
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
    
    with open(course_dir / INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(md_content)

def update_local_json_and_render(course_dir, name, url, size, file_type):
    course_dir.mkdir(parents=True, exist_ok=True)
    json_path = course_dir / RESOURCES_FILE
    
    data = {"files": []}
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: pass
    
    for item in data['files']:
        if item['url'] == url: return False

    # === 关键修正：类型兼容 ===
    if isinstance(size, str):
        size_str = size  # 已经是字符串 (如 "4.9MB")，直接用
    else:
        # 是数字，进行格式化
        try:
            size_val = float(size)
            size_str = f"{int(size_val)}B"
            if size_val > 1024*1024: size_str = f"{size_val/1024/1024:.1f}MB"
            elif size_val > 1024: size_str = f"{size_val/1024:.1f}KB"
        except:
            size_str = str(size) # 兜底
    # ========================

    new_entry = {
        "name": name,
        "url": url,
        "size": size_str,
        "type": str(file_type),
        "date": datetime.date.today().strftime("%Y-%m-%d")
    }
    data['files'].append(new_entry)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    rel_path = course_dir.relative_to(CONTENT_DIR).as_posix()
    course_name = memory.get_display_name_by_path(rel_path)
    render_index_md(course_dir, course_name, data)
    return True

def load_existing_urls():
    urls = set()
    for json_path in CONTENT_DIR.rglob(RESOURCES_FILE):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get('files', []):
                    if 'url' in item: urls.add(item['url'])
        except: pass
    return urls

def smart_sync():
    load_dotenv()
    token = os.getenv('MODELSCOPE_TOKEN')
    repo_id = os.getenv('MODELSCOPE_REPO_ID')
    
    if not token or not repo_id:
        print("❌ 未配置 .env")
        return

    print("🚀 连接 ModelScope (Final Fix Mode)...")
    api = HubApi()
    api.login(token)
    
    try:
        all_files = api.get_model_files(model_id=repo_id, revision='master', recursive=True)
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return

    print("🔍 扫描本地白名单...")
    existing_urls = load_existing_urls()
    blacklist = load_blacklist()
    print(f"   ✅ 已忽略 {len(existing_urls)} 个已整理, {len(blacklist)} 个僵尸文件")

    print(f"📦 云端扫描中...")
    local_courses = {}
    for path in CONTENT_DIR.rglob('*'):
        if path.is_dir() and (path.parent.name.startswith('0') or path.parent.name.startswith('99')):
            rel = path.relative_to(CONTENT_DIR).as_posix()
            local_courses[rel] = path

    processed_count = 0
    skipped_count = 0

    for file_info in all_files:
        if file_info.get('Type') == 'tree': continue
        cloud_path = file_info['Path']
        file_name = cloud_path.split('/')[-1]
        
        if cloud_path in blacklist:
            skipped_count += 1
            continue

        encoded_path = quote(cloud_path)
        current_url = f"https://modelscope.cn/models/{repo_id}/resolve/master/{encoded_path}"
        if current_url in existing_urls:
            skipped_count += 1
            continue

        cloud_folder = "/".join(cloud_path.split('/')[:-1])
        if not cloud_folder: cloud_folder = "(根目录)"

        if file_name.startswith('.') or file_name in ['README.md', 'resources.json', 'index.md']: continue
            
        target_dir = None
        
        parts = cloud_path.split('/')
        if len(parts) >= 2:
            for i in range(len(parts)-1):
                p_key = "/".join(parts[:i+2])
                if p_key in local_courses:
                    target_dir = local_courses[p_key]
                    break
        
        if not target_dir:
            code = memory.guess_course(file_name)
            if code:
                rel = memory.data['courses'][code]['path']
                target_dir = CONTENT_DIR / rel

        if not target_dir:
            print(f"\n❓ 迷路文件: {file_name}")
            print(f"   ☁️  位置: {cloud_folder}")
            print("   [d] 删除/拉黑 [s] 跳过 [0] 新建课程")
            
            all_codes = list(memory.data['courses'].keys())
            all_codes.sort(key=lambda x: (
                memory.data['courses'][x]['category'], 
                memory.data['courses'][x]['name']
            ))
            
            for i, c in enumerate(all_codes): 
                info = memory.data['courses'][c]
                cat_short = info['category'].split('-')[0] 
                print(f"   [{i+1}] {info['name']:<15} \t| {cat_short}")
            
            c = input("   指派: ").strip().lower()
            if c == 'd':
                try:
                    print("   🗑️  尝试云端删除...")
                    api.delete_file(path=cloud_path, model_id=repo_id, revision='master', commit_message=f"Del: {file_name}")
                    print("   ✅ 云端已删除")
                except Exception as e:
                    print(f"   ❌ 删除失败 (可能是权限保护): {e}")
                    confirm_bl = input("   👉 是否添加到【本地拉黑】列表，永不再见? [y/n]: ").strip().lower()
                    if confirm_bl == 'y':
                        add_to_blacklist(cloud_path)
                        print("   💀 已加入黑名单")
                continue

            if c == 's': continue
            if c == '0':
                _, target_dir = create_new_course_interactive()
            elif c.isdigit() and 1 <= int(c) <= len(all_codes):
                target_dir = CONTENT_DIR / memory.data['courses'][all_codes[int(c)-1]]['path']

        if target_dir:
            current_type = safe_guess_type(file_name)
            current_name = file_name
            
            while True:
                t_name = FILE_TYPES.get(current_type, "未知")
                print(f"\n   --------------------------------")
                print(f"   ☁️  云端位置: {cloud_folder}")
                print(f"   📄 文件名称: {current_name}")
                print(f"   📂 存入课程: {target_dir.name}")
                print(f"   🏷️  文件类型: [{current_type}] {t_name}")
                print(f"   --------------------------------")
                
                op = input("   👉 [y]写入 [n]跳过 [d]删除/拉黑 [r]重命名 [1-6]改类型: ").strip().lower()
                
                if op == 'y':
                    if update_local_json_and_render(target_dir, current_name, current_url, file_info['Size'], current_type):
                        print(f"   ✅ 已归档")
                        existing_urls.add(current_url) 
                        processed_count += 1
                    break
                    
                elif op == 'n':
                    print("   💨 已跳过")
                    break
                    
                elif op == 'd':
                    try:
                        print("   🗑️  尝试云端删除...")
                        api.delete_file(path=cloud_path, model_id=repo_id, revision='master', commit_message=f"Del: {file_name}")
                        print("   ✅ 云端已删除")
                    except Exception as e:
                        print(f"   ❌ 删除失败: {e}")
                        confirm_bl = input("   👉 是否添加到【本地拉黑】列表? [y/n]: ").strip().lower()
                        if confirm_bl == 'y':
                            add_to_blacklist(cloud_path)
                            print("   💀 已加入黑名单")
                    break
                
                elif op == 'r':
                    new_n = input(f"   新文件名 (原: {current_name}): ").strip()
                    if new_n: current_name = new_n
                
                elif op in FILE_TYPES:
                    current_type = op
                
                else:
                    print("   ❌ 指令无效")

    print(f"\n🎉 全部完成！本次新增: {processed_count}, 静默跳过: {skipped_count}")

if __name__ == "__main__":
    smart_sync()