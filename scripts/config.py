import os
from pathlib import Path

# ================= 基础路径 =================
BASE_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = BASE_DIR / "_inbox"
STAGING_DIR = BASE_DIR / "_staging"
CONTENT_DIR = BASE_DIR / "content"
PENDING_FILE = BASE_DIR / "pending.json"
RESOLVED_FILE = BASE_DIR / "resolved.json"

# ================= 业务常量 =================
# 00-06 分类映射
CATEGORY_MAP = {
    "00-general-compulsory": "00 - 通识必修",
    "01-general-elective": "01 - 通识选修",
    "02-public-basic": "02 - 公共基础",
    "03-prof-basic": "03 - 专业基础",
    "04-prof-compulsory": "04 - 专业必修",
    "05-prof-elective": "05 - 专业选修",
    "06-practical-training": "06 - 实践环节",
    "99-others": "99 - 其他资源"
}

# 资料类型映射 (ID -> 中文名)
FILE_TYPES = {
    "1": "教材", "2": "课件", "3": "笔记",
    "4": "作业", "5": "试卷", "6": "其他"
}

# 关键词映射 (用于自动猜测类型)
TYPE_KEYWORDS = {
    "5": ["试卷", "期末", "真题", "exam", "paper", "答案"],
    "2": ["课件", "ppt", "slide", "讲义"],
    "3": ["笔记", "重点", "note", "summary", "复习"],
    "4": ["作业", "习题", "homework", "assignment"],
    "1": ["教材", "书", "book", "textbook"]
}

# ================= 课程别名映射 (人工补丁) =================
# 仅当文件名使用简称，且无法直接匹配到课程全名时使用
# 格式: "简称": "content下的文件夹名" (或者部分路径)
COURSE_ALIAS_MAP = {
    "高数": "advanced-mathematicsB-u",
    "大物": "principles-of-mechanics",
    "马原": "modern-history",
    "线代": "linear-algebraB",
    "概统": "probability-and-statistics", 
    "模电": "analog-electronics",
    "数电": "digital-electronics"
}

# ================= 忽略规则 =================
IGNORE_PATTERNS = [
    r"^~\$", r"^\._", r"\.DS_Store", r"Thumbs\.db", 
    r"\.git", r"\.idea", r"__MACOSX", r"\.gitkeep"
]

# ================= 允许的扩展名 =================
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', 
    '.zip', '.rar', '.7z', '.md', '.txt',
    '.jpg', '.png', '.jpeg'
}