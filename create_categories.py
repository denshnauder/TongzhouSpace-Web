#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建00-06的分类文件夹和相应的index.md文件
"""

import os
from pathlib import Path

# 配置
CONTENT_DIR = Path('content')

# 分类列表
CATEGORIES = {
    '00-general-compulsory': '00 - 通识必修',
    '01-general-elective': '01 - 通识选修',
    '02-public-basic': '02 - 公共基础',
    '03-prof-basic': '03 - 专业基础',
    '04-prof-compulsory': '04 - 专业必修',
    '05-prof-elective': '05 - 专业选修',
    '06-practical-training': '06 - 实践环节'
}


def create_category(cat_code, cat_name):
    """
    创建单个分类文件夹和index.md文件
    """
    cat_path = CONTENT_DIR / cat_code
    cat_path.mkdir(exist_ok=True)
    
    index_path = cat_path / 'index.md'
    if not index_path.exists():
        # 生成index.md内容
        content = f"---\ntitle: {cat_name}\n---\n\n"
        content += "## 目录列表 (Directories)\n\n"
        content += "| 内容 | 英文标识 |\n"
        content += "| :--- | :--- |\n"
        
        # 写入文件
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 创建成功: {cat_code}/index.md")
    else:
        print(f"⏭️  跳过: {cat_code}/index.md (已存在)")


def main():
    """
    主函数
    """
    print("🚀 开始创建分类文件夹...")
    print("=" * 50)
    
    # 确保content目录存在
    CONTENT_DIR.mkdir(exist_ok=True)
    
    # 创建每个分类
    for cat_code, cat_name in CATEGORIES.items():
        create_category(cat_code, cat_name)
    
    print("=" * 50)
    print("🎉 创建完成！")


if __name__ == "__main__":
    main()
