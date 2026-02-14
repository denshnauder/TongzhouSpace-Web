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

DIR_DISPLAY_MAP = {
    # 00 - 通识必修
    "modern-history": "中国近现代史纲要",  # 修正：原为临时英文名
    "situation-and-policy": "形势与政策",

    # 02 - 公共基础
    "advanced-mathematicsb-u": "高等数学B（上）",  # 保留官方命名格式
    "complex-functions-and-integral-transforms": "复变函数与积分变换",
    "general-chemistry": "普通化学",
    "linear-algebrab": "线性代数B",
    "probability-theory-and-mathematical-statistics":"概率论与数理统计",

    # 03 - 专业基础
    "electromagnetic-fields": "电磁场",  # 修正：原为临时英文名
    "engineering-materials": "工程材料",
    "engineering-mechanics": "工程力学",
    "engineering-thermodynamics": "工程热力学",
    "equations-of-mathematical-physics": "数理方程",
    "groundwater-dynamics": "地下水动力学",
    "principles-of-mechanics": "机械原理",
    "surveying": "测量学",
    "theoretical-mechanicsc": "理论力学C",  # 保留官方命名格式

    # 04 - 专业必修
    "auto-structure": "汽车构造",
    "auto-theory": "汽车理论",
    "elastic-mechanics": "弹性力学",
    "real-estate-development-and-management": "房地产开发与管理",
    "signal-and-system": "信号与系统",

    # 05 - 专业选修
    "real-estate-valuation": "房地产估价",

    # 99 - 其他资源
    "traffic-engineering": "交通工程学"
}

# 这里的分类映射也建议确认一次，确保父级目录显示正确
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