#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【工具名称】：step3_restructure.py (物理排序文件)
【使用方法】：
    python scripts/step3_restructure.py
【功能说明】：
    - 遍历课程文件夹（二级目录）
    - 跳过带有.origin_archive标记的文件夹
    - 确保exams/和lectures/文件夹存在
    - 将包含"卷/exam/quiz/test"的文件移动到exams/
    - 其他文件移动到lectures/
【示例】：
    # 物理排序文件
    python scripts/step3_restructure.py
"""

import os
import shutil
from pathlib import Path
import re

# 配置
CONTENT_DIR = Path('content')

# 考试相关关键词
EXAM_KEYWORDS = ['卷', 'exam', 'quiz', 'test', '试题', '试卷', '考题', '考卷', 'test', 'exam', 'quiz', 'final', 'midterm']


def is_exam_file(filename):
    """
    判断是否为考试文件
    """
    filename_lower = filename.lower()
    for keyword in EXAM_KEYWORDS:
        if keyword in filename_lower:
            return True
    return False


def process_course_folder(course_folder):
    """
    处理单个课程文件夹
    """
    print(f"📁 处理课程文件夹: {course_folder}")
    
    # 检查是否有.origin_archive标记
    if (course_folder / '.origin_archive').exists():
        print(f"⏭️  跳过（有.origin_archive标记）")
        return False
    
    # 确保exams和lectures文件夹存在
    exams_folder = course_folder / 'exams'
    lectures_folder = course_folder / 'lectures'
    
    exams_folder.mkdir(exist_ok=True)
    lectures_folder.mkdir(exist_ok=True)
    
    # 遍历文件夹中的文件
    files_to_process = []
    for item in course_folder.iterdir():
        # 跳过目录和特殊文件
        if item.is_dir() or item.name.startswith('.') or item.name == 'index.md' or item.name == 'resources.json':
            continue
        files_to_process.append(item)
    
    print(f"📄 发现 {len(files_to_process)} 个文件")
    
    # 处理每个文件
    exam_count = 0
    lecture_count = 0
    
    for file_path in files_to_process:
        filename = file_path.name
        
        try:
            if is_exam_file(filename):
                # 移动到exams文件夹
                target_path = exams_folder / filename
                # 处理重名
                if target_path.exists():
                    # 生成新名称
                    base_name = target_path.stem
                    ext = target_path.suffix
                    counter = 1
                    while target_path.exists():
                        target_path = exams_folder / f"{base_name}_{counter}{ext}"
                        counter += 1
                
                shutil.move(str(file_path), str(target_path))
                exam_count += 1
                print(f"✅ 移动到exams: {filename}")
            else:
                # 移动到lectures文件夹
                target_path = lectures_folder / filename
                # 处理重名
                if target_path.exists():
                    # 生成新名称
                    base_name = target_path.stem
                    ext = target_path.suffix
                    counter = 1
                    while target_path.exists():
                        target_path = lectures_folder / f"{base_name}_{counter}{ext}"
                        counter += 1
                
                shutil.move(str(file_path), str(target_path))
                lecture_count += 1
                print(f"✅ 移动到lectures: {filename}")
        except Exception as e:
            print(f"❌ 移动失败: {filename} - {str(e)}")
    
    print(f"📊 处理结果: exams={exam_count}, lectures={lecture_count}")
    print()
    return True


def main():
    """
    主函数
    """
    print("🚀 开始物理排序文件...")
    print("=" * 50)
    
    # 确保content目录存在
    CONTENT_DIR.mkdir(exist_ok=True)
    
    # 遍历所有分类目录
    category_folders = []
    for item in CONTENT_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            category_folders.append(item)
    
    print(f"📁 发现 {len(category_folders)} 个分类目录")
    print()
    
    # 处理每个分类目录下的课程文件夹
    total_courses = 0
    processed_courses = 0
    
    for category_folder in category_folders:
        print(f"📂 处理分类: {category_folder.name}")
        
        # 遍历课程文件夹
        for course_folder in category_folder.iterdir():
            if course_folder.is_dir() and not course_folder.name.startswith('.'):
                total_courses += 1
                if process_course_folder(course_folder):
                    processed_courses += 1
        
        print()
    
    print("=" * 50)
    print("📊 排序统计:")
    print(f"✅ 处理课程: {processed_courses}")
    print(f"⏭️  跳过课程: {total_courses - processed_courses}")
    print(f"📁 总计: {total_courses}")
    print("=" * 50)
    print("🎉 排序完成！")


if __name__ == "__main__":
    main()
