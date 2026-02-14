import json
import os
from pathlib import Path
from config import INBOX_DIR, PENDING_FILE, IGNORE_PATTERNS
# 引入新写的 Manager
from core.course_manager import CourseManager 

def main():
    if not INBOX_DIR.exists():
        print(f"❌ Inbox 不存在: {INBOX_DIR}")
        return

    # 初始化管理器 (自动扫描现有课程)
    manager = CourseManager()
    
    pending_files = []
    print("🔍 正在扫描 Inbox 并比对本地课程...")

    for root, dirs, files in os.walk(INBOX_DIR):
        for filename in files:
            # 使用正则检查忽略列表
            import re
            if any(re.search(p, filename) for p in IGNORE_PATTERNS):
                continue
            if filename.startswith('.'): continue
            
            # 使用 Manager 查找
            course_path = manager.find_course(filename)
            
            # 如果没找到，加入待办
            if not course_path:
                # 尝试获取贡献者目录名
                rel_path = Path(root).relative_to(INBOX_DIR)
                contributor = rel_path.parts[0] if len(rel_path.parts) > 0 else "Anonymous"
                
                pending_files.append({
                    "filename": filename,
                    "contributor": contributor,
                    "size_str": "Unknown" 
                })
                print(f"   ❓ 未知: {filename}")

    if not pending_files:
        print("\n🎉 本地记忆已覆盖所有文件，无需 AI 介入。直接运行 python manage.py process 即可。")
        return

    # 3. 生成 AI 提示词包
    # 提取现有课程名供 AI 参考
    existing_course_names = list(manager.course_map.keys())

    payload = {
        "instruction": "请分析 pending_files 中的文件名，结合 existing_courses 推断它们属于哪个课程。如果是不存在的课程，标记 is_new_course=true 并建议英文代码。同时推断文件类型 type_id (1=教材, 2=课件, 3=笔记, 4=作业, 5=试卷, 6=其他)。请提取 1-2 个能唯一标识该课程的关键词 (extracted_keywords)。",
        "existing_courses": existing_course_names,
        "pending_files": pending_files
    }

    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    print(f"\n📦 打包完成: {PENDING_FILE}")
    print("👉 请打开该文件，**全选复制**，发送给我 (Gemini)。")
    print("👉 我会返回 resolved.json 给你。")

if __name__ == "__main__":
    main()