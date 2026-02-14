import os
import shutil
import re
from pathlib import Path
# 引入 CATEGORY_MAP 以便识别标准分类目录
from scripts.config import INBOX_DIR, STAGING_DIR, TYPE_KEYWORDS, IGNORE_PATTERNS, CATEGORY_MAP
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
        name = re.sub(r'\(\d+\)|（\d+）|\s-\s副本|\s-\sCopy', '', filename)
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
            
            # ================= 核心逻辑升级 =================
            course_path = None
            category_name = None
            course_name = None

            # 策略 A: 显式结构识别 (优先)
            # 检查是否位于 _inbox/分类/课程/ 结构下
            # f.parent = 课程文件夹, f.parent.parent = 分类文件夹
            grandparent_name = f.parent.parent.name
            if grandparent_name in CATEGORY_MAP:
                # 命中！用户使用了标准的归档结构
                category_name = grandparent_name
                course_name = f.parent.name # 这是一个英文名 (e.g. concrete-structures)
                
                # 这种情况下，我们不需要去 content 里查是否存在，直接信任用户
                # 这允许了 "新课程" 的自动创建
                print(f"   🎯 识别到显式结构: {category_name} -> {course_name}")
            
            else:
                # 策略 B: 模糊匹配 (旧逻辑)
                # 尝试通过文件夹名或文件名去 content 里查找已知课程
                found_path = self.manager.find_course(f.name) or self.manager.find_course(f.parent.name)
                if found_path:
                    # found_path 是 absolute path (e.g., .../content/03-basic/fields)
                    category_name = found_path.parent.name
                    course_name = found_path.name

            # ===============================================
            
            if not category_name or not course_name:
                # 为了调试方便，打印一下文件的父目录名
                print(f"   ⚠️  无法识别课程 (父目录: {f.parent.name})，跳过: {f.name}")
                continue

            # 2. 猜测类型
            type_id = self.guess_type(f.name)
            
            # 3. 清洗文件名
            new_name = self.clean_filename(f.name)
            
            # 4. 移动到 Staging
            # 结构: _staging/CATEGORY/COURSE/TYPE/filename
            staging_target = STAGING_DIR / category_name / course_name / type_id
            staging_target.mkdir(parents=True, exist_ok=True)
            
            target_file = staging_target / new_name
            shutil.move(str(f), str(target_file))
            print(f"   ✅ 已移至 Staging: {course_name} / {new_name}")
            count += 1
            
        print(f"🎉 Stage 1 完成，共处理 {count} 个文件。")