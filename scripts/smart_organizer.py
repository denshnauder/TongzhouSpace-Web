#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【工具名称】：smart_organizer.py (交互式分类文件夹)
【使用方法】：
    python scripts/smart_organizer.py
【功能说明】：
    - 加载scripts/course_memory.json
    - 扫描content/目录中不在固定分类列表中的文件夹
    - 如果匹配内存中的记录，自动移动
    - 如果是新文件夹，询问用户分类和标准名称，并保存到内存
    - 实现合并逻辑：如果目标存在，移动项目到里面；如果文件冲突，重命名
【示例】：
    # 交互式分类文件夹
    python scripts/smart_organizer.py
"""

import os
import shutil
import json
import time
from pathlib import Path

# 配置
CONTENT_DIR = Path('content')
COURSE_MEMORY_FILE = Path('scripts') / 'course_memory.json'

# 固定分类列表
FIXED_CATEGORIES = {
    '00-general-compulsory': '通识必修',
    '01-general-elective': '通识选修',
    '02-public-basic': '公共基础',
    '03-prof-basic': '专业基础',
    '04-prof-compulsory': '专业必修',
    '05-prof-elective': '专业选修',
    '06-practical-training': '实践环节',
    '99-others': '其他/暂存'
}


def load_course_memory():
    """
    加载课程内存文件
    """
    if COURSE_MEMORY_FILE.exists():
        try:
            with open(COURSE_MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载内存文件失败: {str(e)}")
            return {}
    else:
        return {}


def save_course_memory(memory):
    """
    保存课程内存文件
    """
    try:
        COURSE_MEMORY_FILE.parent.mkdir(exist_ok=True)
        with open(COURSE_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存内存文件失败: {str(e)}")
        return False


def get_timestamp():
    """
    获取时间戳
    """
    return str(int(time.time()))


def merge_folders(source, target):
    """
    合并文件夹
    """
    try:
        # 确保目标文件夹存在
        target.mkdir(exist_ok=True)
        
        # 遍历源文件夹中的所有项目
        for item in source.iterdir():
            item_name = item.name
            target_item = target / item_name
            
            # 如果目标已存在
            if target_item.exists():
                # 生成新名称
                new_name = f"{item_name}_new_{get_timestamp()}"
                target_item = target / new_name
                print(f"⚠️  文件冲突，重命名为: {new_name}")
            
            # 移动项目
            if item.is_dir():
                shutil.move(str(item), str(target_item))
            else:
                shutil.copy2(str(item), str(target_item))
                item.unlink()
        
        # 删除空的源文件夹
        if not any(source.iterdir()):
            source.rmdir()
        
        return True
        
    except Exception as e:
        print(f"❌ 合并失败: {str(e)}")
        return False


def process_folder(folder_path, course_memory):
    """
    处理单个文件夹
    """
    folder_name = folder_path.name
    
    # 检查是否在内存中
    if folder_name in course_memory:
        # 自动移动
        memory_data = course_memory[folder_name]
        category = memory_data['category']
        standard_name = memory_data['standard_name']
        
        print(f"📝 内存匹配: {folder_name} -> {FIXED_CATEGORIES[category]}/{standard_name}")
        
        # 构建目标路径
        target_category = CONTENT_DIR / category
        target_folder = target_category / standard_name
        
        # 创建分类目录
        target_category.mkdir(exist_ok=True)
        
        # 执行移动或合并
        if target_folder.exists():
            print(f"🔄 目标已存在，执行合并...")
            if merge_folders(folder_path, target_folder):
                print(f"✅ 合并成功: {folder_name} -> {target_folder}")
            else:
                print(f"❌ 合并失败: {folder_name}")
        else:
            # 直接移动
            try:
                shutil.move(str(folder_path), str(target_folder))
                print(f"✅ 移动成功: {folder_name} -> {target_folder}")
            except Exception as e:
                print(f"❌ 移动失败: {folder_name} - {str(e)}")
        
    else:
        # 交互式分类
        print(f"\n📁 新文件夹: {folder_name}")
        print("请选择分类:")
        print()
        
        # 显示分类选项
        for i, (category_code, category_name) in enumerate(FIXED_CATEGORIES.items(), 1):
            print(f"{i}. {category_code} - {category_name}")
        print()
        
        # 获取用户选择
        while True:
            try:
                choice = int(input("请输入分类编号 (1-8): "))
                if 1 <= choice <= 8:
                    break
                else:
                    print("❌ 请输入1-8之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 获取选择的分类
        selected_category = list(FIXED_CATEGORIES.keys())[choice - 1]
        
        # 获取标准名称
        standard_name = input(f"请输入标准名称 (英文，用于文件夹名): ")
        if not standard_name:
            standard_name = folder_name.lower().replace(' ', '-').replace('_', '-')
        
        # 保存到内存
        course_memory[folder_name] = {
            'category': selected_category,
            'standard_name': standard_name,
            'timestamp': get_timestamp()
        }
        
        # 保存内存文件
        if save_course_memory(course_memory):
            print(f"✅ 已保存到内存: {folder_name} -> {standard_name}")
        else:
            print(f"❌ 保存到内存失败")
        
        # 构建目标路径
        target_category = CONTENT_DIR / selected_category
        target_folder = target_category / standard_name
        
        # 创建分类目录
        target_category.mkdir(exist_ok=True)
        
        # 执行移动
        try:
            shutil.move(str(folder_path), str(target_folder))
            print(f"✅ 移动成功: {folder_name} -> {target_folder}")
        except Exception as e:
            print(f"❌ 移动失败: {folder_name} - {str(e)}")
    
    print()


def main():
    """
    主函数
    """
    print("🚀 开始交互式分类...")
    print("=" * 50)
    
    # 确保目录存在
    CONTENT_DIR.mkdir(exist_ok=True)
    COURSE_MEMORY_FILE.parent.mkdir(exist_ok=True)
    
    # 加载课程内存
    course_memory = load_course_memory()
    print(f"📝 已加载 {len(course_memory)} 条内存记录")
    print()
    
    # 扫描所有文件夹
    folders_to_process = []
    
    for root, dirs, files in os.walk(CONTENT_DIR):
        # 跳过固定分类文件夹
        dirs[:] = [d for d in dirs if d not in FIXED_CATEGORIES.keys()]
        
        # 添加非固定分类的文件夹
        for dir_name in dirs:
            folder_path = Path(root) / dir_name
            folders_to_process.append(folder_path)
    
    print(f"📁 发现 {len(folders_to_process)} 个待分类文件夹")
    print()
    
    # 处理每个文件夹
    for folder_path in folders_to_process:
        process_folder(folder_path, course_memory)
        
        # 保存内存（每次处理后保存）
        save_course_memory(course_memory)
    
    print("=" * 50)
    print("📊 分类统计:")
    print(f"✅ 处理完成: {len(folders_to_process)} 个文件夹")
    print(f"📝 内存记录: {len(course_memory)} 条")
    print("=" * 50)
    print("🎉 分类完成！")


if __name__ == "__main__":
    main()
