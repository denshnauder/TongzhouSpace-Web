import re
from pathlib import Path
from scripts.config import CONTENT_DIR, CATEGORY_MAP, COURSE_ALIAS_MAP

class CourseManager:
    def __init__(self):
        self.course_map = {} # Key: 中文名/英文名/别名, Value: Path对象
        self.scan_courses()

    def scan_courses(self):
        """反向解析 content 目录，构建内存映射表"""
        self.course_map = {}
        if not CONTENT_DIR.exists(): return

        # 1. 遍历实际存在的目录
        for cat_dir in CONTENT_DIR.iterdir():
            if not cat_dir.is_dir() or cat_dir.name not in CATEGORY_MAP: continue

            for course_dir in cat_dir.iterdir():
                if not course_dir.is_dir(): continue

                # A. 注册文件夹英文名 (如 advanced-mathematicsB-u)
                self.course_map[course_dir.name.lower()] = course_dir

                # B. 读取 index.md 注册中文名 (如 高等数学(B))
                index_file = course_dir / "index.md"
                if index_file.exists():
                    title = self._extract_title(index_file)
                    if title:
                        self.course_map[title] = course_dir

        # 2. 注册 Config 中的手动别名 (如 "高数")
        for alias, target_keyword in COURSE_ALIAS_MAP.items():
            # 找到目标对应的真实路径
            target_path = self.find_course(target_keyword)
            if target_path:
                self.course_map[alias] = target_path

    def _extract_title(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("title:"):
                        return line.split(":", 1)[1].strip()
        except: pass
        return None

    def find_course(self, keyword):
        """查找课程路径"""
        # 1. 精确匹配 (Map Lookup)
        if keyword in self.course_map:
            return self.course_map[keyword]
        
        # 2. 包含匹配 (Substring)
        # 仅当 keyword 包含在 已知课程名 中时 (反之容易误判)
        for name, path in self.course_map.items():
            if name in keyword: # e.g. keyword="高数(B)期末", name="高数(B)"
                return path
        return None