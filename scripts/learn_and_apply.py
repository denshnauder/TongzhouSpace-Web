import json
import shutil
from pathlib import Path
try:
    from config import MEMORY_FILE, RESOLVED_FILE, STAGING_DIR
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from config import MEMORY_FILE, RESOLVED_FILE, STAGING_DIR

def load_json(path):
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    if not RESOLVED_FILE.exists():
        print(f"❌ 找不到 {RESOLVED_FILE}。请先把 AI 的回复保存为这个文件。")
        return

    # 这里假设 AI 返回的是一个列表
    resolutions = load_json(RESOLVED_FILE)
    if not isinstance(resolutions, list):
        print("⚠️ resolved.json 格式不对，应该是一个列表。")
        return

    memory = load_json(MEMORY_FILE)
    if "keywords" not in memory: memory["keywords"] = {}
    if "courses" not in memory: memory["courses"] = {}

    print(f"🚀 开始吸收 AI 知识 (共 {len(resolutions)} 条)...")
    
    new_kw_count = 0
    new_course_count = 0

    for item in resolutions:
        # 必须有的字段
        filename = item.get('filename')
        course_code = item.get('course_code')
        keywords = item.get('extracted_keywords', [])
        
        # 可选字段 (新课程相关)
        target_path = item.get('target_course_path') # e.g. "04-prof-compulsory/auto-structure"
        course_name = item.get('course_name')        # e.g. "汽车构造"
        is_new = item.get('is_new_course', False)

        if not course_code: continue

        # 1. 注册新课程
        if is_new and target_path and course_code not in memory['courses']:
            memory['courses'][course_code] = {
                "name": course_name if course_name else course_code,
                "path": target_path,
                "category": target_path.split('/')[0] if '/' in target_path else "99-others"
            }
            new_course_count += 1
            print(f"   🌱 [新课] {course_code} -> {target_path}")

        # 2. 学习关键词
        if keywords:
            for kw in keywords:
                # 只有当这个关键词还没被注册，或者指向不明时才更新
                if kw and kw not in memory['keywords']:
                    memory['keywords'][kw] = course_code
                    new_kw_count += 1
                    print(f"   🧠 [记忆] '{kw}' -> {course_code}")
    
    save_memory(memory)
    print("\n" + "="*40)
    print(f"✅ 学习完毕！")
    print(f"   - 新增关键词: {new_kw_count}")
    print(f"   - 新增课程:   {new_course_count}")
    print("👉 现在请运行你的 `python manage.py`。它现在应该能自动识别这些文件了！")

if __name__ == "__main__":
    main()