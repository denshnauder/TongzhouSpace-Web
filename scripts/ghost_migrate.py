#!/usr/bin/env python3
"""
【工具名称】：ghost_migrate.py (幽灵文件迁移工具)
【使用方法】：
    python scripts/ghost_migrate.py [--dry-run]
【功能说明】：
    - 递归扫描 content 目录下的所有文件
    - 识别并处理指定的二进制文件（PDF、PPT、Word、图片、视频等）
    - 将文件上传到 ModelScope
    - 创建对应的幽灵 .md 文件，包含下载链接
    - 删除原始本地二进制文件以释放空间
【参数说明】：
    --dry-run                 - 模拟运行，只打印操作而不执行
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from modelscope.hub.api import HubApi
from urllib.parse import quote
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 文件类型映射
extension_to_type = {
    # Engineering & Code
    '.m': 'Matlab Code',
    '.mat': 'Matlab Data',
    '.py': 'Python Code',
    '.ipynb': 'Jupyter Notebook',
    '.cpp': 'C++ Code',
    '.c': 'C Code',
    '.h': 'C/C++ Header',
    '.java': 'Java Code',
    '.jar': 'Java Archive',
    
    # Documents & Data
    '.pdf': 'PDF Document',
    '.ppt': 'PowerPoint Presentation',
    '.pptx': 'PowerPoint Presentation',
    '.doc': 'Word Document',
    '.docx': 'Word Document',
    '.xls': 'Excel Spreadsheet',
    '.xlsx': 'Excel Spreadsheet',
    
    # Media
    '.jpg': 'Image',
    '.jpeg': 'Image',
    '.png': 'Image',
    '.mp4': 'Video',
    '.mov': 'Video',
    '.mp3': 'Audio'
}

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='幽灵文件迁移工具')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，只打印操作而不执行')
    return parser.parse_args()

def upload_and_get_url(file_path, api, repo_id):
    """
    上传文件到 ModelScope 并返回可下载的 URL
    """
    try:
        # 构建相对路径（使用正斜杠）
        # 从 content/ 开始构建相对路径
        relative_path = os.path.relpath(file_path, 'content').replace('\\', '/')
        
        # 上传文件到 ModelScope
        api.upload_file(
            repo_id=repo_id,
            path_or_fileobj=file_path,
            path_in_repo=relative_path,
            revision='master'
        )
        
        # 构建可下载的 URL，确保路径被正确编码
        encoded_path = quote(relative_path)
        url = f"https://modelscope.cn/api/v1/models/{repo_id}/repo?Revision=master&FilePath={encoded_path}"
        
        return url
        
    except Exception as e:
        logging.error(f"上传文件 {file_path} 失败: {e}")
        return None

def main():
    """主函数"""
    args = parse_args()
    
    # 加载 .env 文件
    load_dotenv()
    
    # 获取配置
    MODELSCOPE_TOKEN = os.getenv('MODELSCOPE_TOKEN')
    MODELSCOPE_REPO_ID = os.getenv('MODELSCOPE_REPO_ID')
    
    # 检查配置是否存在
    if not MODELSCOPE_TOKEN:
        logging.error("错误：未设置 MODELSCOPE_TOKEN 环境变量")
        sys.exit(1)
    
    if not MODELSCOPE_REPO_ID:
        logging.error("错误：未设置 MODELSCOPE_REPO_ID 环境变量")
        sys.exit(1)
    
    # 初始化 HubApi 并登录
    try:
        api = HubApi()
        api.login(MODELSCOPE_TOKEN)
        logging.info("成功登录 ModelScope")
    except Exception as e:
        logging.error(f"登录 ModelScope 失败: {e}")
        sys.exit(1)
    
    # 目标文件扩展名
    target_extensions = {
        # Engineering & Code
        '.m', '.mat', '.py', '.cpp', '.c', '.h', '.java', '.jar', '.ipynb',
        
        # Documents & Data
        '.pdf', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx',
        
        # Media
        '.jpg', '.jpeg', '.png', '.mp4', '.mov', '.mp3'
    }
    
    # 排除的文件扩展名和文件名
    excluded_extensions = {'.md', '.zip', '.rar', '.7z'}
    excluded_filenames = {'.DS_Store'}
    
    # 收集所有目标文件
    target_files = []
    content_dir = 'content'
    
    if not os.path.exists(content_dir):
        logging.error(f"目录 {content_dir} 不存在")
        sys.exit(1)
    
    # 递归遍历 content 目录，收集目标文件
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            # 跳过系统文件
            if file in excluded_filenames or file.startswith('.git'):
                continue
            
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            # 检查是否为目标文件且不在排除列表中
            if ext in target_extensions and ext not in excluded_extensions:
                target_files.append(file_path)
    
    # 打印统计信息
    logging.info(f"找到 {len(target_files)} 个目标文件")
    
    # 处理目标文件
    success_count = 0
    failure_count = 0
    
    with tqdm(total=len(target_files), desc="迁移进度") as pbar:
        for file_path in target_files:
            filename = os.path.basename(file_path)
            ghost_file = file_path + '.md'
            
            # 检查幽灵文件是否已存在（支持断点续传）
            if os.path.exists(ghost_file):
                logging.info(f"跳过 {filename}，幽灵文件已存在")
                pbar.update(1)
                continue
            
            print(f"Processing: {filename}...")
            
            if args.dry_run:
                # 模拟运行，只打印操作
                logging.info(f"模拟操作: 上传 {filename} -> 创建 {ghost_file} -> 删除 {filename}")
                pbar.update(1)
                continue
            
            try:
                # 上传文件到 ModelScope
                url = upload_and_get_url(file_path, api, MODELSCOPE_REPO_ID)
                
                # 安全检查：确保 URL 有效
                if url and url.startswith('http'):
                    # 确定文件类型
                    ext = os.path.splitext(file_path)[1].lower()
                    file_type = extension_to_type.get(ext, '文件')
                    
                    # 创建幽灵文件
                    with open(ghost_file, 'w', encoding='utf-8') as f:
                        f.write(f"---\ntitle: {filename}\ntags: [云端资源]\n---\n[💾 点击下载 {filename}]({url})\n")
                    
                    # 删除原始文件
                    os.remove(file_path)
                    
                    success_count += 1
                    print(f"[SUCCESS] Uploaded & Ghosted: {filename}")
                    
                else:
                    failure_count += 1
                    print(f"[ERROR] Upload failed for {filename}. Keeping local file.")
                    
            except Exception as e:
                failure_count += 1
                logging.error(f"处理 {filename} 时出错: {e}")
                print(f"[ERROR] Upload failed for {filename}. Keeping local file.")
            
            pbar.update(1)
    
    # 打印最终统计信息
    logging.info(f"\n📊 迁移完成！")
    logging.info(f"✅ 成功: {success_count} 个文件")
    logging.info(f"❌ 失败: {failure_count} 个文件")

if __name__ == "__main__":
    main()
