import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 添加 scripts 到路径，确保能 import
sys.path.append(str(Path(__file__).resolve().parent))

from scripts.core.processor import Processor
from scripts.core.uploader import Uploader

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py [process | upload]")
        return

    cmd = sys.argv[1]

    if cmd == "process":
        # 公开步骤：无需 Token
        p = Processor()
        p.run()
    
    elif cmd == "upload":
        # 私有步骤：需要 Token
        load_dotenv()
        token = os.getenv('MODELSCOPE_TOKEN')
        repo_id = os.getenv('MODELSCOPE_REPO_ID')
        if not token:
            print("❌ 错误: 未找到 MODELSCOPE_TOKEN")
            return
        
        u = Uploader(token, repo_id)
        u.run()
        
        # 自动 Git Push (可选)
        print("☁️  正在推送到 GitHub...")
        os.system("git add content/")
        os.system("git commit -m 'Auto-update resources'")
        os.system("git push")

    else:
        print("未知命令。")

if __name__ == "__main__":
    main()