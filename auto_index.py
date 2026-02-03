"""
【工具名称】：auto_index.py (缺失索引自动补全工具)
【使用方法】：
    python auto_index.py [--content-dir CONTENT_DIR] [--verbose]
【功能说明】：
    - 递归扫描 content 目录下的所有子文件夹。
    - 发现没有 index.md 的文件夹时，自动创建一个基础的 index.md 文件。
    - 确保侧边栏和文件夹页面可以正常点击访问。
【注意事项】：
    - 生成的内容仅为占位标题，后续建议手动修改 index.md 增加详细描述。
"""

import os
import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(description='缺失索引自动补全工具')
    parser.add_argument('--content-dir', default='content', help='内容目录路径')
    parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    return parser.parse_args()

def fix_missing_indices(content_dir, verbose):
    if verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    created_count = 0
    
    try:
        for root, dirs, files in os.walk(content_dir):
            # 如果文件夹里没有 index.md
            if "index.md" not in files:
                folder_name = os.path.basename(root)
                # 跳过根目录 content 本身
                if root == content_dir:
                    continue
                
                index_path = os.path.join(root, "index.md")
                # 自动生成一个基础的 index.md
                try:
                    with open(index_path, "w", encoding="utf-8") as f:
                        f.write(f"---\ntitle: {folder_name}\n---\n\n# {folder_name}\n\n欢迎来到 {folder_name} 分类。")
                    if verbose:
                        logging.info(f"✨ 已自动补齐: {index_path}")
                    else:
                        print(f"✨ 已自动补齐: {index_path}")
                    created_count += 1
                except Exception as e:
                    if verbose:
                        logging.error(f"❌ 创建索引失败: {index_path}, 错误: {e}")
                    else:
                        print(f"❌ 创建索引失败: {index_path}, 错误: {e}")
        
        print(f"\n📊 统计信息:")
        print(f"✅ 成功创建 {created_count} 个索引文件")
        
    except Exception as e:
        if verbose:
            logging.error(f"❌ 执行失败: {e}")
        else:
            print(f"❌ 执行失败: {e}")

def main():
    args = parse_args()
    fix_missing_indices(args.content_dir, args.verbose)

if __name__ == "__main__":
    main()