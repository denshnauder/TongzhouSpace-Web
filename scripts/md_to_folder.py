"""
【工具名称】：md_to_folder.py (Markdown 文件转文件夹模式工具)
【使用方法】：
    python md_to_folder.py [--content-dir CONTENT_DIR] [--verbose]
【功能说明】：
    - 扫描 content 目录下所有落单的 .md 文件。
    - 为每个文件创建同名文件夹，并将文件重命名为 index.md 移入其中。
    - 它是解决 Quartz 404 错误（因为路径不匹配）的最快方案。
【注意事项】：
    - 会直接移动文件。运行前请确保 content 目录下没有与文件名同名的文件夹。
"""

import os
import shutil
import argparse
import logging
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Markdown 文件转文件夹模式工具')
    parser.add_argument('--content-dir', default='content', help='内容目录路径')
    parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    return parser.parse_args()

def convert_md_to_folder_notes(content_dir, verbose):
    if verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    converted_count = 0
    skipped_count = 0
    content_path = Path(content_dir)
    
    try:
        for item in os.listdir(content_dir):
            item_path = content_path / item
            
            # 只要是 .md 文件，且不是 index.md 和 README.md
            if item_path.is_file() and item.endswith(".md") and item not in ["index.md", "README.md"]:
                file_name = item[:-3]  # 去掉 .md
                new_folder_path = content_path / file_name
                
                # 检查文件夹是否已存在
                if new_folder_path.exists():
                    if verbose:
                        logging.warning(f"⚠️  跳过: 文件夹已存在 - {new_folder_path}")
                    else:
                        print(f"⚠️  跳过: 文件夹已存在 - {new_folder_path}")
                    skipped_count += 1
                    continue
                
                try:
                    # 1. 创建文件夹
                    new_folder_path.mkdir(parents=True, exist_ok=True)
                    
                    # 2. 移动并重命名为 index.md
                    target_path = new_folder_path / "index.md"
                    shutil.move(str(item_path), str(target_path))
                    
                    if verbose:
                        logging.info(f"✅ 已转换: {item} -> {file_name}/index.md")
                    else:
                        print(f"✅ 已转换: {item} -> {file_name}/index.md")
                    converted_count += 1
                    
                except Exception as e:
                    if verbose:
                        logging.error(f"❌ 转换失败: {item}, 错误: {e}")
                    else:
                        print(f"❌ 转换失败: {item}, 错误: {e}")
                    skipped_count += 1
        
        print(f"\n📊 统计信息:")
        print(f"✅ 成功转换 {converted_count} 个文件")
        print(f"⚠️  跳过 {skipped_count} 个文件")
        
    except Exception as e:
        if verbose:
            logging.error(f"❌ 执行失败: {e}")
        else:
            print(f"❌ 执行失败: {e}")

def main():
    args = parse_args()
    convert_md_to_folder_notes(args.content_dir, args.verbose)

if __name__ == "__main__":
    main()