#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【工具名称】：smart_migrate.py (智能迁移工具)
【使用方法】：
    python scripts/smart_migrate.py
【功能说明】：
    - 将内容从时间基文件夹迁移到分类基文件夹
    - 使用英文名称和适当的标签
    - 基于课程映射字典自动分类内容
【注意事项】：
    - 需要安装 pypinyin 包：pip install pypinyin
【示例】：
    # 运行智能迁移
    python scripts/smart_migrate.py
"""

import os
import shutil
import re
from pypinyin import pinyin, Style

# Configuration
CONTENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'content')
TARGET_FOLDERS = [
    '00-general-compulsory',
    '01-general-elective',
    '02-public-basic',
    '03-prof-basic',
    '04-prof-compulsory',
    '05-prof-elective',
    '06-practical',
    '99-unsorted'
]

# Course mapping dictionary
COURSE_MAP = {
    # 00-general-compulsory
    "毛概": ("00-general-compulsory", "mao-zedong-thought"),
    "马原": ("00-general-compulsory", "marxist-principles"),
    "思修": ("00-general-compulsory", "ethics-law"),
    "近代史": ("00-general-compulsory", "modern-history"),
    "军理": ("00-general-compulsory", "military-theory"),
    "体育": ("00-general-compulsory", "pe"),
    
    # 02-public-basic
    "高数": ("02-public-basic", "calculus"),
    "高等数学": ("02-public-basic", "calculus"),
    "线代": ("02-public-basic", "linear-algebra"),
    "线性代数": ("02-public-basic", "linear-algebra"),
    "大物": ("02-public-basic", "physics"),
    "大学物理": ("02-public-basic", "physics"),
    "英语": ("02-public-basic", "english"),
    "C语言": ("02-public-basic", "c-programming"),
    "Python": ("02-public-basic", "python"),
    "概率": ("02-public-basic", "probability-statistics"),

    # 03-prof-basic (专业基础 - 工科硬菜)
    "工图": ("03-prof-basic", "engineering-drawing"),
    "工程制图": ("03-prof-basic", "engineering-drawing"),
    "理力": ("03-prof-basic", "theoretical-mechanics"),
    "理论力学": ("03-prof-basic", "theoretical-mechanics"),
    "材力": ("03-prof-basic", "mechanics-materials"),
    "材料力学": ("03-prof-basic", "mechanics-materials"),
    "流体": ("03-prof-basic", "fluid-mechanics"),
    "热力学": ("03-prof-basic", "thermodynamics"),
    "电工": ("03-prof-basic", "electrical-engineering"),
    "电子": ("03-prof-basic", "electronics"),
    "机械原理": ("03-prof-basic", "mech-principles"),
    "机械设计": ("03-prof-basic", "mech-design"),

    # 04-prof-compulsory (车辆核心)
    "汽车构造": ("04-prof-compulsory", "auto-structure"),
    "汽车理论": ("04-prof-compulsory", "auto-theory"),
    "发动机": ("04-prof-compulsory", "engine-principle"),
    "汽车设计": ("04-prof-compulsory", "auto-design"),
    "制造工艺": ("04-prof-compulsory", "manufacturing-tech"),

    # 05-prof-elective (选修)
    "单片机": ("05-prof-elective", "microcontroller"),
    "新能源": ("05-prof-elective", "new-energy"),
    "自动驾驶": ("05-prof-elective", "autonomous-driving"),
    "智能": ("05-prof-elective", "intelligent-vehicle"),
    "振动": ("05-prof-elective", "vibration-noise"),
    "Matlab": ("05-prof-elective", "matlab-skills"),

    # 06-practical
    "金工": ("06-practical", "metalworking-internship"),
    "实习": ("06-practical", "internship"),
    "毕设": ("06-practical", "graduation-project"),
    "课程设计": ("06-practical", "course-design"),
}

def to_kebab_case(text):
    """Convert Chinese text to kebab-case"""
    if not text:
        return ""
    
    # Check if text is in COURSE_MAP values
    for course, (_, english_name) in COURSE_MAP.items():
        if course in text:
            return english_name
    
    # Use pypinyin to convert Chinese to pinyin
    pinyin_list = pinyin(text, style=Style.NORMAL)
    pinyin_str = '-'.join([item[0].lower() for item in pinyin_list])
    
    # Clean up
    pinyin_str = re.sub(r'[^a-z0-9-]', '-', pinyin_str)
    pinyin_str = re.sub(r'-+', '-', pinyin_str)
    pinyin_str = pinyin_str.strip('-')
    
    return pinyin_str or "unknown"

def create_category_indexes():
    """Create index.md files for each category folder"""
    for folder in TARGET_FOLDERS:
        folder_path = os.path.join(CONTENT_DIR, folder)
        index_path = os.path.join(folder_path, 'index.md')
        
        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
        
        # Create index.md if it doesn't exist
        if not os.path.exists(index_path):
            # Convert folder name to readable title
            title = folder.replace('-', ' ').title()
            # Special case for numbered folders
            title = title.replace('00 ', '').replace('01 ', '').replace('02 ', '').replace('03 ', '').replace('04 ', '').replace('05 ', '').replace('06 ', '').replace('99 ', '')
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(f"---\ntitle: \"{title}\"\n---\n")
            print(f"Created index.md for {folder}")

def process_folder(source_path, original_name, parent_folder):
    """Process a single folder"""
    # Check if folder name is in course map
    matched = False
    target_folder = None
    new_name = None
    
    for course_key, (target, english_name) in COURSE_MAP.items():
        if course_key in original_name:
            target_folder = target
            new_name = english_name
            matched = True
            break
    
    if not matched:
        # Move to unsorted
        target_folder = '99-unsorted'
        new_name = to_kebab_case(original_name)
        print(f"Unmatched folder {original_name}, moving to {target_folder}/{new_name}")
    else:
        print(f"Matched folder {original_name}, moving to {target_folder}/{new_name}")
    
    # Create target directory
    target_path = os.path.join(CONTENT_DIR, target_folder, new_name)
    os.makedirs(os.path.join(CONTENT_DIR, target_folder), exist_ok=True)
    
    # Handle existing target folder
    counter = 1
    original_target_path = target_path
    while os.path.exists(target_path):
        target_path = f"{original_target_path}-{counter}"
        counter += 1
    
    # Move the folder
    try:
        shutil.move(source_path, target_path)
        print(f"Moved {source_path} to {target_path}")
        
        # Update or create index.md
        index_path = os.path.join(target_path, 'index.md')
        if os.path.exists(index_path):
            # Update existing index.md
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add tag for original path if not present
            if f"#{parent_folder}" not in content:
                # Check if frontmatter exists
                if content.startswith('---'):
                    # Find end of frontmatter
                    frontmatter_end = content.find('---', 3)
                    if frontmatter_end != -1:
                        # Add tag after frontmatter
                        new_content = content[:frontmatter_end + 3] + f"\n\n#{parent_folder}\n" + content[frontmatter_end + 3:]
                    else:
                        # No frontmatter end, add to beginning
                        new_content = content + f"\n\n#{parent_folder}"
                else:
                    # No frontmatter, add to beginning
                    new_content = f"---\ntitle: \"{original_name}\"\n---\n\n#{parent_folder}\n" + content
                
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated index.md with tag #{parent_folder}")
        else:
            # Create new index.md
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(f"---\ntitle: \"{original_name}\"\n---\n\n#{parent_folder}\n")
            print(f"Created index.md with title {original_name} and tag #{parent_folder}")
            
    except Exception as e:
        print(f"Error processing {source_path}: {e}")

def main():
    """Main function"""
    print("Starting smart migrate script...")
    print(f"Content directory: {CONTENT_DIR}")
    
    # Create category indexes
    create_category_indexes()
    
    # Iterate through all folders in content
    for item in os.listdir(CONTENT_DIR):
        item_path = os.path.join(CONTENT_DIR, item)
        
        # Skip target folders and files
        if not os.path.isdir(item_path) or item in TARGET_FOLDERS:
            continue
        
        # This is a source folder (e.g., "大二上")
        parent_folder = item
        print(f"\nProcessing parent folder: {parent_folder}")
        
        # Iterate through subfolders (e.g., "汽车理论")
        for subitem in os.listdir(item_path):
            subitem_path = os.path.join(item_path, subitem)
            
            if os.path.isdir(subitem_path):
                process_folder(subitem_path, subitem, parent_folder)
        
        # Check if parent folder is empty after processing
        try:
            if not os.listdir(item_path):
                os.rmdir(item_path)
                print(f"Removed empty parent folder: {parent_folder}")
        except Exception as e:
            print(f"Error removing parent folder {parent_folder}: {e}")
    
    print("\nMigration completed!")
    print("\nNext steps:")
    print("1. Check 99-unsorted folder for files that need manual categorization")
    print("2. Verify all files were moved correctly")
    print("3. Run 'npx quartz build' to rebuild the site")

if __name__ == "__main__":
    # Check if pypinyin is installed
    try:
        import pypinyin
    except ImportError:
        print("Error: pypinyin is not installed. Please run 'pip install pypinyin' first.")
        exit(1)
    
    main()
