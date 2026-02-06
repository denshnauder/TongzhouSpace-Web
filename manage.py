#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TongzhouSpace 全自动整理脚本 (Smart Edition)
包含功能：
1. 递归解压 & 图片转PDF
2. 智能交互分类 (自动记忆)
3. 智能资料类型猜测 (新增)
4. ModelScope上传 & 直链生成
5. 双层页面自动渲染
6. Git自动推送
"""

import os
import shutil
import json
import zipfile
import datetime
import time
import requests
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from modelscope.hub.api import HubApi
from urllib.parse import quote

# ================= 配置区域 =================
INBOX_DIR = Path('_inbox')
CONTENT_DIR = Path('content')
MEMORY_FILE = Path('scripts/memory.json')
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

IGNORE_FILES = ['.DS_Store', 'Thumbs.db', '.gitignore', '.gitkeep']
# ===========================================

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

    def guess(self, filename):
        for k, v in self.data['keywords'].items():
            if k in filename: return v
        for code, info in self.data['courses'].items():
            if info['name'] in filename or code in filename:
                return code
        return None

    def get_course_path(self, standard_name):
        info = self.data['courses'].get(standard_name)
        if info: return Path(info['path'])
        return None

memory = Memory()

# --- 新增：智能类型猜测 ---
def smart_guess_type(filename):
    name = filename.lower()
    ext = os.path.splitext(name)[1]
    
    # 1. 关键词优先
    if any(k in name for k in ['期末', '期中', '试卷', '试题', 'exam', 'quiz', 'test', '真题', '模拟']):
        return '5' # 试卷
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
    if ext in ['.doc', '.docx', '.md', '.txt']: return '3'
    
    # 3. 默认
    return '6'

# ================= 核心工具函数 =================

def unzip_recursive(target_dir):
    """递归暴力解压"""
    while True:
        zips = list(target_dir.rglob('*.zip'))
        if not zips: break
        extracted_any = False
        for z in zips:
            try:
                extract_path = z.parent / z.stem
                with zipfile.ZipFile(z, 'r') as zf:
                    zf.extractall(extract_path)
                z.unlink()
                extracted_any = True
                print(f"📦 已炸开压缩包: {z.name}")
            except Exception as e:
                print(f"❌ 坏包跳过: {z.name}")
                z.rename(z.with_suffix('.badzip'))
        if not extracted_any: break

def smart_merge_pdf(target_dir):
    """检测纯图片文件夹并合并"""
    subdirs = [d for d in target_dir.iterdir() if d.is_dir()]
    for folder in subdirs:
        files = [f for f in folder.iterdir() if f.is_file() and f.name not in IGNORE_FILES]
        if not files: continue
        images = [f for f in files if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        
        if len(images) > 1 and len(images) / len(files) > 0.9:
            print(f"\n📸 检测到笔记文件夹: [{folder.name}] ({len(images)}张)")
            choice = input(f"   合并为PDF吗? (y/n, 默认y): ").strip().lower()
            if choice == 'n': continue
            try:
                images.sort(key=lambda x: x.name)
                img_list = []
                for img_path in images:
                    img = Image.open(img_path)
                    if img.mode != 'RGB': img = img.convert('RGB')
                    img_list.append(img)
                output_pdf = target_dir / f"{folder.name}.pdf"
                img_list[0].save(output_pdf, save_all=True, append_images=img_list[1:])
                print(f"   ✨ 合并成功: {output_pdf.name}")
                shutil.rmtree(folder)
            except Exception as e:
                print(f"   ❌ 合并失败: {e}")

# ================= 交互与逻辑 =================

def create_new_course():
    print("\n   🏗️  新建课程归档")
    print("   该课程属于哪个大类？")
    cats = list(CATEGORY_MAP.keys())
    for i, cat in enumerate(cats):
        print(f"   [{i}] {cat}")
    
    try:
        c_idx = int(input("   序号: "))
        display_key = cats[c_idx]
        cat_folder_name = CATEGORY_MAP[display_key]
    except:
        print("   默认归入: 99-others")
        cat_folder_name = "99-others"
    
    cn_name = input("   课程中文名 (如 工程热力学): ").strip()
    en_name = input("   文件夹英文名 (如 thermodynamics): ").strip().replace(" ", "-")
    
    memory.register_course(en_name, cn_name, cat_folder_name)
    print(f"   ✅ 已创建: {cat_folder_name}/{cn_name}")
    return en_name

def get_course_interaction(file_path):
    filename = file_path.name
    guess_code = memory.guess(filename)
    if guess_code:
        info = memory.data['courses'].get(guess_code)
        if info:
            print(f"\n🤖 自动识别: 【{filename}】 -> {info['name']}")
            return guess_code

    print(f"\n❓ 未知归属: 【{filename}】")
    recent_courses = list(memory.data['courses'].keys())[-5:]
    if recent_courses:
        print("   最近常选:")
        for idx, code in enumerate(recent_courses):
            print(f"   [{idx+1}] {memory.data['courses'][code]['name']}")
    
    print("   [0] + 新建课程 (New Course)")
    print("   [s] 跳过 (Skip)")
    
    sel = input("   选择序号或输入搜索词: ").strip()
    if sel == 's': return None
    if sel == '0': return create_new_course()
    
    if sel.isdigit() and 1 <= int(sel) <= len(recent_courses):
        return recent_courses[int(sel)-1]
    
    for code, info in memory.data['courses'].items():
        if sel in info['name'] or sel in code:
            return code
            
    print("   ❌ 没找到，建议新建。")
    return get_course_interaction(file_path)

def upload_modelscope(file_path, api, repo_id):
    print(f"   ☁️  正在上传...")
    try:
        file_name = file_path.name
        api.upload_file(
            repo_id=repo_id,
            path_or_fileobj=str(file_path),
            path_in_repo=file_name,
            revision='master'
        )
        
        encoded_name = quote(file_name)
        url = f"https://modelscope.cn/models/{repo_id}/resolve/master/{encoded_name}"
        
        try:
            r = requests.head(url, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                print(f"   ⚠️  警告: 链接返回 {r.status_code}")
        except: pass
        
        return url
    except Exception as e:
        print(f"   ❌ 上传炸了: {e}")
        return None

# ================= 渲染页面 =================

def update_json_and_render(course_code, type_key, file_name, url, size):
    info = memory.data['courses'][course_code]
    course_dir = CONTENT_DIR / info['path']
    course_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = course_dir / RESOURCES_FILE
    data = {"files": []}
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    new_entry = {
        "name": file_name,
        "url": url,
        "size": size,
        "type": type_key,
        "date": datetime.date.today().strftime("%Y-%m-%d")
    }
    
    idx = -1
    for i, item in enumerate(data['files']):
        if item['name'] == file_name:
            idx = i; break
    if idx >= 0: data['files'][idx] = new_entry
    else: data['files'].append(new_entry)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    grouped = {}
    for f in data['files']:
        t = f.get('type', '6')
        if t not in grouped: grouped[t] = []
        grouped[t].append(f)
        
    md_content = f"---\ntitle: {info['name']}\n---\n\n# {info['name']}\n\n"
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
        
    with open(course_dir / INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(md_content)

def render_category_pages():
    print("🎨 正在刷新大类目录...")
    for display_name, folder_name in CATEGORY_MAP.items():
        cat_dir = CONTENT_DIR / folder_name
        if not cat_dir.exists(): continue
        
        courses = [d for d in cat_dir.iterdir() if d.is_dir()]
        courses.sort(key=lambda x: x.name)
        
        content = f"---\ntitle: {display_name}\n---\n\n# 📂 {display_name}\n\n"
        if not courses:
            content += "*暂无课程*\n"
        else:
            for course_dir in courses:
                course_cn_name = course_dir.name
                for code, info in memory.data['courses'].items():
                    if info['path'].replace("\\", "/").endswith(f"{folder_name}/{course_dir.name}"):
                        course_cn_name = info['name']
                        break
                content += f"- 📁 [[{course_dir.name}/index|{course_cn_name}]]\n"
        
        with open(cat_dir / "index.md", "w", encoding='utf-8') as f:
            f.write(content)
    print("   ✅ 大类目录已更新")

def get_size_str(path):
    s = path.stat().st_size
    if s < 1024: return f"{s}B"
    if s < 1024**2: return f"{s/1024:.1f}KB"
    return f"{s/1024**2:.1f}MB"

# ================= 主程序 =================

def main():
    load_dotenv()
    token = os.getenv('MODELSCOPE_TOKEN')
    repo_id = os.getenv('MODELSCOPE_REPO_ID')
    if not token:
        print("❌ 未配置 .env (MODELSCOPE_TOKEN)")
        return
    
    api = HubApi()
    api.login(token)
    
    if not INBOX_DIR.exists():
        INBOX_DIR.mkdir()
        print(f"📂 工作目录 {INBOX_DIR} 已创建，请放入文件。")
        return

    print("🚀 启动整理引擎...")
    unzip_recursive(INBOX_DIR)
    smart_merge_pdf(INBOX_DIR)
    
    files = [f for f in INBOX_DIR.rglob('*') if f.is_file() and f.name not in IGNORE_FILES]
    if not files:
        print("📭 Inbox 是空的。")
        render_category_pages()
    else:
        for f in files:
            if not f.exists(): continue
            course_code = get_course_interaction(f)
            if not course_code: continue
            
            # 【升级】使用智能猜测作为默认值
            guessed_type = smart_guess_type(f.name)
            print(f"   类型? [1]教材 [2]课件 [3]笔记 [4]作业 [5]试卷 [6]其他")
            
            # 动态显示默认值
            t_key = input(f"   (回车默认[{guessed_type} {FILE_TYPES[guessed_type]}]): ").strip()
            if not t_key:
                t_key = guessed_type
            
            mem_key = input("   💡 记住关键词? (回车跳过): ").strip()
            if mem_key: memory.add_keyword(mem_key, course_code)
                
            url = upload_modelscope(f, api, repo_id)
            if url:
                update_json_and_render(course_code, t_key, f.name, url, get_size_str(f))
                f.unlink()
                print("   ✅ 完成，本地已删")

        for d in INBOX_DIR.iterdir():
            if d.is_dir() and not any(d.iterdir()):
                shutil.rmtree(d)
        
        render_category_pages()

    print("\n🚀 正在自动推送到 GitHub...")
    if os.system("git add .") == 0:
        if os.system('git commit -m "Auto-update by manage.py"') == 0:
            os.system("git push")
            print("☁️ 推送完成！")
        else:
            print("⚠️ 无文件变化，跳过提交。")
    else:
        print("❌ Git Add 失败。")

if __name__ == "__main__":
    main()