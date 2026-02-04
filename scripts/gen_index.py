#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【工具名称】：gen_index.py (生成index.md文件)
【使用方法】：
    python scripts/gen_index.py
【功能说明】：
    - 递归遍历content/目录，为每个子文件夹生成index.md
    - 跳过根目录content/index.md（手动维护）
    - 模式A：节点页（无resources.json）- 列出子文件夹
    - 模式B：叶子页（有resources.json）- 列出文件下载链接
    - 实现命名映射：英文文件夹名 -> 中文显示名
【示例】：
    # 生成index.md文件
    python scripts/gen_index.py
"""

import os
import json
from pathlib import Path

# 配置
CONTENT_DIR = Path('content')
COURSE_MEMORY_FILE = Path('scripts') / 'course_memory.json'

# 一级目录映射
CATEGORY_MAP = {
    '00-general-compulsory': '00 - 通识必修',
    '01-general-elective': '01 - 通识选修',
    '02-public-basic': '02 - 公共基础',
    '03-prof-basic': '03 - 专业基础',
    '04-prof-compulsory': '04 - 专业必修',
    '05-prof-elective': '05 - 专业选修',
    '06-practical-training': '06 - 实践环节',
    '99-others': '99 - 其他资源'
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
            print(f"❌ 加载课程内存失败: {str(e)}")
            return {}
    else:
        return {}


def get_display_name(folder_name):
    """
    获取文件夹的显示名称（中文）
    """
    # 检查一级目录映射
    if folder_name in CATEGORY_MAP:
        return CATEGORY_MAP[folder_name]
    
    # 检查课程内存映射（反向查找）
    course_memory = load_course_memory()
    for course_name, memory_data in course_memory.items():
        if memory_data.get('standard_name') == folder_name:
            return course_name
    
    # Fallback：返回英文原名
    return folder_name


def generate_node_page(folder_path, folder_name):
    """
    生成节点页（列出子文件夹）
    """
    # 获取显示名称
    display_name = get_display_name(folder_name)
    
    # 收集子文件夹
    subfolders = []
    for item in folder_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            subfolders.append(item)
    
    # 按名称排序
    subfolders.sort(key=lambda x: x.name)
    
    # 生成Markdown内容
    content = f"---\ntitle: {display_name}\n---\n\n"
    content += "## 📂 目录列表 (Directories)\n\n"
    content += "| 内容 | 英文标识 |\n"
    content += "| :--- | :--- |\n"
    
    for subfolder in subfolders:
        subfolder_name = subfolder.name
        subfolder_display = get_display_name(subfolder_name)
        content += f"| **[[{subfolder_name}/index|📁 {subfolder_display}]]** | `{subfolder_name}` |\n"
    
    return content


def generate_leaf_page(folder_path, folder_name):
    """
    生成叶子页（列出文件下载链接）
    """
    # 获取显示名称
    display_name = get_display_name(folder_name)
    
    # 读取resources.json
    resources_file = folder_path / 'resources.json'
    if not resources_file.exists():
        return None
    
    try:
        with open(resources_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        files = data.get('files', [])
    except Exception as e:
        print(f"❌ 读取resources.json失败: {str(e)}")
        files = []
    
    # 获取父文件夹名称（用于标签）
    parent_folder = folder_path.parent.name
    
    # 生成Markdown内容
    content = f"---\ntitle: {display_name}\ntags: [{parent_folder}]\n---\n\n"
    content += "## 💾 资源列表 (Files)\n\n"
    content += "| 文件名 | 大小 | 下载直链 |\n"
    content += "| :--- | :--- | :--- |\n"
    
    for file_info in files:
        name = file_info.get('name', '')
        url = file_info.get('url', '')
        size = file_info.get('size', '')
        content += f"| **{name}** | {size} | [☁️ 点击下载]({url}) |\n"
    
    return content


def generate_index(folder_path):
    """
    生成单个文件夹的index.md
    """
    folder_name = folder_path.name
    index_file = folder_path / 'index.md'
    
    # 检查是否有resources.json
    has_resources = (folder_path / 'resources.json').exists()
    
    if has_resources:
        # 生成叶子页
        content = generate_leaf_page(folder_path, folder_name)
        if content:
            try:
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 生成叶子页: {folder_path}")
                return True
            except Exception as e:
                print(f"❌ 生成叶子页失败: {folder_path} - {str(e)}")
                return False
    else:
        # 生成节点页
        content = generate_node_page(folder_path, folder_name)
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 生成节点页: {folder_path}")
            return True
        except Exception as e:
            print(f"❌ 生成节点页失败: {folder_path} - {str(e)}")
            return False


def main():
    """
    主函数
    """
    print("🚀 开始生成index.md文件...")
    print("=" * 50)
    
    # 确保content目录存在
    CONTENT_DIR.mkdir(exist_ok=True)
    
    # 遍历所有文件夹
    folders_to_process = []
    for root, dirs, files in os.walk(CONTENT_DIR):
        # 跳过根目录（手动维护）
        if root == str(CONTENT_DIR):
            continue
        
        folder_path = Path(root)
        folders_to_process.append(folder_path)
    
    print(f"📁 发现 {len(folders_to_process)} 个文件夹")
    print()
    
    # 处理每个文件夹
    success_count = 0
    fail_count = 0
    
    for folder_path in folders_to_process:
        if generate_index(folder_path):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 50)
    print("📊 生成统计:")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📁 总计: {success_count + fail_count}")
    print("=" * 50)
    print("🎉 生成完成！")
    print("📝 注意：根目录content/index.md需要手动维护")


if __name__ == "__main__":
    main()
