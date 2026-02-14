import os
import hashlib
from pathlib import Path
from ..config import INBOX_DIR, GARBAGE_PATTERNS, ALLOWED_EXTENSIONS
import re

class Extractor:
    def __init__(self):
        self.inbox = INBOX_DIR

    def _calculate_md5(self, filepath):
        """计算文件指纹，用于后续去重"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def _is_garbage(self, filename):
        for p in GARBAGE_PATTERNS:
            if re.search(p, filename): return True
        return False

    def scan(self):
        """
        扫描 Inbox，提取元数据。
        逻辑：
        1. 如果文件在 _inbox/张三/a.pdf -> contributor = "张三"
        2. 如果文件在 _inbox/a.pdf      -> contributor = "Anonymous"
        """
        raw_items = []
        
        if not self.inbox.exists():
            print(f"❌ Inbox 不存在: {self.inbox}")
            return []

        print(f"🔍 正在扫描 Inbox...")

        for root, dirs, files in os.walk(self.inbox):
            for filename in files:
                if self._is_garbage(filename):
                    continue
                
                file_path = Path(root) / filename
                
                # 检查后缀名
                if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                    print(f"⚠️ 跳过不支持的文件类型: {filename}")
                    continue

                # === 核心逻辑：文件夹即署名 ===
                # 计算相对路径：例如 "张三/马原/test.pdf" 或 "test.pdf"
                rel_path = file_path.relative_to(self.inbox)
                parts = rel_path.parts
                
                if len(parts) > 1:
                    # 只要是在子文件夹里，第一级目录名就是贡献者
                    contributor = parts[0]
                else:
                    # 在根目录下，归为匿名
                    contributor = "Anonymous"

                raw_items.append({
                    "source_path": file_path,
                    "filename": filename,
                    "contributor": contributor,
                    "md5": self._calculate_md5(file_path),
                    "size": os.path.getsize(file_path)
                })

        print(f"✅ 提取完成: 发现 {len(raw_items)} 个有效文件")
        return raw_items

if __name__ == "__main__":
    # 测试代码
    e = Extractor()
    items = e.scan()
    for i in items:
        print(f"  - [{i['contributor']}] {i['filename']}")