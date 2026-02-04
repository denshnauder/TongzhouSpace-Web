#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【工具名称】：main.py (统一工具管理脚本)
【使用方法】：
    python scripts/main.py [命令] [参数]
【功能说明】：
    统一管理所有内容管理工具，提供一致的命令行接口
【可用命令】：
    migrate     - 智能迁移内容到分类结构
    process     - 处理文件（解压、大文件处理）
    index       - 生成缺失的 index.md 文件
    folderize   - 将 MD 文件转换为文件夹结构
    all         - 按顺序运行所有命令
【示例】：
    # 查看帮助
    python scripts/main.py --help
    
    # 智能迁移内容
    python scripts/main.py migrate
    
    # 处理文件
    python scripts/main.py process
    
    # 生成索引
    python scripts/main.py index
    
    # 转换 MD 文件
    python scripts/main.py folderize
    
    # 运行所有命令
    python scripts/main.py all
"""

import os
import sys
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import functions from other scripts
try:
    from smart_migrate import main as smart_migrate_main
    from process_files import process_files as process_files_main
    from generate_index import generate_index as auto_index_main
    from md_to_folder import convert_md_to_folder_notes as md_to_folder_main
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all script files are in the scripts directory")
    sys.exit(1)

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='TongzhouSpace Content Management Tool')
    parser.add_argument('--content-dir', default='content', help='Content directory path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Smart migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate content to category-based structure')
    
    # Process files command
    process_parser = subparsers.add_parser('process', help='Process files (unzip, handle large files)')
    
    # Auto index command
    index_parser = subparsers.add_parser('index', help='Generate missing index.md files')
    
    # MD to folder command
    folder_parser = subparsers.add_parser('folderize', help='Convert MD files to folder structure')
    
    # All-in-one command
    all_parser = subparsers.add_parser('all', help='Run all commands in sequence')
    
    return parser.parse_args()

def run_all_commands(content_dir, verbose):
    """
    Run all commands in sequence
    """
    print("=" * 80)
    print("Running all content management commands...")
    print("=" * 80)
    
    print("\n1. Migrating content to category-based structure...")
    print("-" * 60)
    try:
        smart_migrate_main()
    except Exception as e:
        print(f"Error running migrate: {e}")
    
    print("\n2. Processing files (unzipping, handling large files)...")
    print("-" * 60)
    try:
        process_files_main()
    except Exception as e:
        print(f"Error running process: {e}")
    
    print("\n3. Generating missing index.md files...")
    print("-" * 60)
    try:
        auto_index_main()
    except Exception as e:
        print(f"Error running index: {e}")
    
    print("\n4. Converting MD files to folder structure...")
    print("-" * 60)
    try:
        md_to_folder_main(content_dir, verbose)
    except Exception as e:
        print(f"Error running folderize: {e}")
    
    print("\n" + "=" * 80)
    print("All commands completed!")
    print("=" * 80)

def main():
    """
    Main function
    """
    args = parse_args()
    
    if not args.command:
        print("Error: No command specified")
        print("Use --help to see available commands")
        sys.exit(1)
    
    if args.command == 'migrate':
        print("Running smart migration...")
        smart_migrate_main()
    elif args.command == 'process':
        print("Processing files...")
        process_files_main()
    elif args.command == 'index':
        print("Generating missing index.md files...")
        auto_index_main()
    elif args.command == 'folderize':
        print("Converting MD files to folder structure...")
        md_to_folder_main(args.content_dir, args.verbose)
    elif args.command == 'all':
        run_all_commands(args.content_dir, args.verbose)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
