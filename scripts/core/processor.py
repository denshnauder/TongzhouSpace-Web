import os
import shutil
import re
from pathlib import Path
from scripts.config import INBOX_DIR, STAGING_DIR, TYPE_KEYWORDS, IGNORE_PATTERNS
from scripts.core.course_manager import CourseManager

class Processor:
    def __init__(self):
        self.manager = CourseManager()

    def guess_type(self, filename):
        name = filename.lower()
        for type_id, keywords in TYPE_KEYWORDS.items():
            if any(k in name for k in keywords):
                return type_id
        return "6" # 其他

    def clean_filename(self, filename):
        # 去除副本标记 (1), - Copy 等
        name = re.sub(r'\(\d+\)|（\d+）|\s-\s副本|\s-\sCopy', '', filename)
        # 去除开头结尾空格
        return name.strip()

    def run(self):
        print("🧹 [Stage 1] 正在处理 Inbox (无需 Token)...")
        if not INBOX_DIR.exists():
            print("   Inbox 不存在。")
            return

        files = [f for f in INBOX_DIR.rglob('*') if f.is_file()]
        count = 0

        for f in files:
            # 过滤垃圾文件
            if any(re.search(p, f.name) for p in IGNORE_PATTERNS):
                continue
            
            # 1. 尝试匹配课程
            # 优先用文件夹名匹配 (贡献者模式)，其次用文件名匹配
            # 逻辑：_inbox/张三/高数/笔记.pdf -> 尝试用 "高数" 匹配
            # 逻辑：_inbox/高数笔记.pdf -> 尝试用 "高数笔记" 匹配
            
            # 简单起见，这里演示基于文件名的匹配
            course_path = self.manager.find_course(f.name) or self.manager.find_course(f.parent.name)
            
            if not course_path:
                print(f"   ⚠️  无法识别课程，跳过: {f.name}")
                continue

            # 2. 猜测类型
            type_id = self.guess_type(f.name)
            
            # 3. 清洗文件名
            new_name = self.clean_filename(f.name)
            
            # 4. 移动到 Staging
            # 结构: _staging/course_relative_path/type_id/filename
            # course_path 是绝对路径，需要转相对路径
            rel_course_path = course_path.relative_to(course_path.parent.parent.parent / "content") # 略显麻烦，简化如下:
            # 实际上 course_path.name 是 auto-structure, parent.name 是 04-xxx
            staging_target = STAGING_DIR / course_path.parent.name / course_path.name / type_id
            staging_target.mkdir(parents=True, exist_ok=True)
            
            target_file = staging_target / new_name
            shutil.move(str(f), str(target_file))
            print(f"   ✅ 已移至 Staging: {course_path.name} / {new_name}")
            count += 1
            
        print(f"🎉 Stage 1 完成，共处理 {count} 个文件。请检查 _staging 目录。")