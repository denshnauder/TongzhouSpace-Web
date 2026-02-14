import json
import os
from pathlib import Path
# 引入配置文件
try:
    from config import INBOX_DIR, CONTENT_DIR, MEMORY_FILE, PENDING_FILE, IGNORE_FILES
except ImportError:
    # 兼容直接运行的情况
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from config import INBOX_DIR, CONTENT_DIR, MEMORY_FILE, PENDING_FILE, IGNORE_FILES

def load_memory():
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"keywords": {}, "courses": {}}

def build_course_map():
    """建立现有课程地图 {相对路径: 课程中文名}"""
    course_map = {}
    if not CONTENT_DIR.exists(): return course_map
    
    for cat_dir in CONTENT_DIR.iterdir():
        if not cat_dir.is_dir() or not cat_dir.name[0].isdigit(): continue
        for course_dir in cat_dir.iterdir():
            if not course_dir.is_dir(): continue
            
            # 读取 index.md 获取中文名，默认为文件夹名
            cn_name = course_dir.name 
            index_file = course_dir / "index.md"
            if index_file.exists():
                try:
                    with open(index_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith("title:"):
                                cn_name = line.split(":", 1)[1].strip()
                                break
                except: pass
            
            # 格式: 04-prof-compulsory/auto-structure
            rel_path = f"{cat_dir.name}/{course_dir.name}"
            course_map[rel_path] = cn_name
    return course_map

def main():
    if not INBOX_DIR.exists():
        print(f"❌ Inbox 不存在: {INBOX_DIR}")
        return

    memory = load_memory()
    existing_courses = build_course_map()
    pending_files = []
    
    print("🔍 正在扫描 Inbox 并比对本地记忆...")

    # 递归扫描
    for root, dirs, files in os.walk(INBOX_DIR):
        for filename in files:
            if filename in IGNORE_FILES or filename.startswith('.'): continue
            
            file_path = Path(root) / filename
            
            # 1. 检查本地记忆是否命中 (模拟 manage.py 的逻辑)
            hit = False
            # A. 关键词命中
            for kw, code in memory.get('keywords', {}).items():
                if kw in filename:
                    hit = True; break
            # B. 课程名命中
            if not hit:
                for code, info in memory.get('courses', {}).items():
                    if info['name'] in filename or code in filename:
                        hit = True; break
            
            # 2. 如果未命中，加入待办列表
            if not hit:
                # 提取贡献者 (子文件夹名)
                contributor = "Anonymous"
                try:
                    rel = file_path.relative_to(INBOX_DIR)
                    if len(rel.parts) > 1:
                        contributor = rel.parts[0]
                except: pass

                pending_files.append({
                    "filename": filename,
                    "contributor": contributor, # 文件夹即署名
                    "size_str": f"{file_path.stat().st_size / 1024:.1f}KB"
                })
                print(f"   ❓ 未知: {filename} <{contributor}>")
    
    if not pending_files:
        print("\n🎉 本地记忆已覆盖所有文件，无需 AI 介入。直接运行 manage.py 即可。")
        return

    # 3. 生成 AI 提示词包
    payload = {
        "instruction": "请分析 pending_files 中的文件名，结合 existing_courses 推断它们属于哪个课程。如果是不存在的课程，标记 is_new_course=true 并建议英文代码。同时推断文件类型 type_id (1=教材, 2=课件, 3=笔记, 4=作业, 5=试卷, 6=其他)。请提取 1-2 个能唯一标识该课程的关键词 (extracted_keywords)。",
        "existing_courses": existing_courses,
        "pending_files": pending_files
    }

    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    print(f"\n📦 打包完成: {PENDING_FILE}")
    print("👉 请打开该文件，**全选复制**，发送给我 (Gemini)。")
    print("👉 我会返回 resolved.json 给你。")

if __name__ == "__main__":
    main()