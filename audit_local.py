import os
import json
import hashlib
import re
from pathlib import Path

# 配置
CONTENT_DIR = "content"
OUTPUT_FILE = "local_state.json"

# 疑似重复文件的特征正则
SUSPICIOUS_PATTERNS = [
    r"\(\d+\)",          # 例如: file(1).pdf
    r"副本",             # 例如: file - 副本.pdf
    r"copy",             # 例如: file - Copy.pdf
    r"conflicted",       # 同步冲突文件
    r"^\._",             # macOS 临时文件
    r"~$",               # 临时文件
]

def calculate_md5(filepath):
    """计算文件的 MD5 哈希值，用于确认识别重复内容"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def is_suspicious(filename):
    """判断文件名是否包含自动生成的副本特征"""
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False

def audit_resources(dir_path, files_in_dir):
    """
    核对 resources.json 与实际文件的对应关系
    返回: (缺失的文件列表, 未注册的幽灵文件列表)
    """
    json_path = os.path.join(dir_path, "resources.json")
    if not os.path.exists(json_path):
        return [], []

    missing_files = []
    registered_files = set()

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 兼容列表或字典结构，提取 'url'
            items = data if isinstance(data, list) else data.values()
            
            for item in items:
                if isinstance(item, dict) and 'url' in item:
                    url = item['url']
                    # 忽略远程链接
                    if url.startswith(('http://', 'https://', '//')):
                        continue
                    
                    # 记录注册的文件（标准化路径分隔符）
                    # 假设 url 是相对路径，直接指向文件名
                    registered_files.add(os.path.normpath(url))
                    
                    # 检查文件是否存在
                    file_abs_path = os.path.join(dir_path, url)
                    if not os.path.exists(file_abs_path):
                        missing_files.append(url)

    except json.JSONDecodeError:
        print(f"CRITICAL: {json_path} JSON 格式错误，跳过分析。")
        return ["JSON_ERROR"], []
    except Exception as e:
        print(f"ERROR: 分析 {json_path} 时出错: {e}")
        return [f"ERROR: {e}"], []

    # 找出幽灵文件 (在磁盘上但不在 json 里)
    # 排除 index.md, resources.json, .DS_Store 等系统/结构文件
    ghost_files = []
    ignored_files = {"index.md", "resources.json", ".DS_Store", ".gitignore"}
    
    for filename in files_in_dir:
        if filename in ignored_files:
            continue
        
        # 简单比对：如果文件名不在注册列表中，视为幽灵文件
        # 注意：这里假设 resources.json 里的 url 主要指向当前目录下的文件
        if os.path.normpath(filename) not in registered_files:
            ghost_files.append(filename)

    return missing_files, ghost_files

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"错误: 找不到目录 '{CONTENT_DIR}'。请确保脚本在项目根目录下运行。")
        return

    print(f"正在扫描 '{CONTENT_DIR}' ...")
    
    scan_results = {
        "files": [],
        "anomalies": []
    }

    for root, dirs, files in os.walk(CONTENT_DIR):
        # 1. 扫描当前目录下的所有文件
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # 计算相对路径，方便阅读
            rel_path = os.path.relpath(filepath, CONTENT_DIR)
            
            file_data = {
                "path": rel_path,
                "filename": filename,
                "size": os.path.getsize(filepath),
                "md5": calculate_md5(filepath),
                "suspicious": is_suspicious(filename)
            }
            scan_results["files"].append(file_data)

        # 2. 核对资源索引
        if "resources.json" in files:
            missing, ghosts = audit_resources(root, files)
            if missing or ghosts:
                rel_dir = os.path.relpath(root, CONTENT_DIR)
                scan_results["anomalies"].append({
                    "directory": rel_dir,
                    "missing_in_disk": missing,  # 有记录但没文件（死链）
                    "unregistered_ghosts": ghosts # 有文件但没记录（孤儿）
                })

    # 保存结果
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(scan_results, f, indent=2, ensure_ascii=False)

    print(f"扫描完成。")
    print(f"总文件数: {len(scan_results['files'])}")
    print(f"发现异常目录数: {len(scan_results['anomalies'])}")
    print(f"详细报告已生成至: {OUTPUT_FILE}")
    print("请检查该文件，然后发送给我进行下一步分析。")

if __name__ == "__main__":
    main()