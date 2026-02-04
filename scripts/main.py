#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for TongzhouSpace content management

This script integrates all content management functions:
1. Smart migration (smart_migrate.py)
2. File processing (process_files.py)
3. Index generation (auto_index.py)
4. MD to folder conversion (md_to_folder.py)
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
    from auto_index import fix_missing_indices as auto_index_main
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
        auto_index_main(content_dir, verbose)
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
        auto_index_main(args.content_dir, args.verbose)
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
