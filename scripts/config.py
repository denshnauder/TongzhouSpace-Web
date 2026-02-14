import os
from pathlib import Path

# ================= 基础路径 =================
# 假设脚本位于 /scripts 目录，向上两级是根目录
BASE_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = BASE_DIR / "_inbox"
CONTENT_DIR = BASE_DIR / "content"
MEMORY_FILE = BASE_DIR / "scripts/memory.json"
PENDING_FILE = BASE_DIR / "pending.json"
RESOLVED_FILE = BASE_DIR / "resolved.json"

# ================= 文件类型映射 =================
TYPE_ID_NAME = {
    "1": "教材", "2": "课件", "3": "笔记", 
    "4": "作业", "5": "试卷", "6": "其他"
}

# ================= 忽略规则 =================
IGNORE_FILES = ['.DS_Store', 'Thumbs.db', '.gitignore', '.gitkeep', '__MACOSX']

# ================= 允许的扩展名 =================
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', 
    '.zip', '.rar', '.7z', '.md', '.txt',
    '.jpg', '.png', '.jpeg'
}