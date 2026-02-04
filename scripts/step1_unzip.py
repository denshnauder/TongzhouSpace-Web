#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【工具名称】：step1_unzip.py (解压文件并标记)
【使用方法】：
    python scripts/step1_unzip.py
【功能说明】：
    - 扫描content/目录中的.zip文件
    - 解压到同名文件夹
    - 在解压的文件夹中创建.empty_origin_archive文件作为标记
    - 删除原始zip文件
【示例】：
    # 解压所有zip文件
    python scripts/step1_unzip.py
"""

import os
import zipfile
from pathlib import Path

# 配置
CONTENT_DIR = Path('content')


def unzip_file(zip_path):
    """
    解压单个zip文件
    """
    try:
        # 获取zip文件名（不含扩展名）
        folder_name = zip_path.stem
        # 解压目标路径
        extract_path = zip_path.parent / folder_name
        
        # 创建目标文件夹
        extract_path.mkdir(exist_ok=True)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_path)
        
        # 创建标记文件
        marker_file = extract_path / '.origin_archive'
        marker_file.touch()
        
        # 删除原始zip文件
        zip_path.unlink()
        
        print(f"✅ 解压成功: {zip_path.name} -> {folder_name}/")
        return True
        
    except Exception as e:
        print(f"❌ 解压失败: {zip_path.name} - {str(e)}")
        return False


def main():
    """
    主函数
    """
    print("🚀 开始解压文件...")
    print("=" * 50)
    
    # 确保content目录存在
    CONTENT_DIR.mkdir(exist_ok=True)
    
    # 扫描所有zip文件
    zip_files = list(CONTENT_DIR.rglob('*.zip'))
    
    print(f"📦 发现 {len(zip_files)} 个zip文件")
    print()
    
    # 处理每个zip文件
    success_count = 0
    fail_count = 0
    
    for zip_path in zip_files:
        if unzip_file(zip_path):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 50)
    print("📊 解压统计:")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📁 总计: {success_count + fail_count}")
    print("=" * 50)
    print("🎉 解压完成！")


if __name__ == "__main__":
    main()
