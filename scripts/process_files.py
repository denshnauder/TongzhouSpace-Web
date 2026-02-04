#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process files in content directory:
1. Unzip zip files (< 100MB) into folders with the same name
2. Handle Chinese filename encoding issues
3. Filter junk files
4. Generate index.md files for unzipped folders
5. Skip large files (> 100MB) and call upload_to_oss placeholder
"""

import os
import zipfile
import shutil
from pathlib import Path

# Constants
MAX_SIZE_FOR_UNZIP = 100 * 1024 * 1024  # 100MB
JUNK_PATTERNS = ['__MACOSX', '.DS_Store', 'Thumbs.db', '.git']
CONTENT_DIR = Path('content')


def decode_path(path_bytes):
    """
    Fix Chinese filename encoding issue in zip files
    Try to decode using utf-8 first, then gbk, then cp437
    """
    if isinstance(path_bytes, str):
        return path_bytes
    
    try:
        return path_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return path_bytes.decode('gbk')
        except UnicodeDecodeError:
            return path_bytes.decode('cp437')


def is_junk_file(filename):
    """
    Check if a file is junk and should be filtered out
    """
    for pattern in JUNK_PATTERNS:
        if pattern in filename:
            return True
    return False


def upload_to_oss(file_path):
    """
    Placeholder function for uploading large files to OSS
    In a real implementation, this would upload to ModelScope or similar
    """
    print(f"[OSS Upload] Would upload large file: {file_path}")
    # TODO: Implement actual upload logic
    return f"https://oss.example.com/{file_path.name}"


def process_large_file(file_path):
    """
    Process large files (> 100MB)
    Call upload_to_oss and create a folder with index.md containing the link
    """
    folder_name = file_path.stem
    folder_path = file_path.parent / folder_name
    
    # Create folder if it doesn't exist
    folder_path.mkdir(exist_ok=True)
    
    # Upload to OSS (placeholder)
    download_link = upload_to_oss(file_path)
    
    # Generate index.md
    index_content = f"---\ntitle: {folder_name}\ntags: [大文件]\n---\n\n## {folder_name}\n\n[下载链接]({download_link})\n"
    (folder_path / 'index.md').write_text(index_content, encoding='utf-8')
    
    print(f"[Large File] Created folder with download link: {folder_path}")


def unzip_file(zip_path):
    """
    Unzip a zip file with proper encoding handling and junk filtering
    """
    folder_name = zip_path.stem
    extract_path = zip_path.parent / folder_name
    
    # Create extraction folder if it doesn't exist
    extract_path.mkdir(exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Process each file in the zip
            for file_info in zf.infolist():
                # Fix filename encoding
                original_name = file_info.filename
                decoded_name = decode_path(original_name)
                
                # Skip junk files
                if is_junk_file(decoded_name):
                    print(f"[Filtered] Skipping junk file: {decoded_name}")
                    continue
                
                # Skip directories
                if decoded_name.endswith('/') or decoded_name.endswith('\\'):
                    continue
                
                # Create full path for extracted file
                file_path = extract_path / decoded_name
                
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract file
                with zf.open(file_info) as source, open(file_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                print(f"[Extracted] {decoded_name} -> {file_path}")
        
        # Generate index.md for the unzipped folder
        index_content = f"---\ntitle: {folder_name}\ntags: [已解压]\n---\n\n## {folder_name}\n\n此文件夹包含从 {zip_path.name} 解压的内容。\n"
        (extract_path / 'index.md').write_text(index_content, encoding='utf-8')
        
        # Delete the original zip file
        zip_path.unlink()
        print(f"[Cleanup] Deleted original zip file: {zip_path}")
        
        return True
        
    except Exception as e:
        print(f"[Error] Failed to unzip {zip_path}: {e}")
        return False


def process_files():
    """
    Main function to process all files in content directory
    """
    print(f"[Start] Processing files in {CONTENT_DIR}")
    
    processed_count = 0
    zip_count = 0
    large_file_count = 0
    
    try:
        # Recursively scan all files
        for root, dirs, files in os.walk(CONTENT_DIR):
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                
                # Get file size
                try:
                    file_size = file_path.stat().st_size
                except Exception as e:
                    print(f"[Error] Failed to get file size for {file_path}: {e}")
                    continue
                
                processed_count += 1
                
                # Check if file is a zip
                if file.lower().endswith('.zip'):
                    zip_count += 1
                    print(f"[Found] Zip file: {file_path} ({file_size / 1024 / 1024:.2f}MB)")
                    
                    # Check file size
                    if file_size > MAX_SIZE_FOR_UNZIP:
                        print(f"[Large Zip] File exceeds 100MB, skipping unzip: {file_path}")
                        process_large_file(file_path)
                        large_file_count += 1
                    else:
                        print(f"[Processing] Unzipping: {file_path}")
                        unzip_file(file_path)
                
                # Check for other large files
                elif file_size > MAX_SIZE_FOR_UNZIP:
                    large_file_count += 1
                    print(f"[Found] Large file: {file_path} ({file_size / 1024 / 1024:.2f}MB)")
                    process_large_file(file_path)
        
        print("\n📊 统计信息:")
        print(f"✅ 处理文件总数: {processed_count}")
        print(f"✅ Zip文件数量: {zip_count}")
        print(f"✅ 大文件数量: {large_file_count}")
        print("[Finish] Processing complete")
    except Exception as e:
        print(f"[Error] Processing failed: {e}")


if __name__ == "__main__":
    process_files()
