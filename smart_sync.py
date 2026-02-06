#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ModelScope 云端智能同步工具 (Smart Sync - Type Aware)
修复：
1. 引入文件名关键词智能猜测类型 (不再无脑选教材)
2. 人工认领时，允许手动选择文件类型 (1-6)
"""

import os
import json
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from modelscope.hub.api import HubApi

# ================= 配置 =================
CONTENT_DIR = Path('content')
MEMORY_FILE = Path('scripts/memory.json')
RESOURCES_FILE = 'resources.json'

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

# 资料类型定义
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
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"keywords": {}, "courses": {}}

    def save(self):
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def register_course(self, standard_name, display_name, category_folder):
        self.data['courses'][standard_name] = {
            "name": display_name,
            "category": category_folder,
            "path": f"{category_folder}/{standard_name}"
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

memory = Memory()

# --- 智能类型猜测 ---
def smart_guess_type(filename):
    name = filename.lower()
    ext = os.path.splitext(name)[1]
    
    # 1. 关键词优先
    if any(k in name for k in ['期末', '期中', '试卷', '试题', 'exam', 'quiz', 'test', '真题', '模拟']):
        return '5' # 模拟题
    if any(k in name for k in ['作业', '习题', 'homework', 'assignment', 'problem']):
        return '4' # 作业
    if any(k in name for k in ['笔记', '总结', 'note', 'summary', 'point']):
        return '3' # 笔记
    if any(k in name for k in ['ppt', 'slide', '课件', '讲义', 'presentation']):
        return '2' # 课件
    if any(k in name for k in ['教材', '书', 'textbook', 'edition', 'guide']):
        return '1' # 教材
        
    # 2. 后缀兜底
    if ext in ['.ppt', '.pptx']: return '2'
    if ext in ['.doc', '.docx', '.md', '.txt']: return '3' # 文档默认归笔记/其他
    
    # 3. 默认
    return '6' # 其他

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
    
    print(f"   ✅ 已创建: {cat_folder_name}/{en_name}")
    return en_name, full_path

def smart_sync():
    load_dotenv()
    token = os.getenv('MODELSCOPE_TOKEN')
    repo_id = os.getenv('MODELSCOPE_REPO_ID')
    
    if not token or not repo_id:
        print("❌ 未配置 .env")
        return

    print("🚀 连接 ModelScope...")
    api = HubApi()
    api.login(token)
    
    try:
        all_files = api.get_model_files(model_id=repo_id, revision='master', recursive=True)
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return

    print(f"📦 云端共有 {len(all_files)} 个项目，开始分拣...")
    
    local_courses = {}
    def refresh_local_courses():
        local_courses.clear()
        for path in CONTENT_DIR.rglob('*'):
            if path.is_dir() and (path.parent.name.startswith('0') or path.parent.name.startswith('99')):
                rel = path.relative_to(CONTENT_DIR).as_posix()
                local_courses[rel] = path
    refresh_local_courses()

    success_count = 0
    deleted_count = 0
    
    for file_info in all_files:
        if file_info.get('Type') == 'tree': continue

        cloud_path = file_info['Path']
        file_name = cloud_path.split('/')[-1]
        
        if file_name.startswith('.') or file_name in ['README.md', 'resources.json', 'index.md']:
            continue
            
        target_dir = None
        match_method = ""
        # 默认使用智能猜测，如果是人工认领则允许覆盖
        file_type = smart_guess_type(file_name) 

        # === 1. 完美匹配 ===
        parts = cloud_path.split('/')
        if len(parts) >= 2:
            for i in range(len(parts)-1):
                potential_key = "/".join(parts[:i+2])
                if potential_key in local_courses:
                    target_dir = local_courses[potential_key]
                    match_method = "路径自动匹配"
                    break
            if not target_dir:
                 potential_key = f"{parts[0]}/{parts[1]}"
                 if potential_key in local_courses:
                     target_dir = local_courses[potential_key]
                     match_method = "路径自动匹配"

        # === 2. 记忆匹配 ===
        if not target_dir:
            code = memory.guess_course(file_name)
            if code:
                rel_path = memory.data['courses'][code]['path']
                target_dir = CONTENT_DIR / rel_path
                match_method = f"记忆自动匹配"

        # === 3. 人工判决 ===
        if not target_dir:
            encoded_path = quote(cloud_path)
            url_check = f"https://modelscope.cn/models/{repo_id}/resolve/master/{encoded_path}"
            if is_already_indexed(url_check): continue

            print(f"\n❓ 未知归属: 【{file_name}】")
            print(f"   (原路径: {cloud_path})")
            
            recent_codes = list(memory.data['courses'].keys())
            print("   --- 请选择操作 ---")
            for i, code in enumerate(recent_codes[-5:]):
                print(f"   [{i+1}] 归入: {memory.data['courses'][code]['name']}")
            print("   [0] + 新建课程 (New Course) ✨")
            print("   [s] 跳过 (Keep)")
            print("   [d] 删除 (Delete) 🗑️")
            print("   [f] 搜索课程")

            choice = input("   你的决定: ").strip().lower()
            
            if choice == 'd':
                try:
                    if file_info.get('Type') == 'blob':
                        api.delete_file(path=cloud_path, model_id=repo_id, revision='master', commit_message=f"Del: {file_name}")
                        print(f"   🗑️  已删除")
                        deleted_count += 1
                except: pass
                continue

            if choice == 's': continue
            
            selected_code = None
            if choice == '0':
                new_code, new_path = create_new_course_interactive()
                refresh_local_courses()
                target_dir = new_path
                match_method = "新建并归入"
                memory.add_keyword(file_name, new_code)
                selected_code = new_code
                
            elif choice == 'f':
                keyword = input("   搜索课程名: ").strip()
                selected_code = memory.guess_course(keyword)
            elif choice.isdigit() and 1 <= int(choice) <= 5:
                selected_code = recent_codes[-5:][int(choice)-1]
            
            if selected_code:
                # 只有在人工选择课程后，才询问文件类型
                if not target_dir: # 如果不是新建课程流程进来的(已经拿到target_dir了)，才去获取路径
                    rel_path = memory.data['courses'][selected_code]['path']
                    target_dir = CONTENT_DIR / rel_path
                
                match_method = "人工认领"
                memory.add_keyword(file_name, selected_code)
                
                # 【新增】人工选择文件类型
                guessed = smart_guess_type(file_name)
                print(f"   类型? [1]教材 [2]课件 [3]笔记 [4]作业 [5]试卷 [6]其他")
                t_input = input(f"   (回车默认[{guessed}]): ").strip()
                if t_input in FILE_TYPES:
                    file_type = t_input
                else:
                    file_type = guessed

        # === 执行归档 ===
        if target_dir:
            encoded_path = quote(cloud_path)
            url = f"https://modelscope.cn/models/{repo_id}/resolve/master/{encoded_path}"
            
            # 传入 file_type
            if update_local_json(target_dir, file_name, url, file_info['Size'], file_type):
                print(f"   ✅ [{match_method}] [{FILE_TYPES[file_type]}] -> {target_dir.name}")
                success_count += 1

    print(f"\n🎉 整理完成！更新: {success_count}, 删除: {deleted_count}")
    print("🚀 请运行 python manage.py 刷新网页。")

def is_already_indexed(url):
    for json_path in CONTENT_DIR.rglob(RESOURCES_FILE):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data['files']:
                    if item.get('url') == url: return True
        except: pass
    return False

# 增加 file_type 参数
def update_local_json(course_dir, name, url, size, file_type):
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

    size_str = f"{size}B"
    if size > 1024*1024: size_str = f"{size/1024/1024:.1f}MB"
    elif size > 1024: size_str = f"{size/1024:.1f}KB"

    new_entry = {
        "name": name,
        "url": url,
        "size": size_str,
        "type": file_type, # 使用传入的类型
        "date": "Cloud-Sync"
    }
    data['files'].append(new_entry)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

if __name__ == "__main__":
    smart_sync()