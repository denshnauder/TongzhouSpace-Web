import re
from pathlib import Path
from scripts.config import CONTENT_DIR, CATEGORY_MAP

class CourseManager:
    def __init__(self):
        self.course_map = {} # { "课程名/别名": PathObj }
        self.scan_courses()

    def scan_courses(self):
        """
        反向解析 content 目录，构建内存映射表。
        原则：严格映射，拒绝模糊猜测。
        """
        self.course_map = {}
        if not CONTENT_DIR.exists(): return

        # 遍历分类目录 (00-xxx, 01-xxx)
        for cat_dir in CONTENT_DIR.iterdir():
            if not cat_dir.is_dir() or cat_dir.name not in CATEGORY_MAP:
                continue

            # 遍历课程目录
            for course_dir in cat_dir.iterdir():
                if not course_dir.is_dir(): continue

                # 1. 注册英文名 (如 advanced-mathematicsB-u)
                self.course_map[course_dir.name.lower()] = course_dir

                # 2. 读取 index.md 注册中文标题 (如 高等数学(B)上)
                index_file = course_dir / "index.md"
                if index_file.exists():
                    title = self._extract_title(index_file)
                    if title:
                        self.course_map[title] = course_dir
                        # 注意：此处已移除 "去括号" 逻辑
                        # "高等数学(B)" 必须严格匹配 "高等数学(B)"，不会退化为 "高等数学"

    def _extract_title(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("title:"):
                        return line.split(":", 1)[1].strip()
        except: pass
        return None

    def find_course(self, keyword):
        """根据关键词查找课程路径"""
        # 1. 精确匹配 (Hash Lookup)
        if keyword in self.course_map:
            return self.course_map[keyword]
        
        # 2. 包含匹配 (Substring)
        # 只有当 课程名 完整出现在 文件名 中时才算命中
        # 例如: 文件名 "高等数学(B)期末.pdf" 包含 课程名 "高等数学(B)" -> 命中
        #      文件名 "高等数学期末.pdf" 不包含 "高等数学(B)" -> 不命中 (正确行为)
        for name, path in self.course_map.items():
            if name in keyword:
                return path
        return None