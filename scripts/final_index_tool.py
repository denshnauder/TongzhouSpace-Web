#!/usr/bin/env python3
"""
【工具名称】：final_index_tool.py (最终索引工具)
【使用方法】：
    python scripts/final_index_tool.py [--content-dir CONTENT_DIR] [--verbose] [--classify]
【功能说明】：
    - 递归扫描 content 目录下的所有子文件夹。
    - 为每个文件夹生成包含子文件夹和文件链接的 index.md 文件。
    - 自动将单文件归类到期末试卷(exams)和课件(lectures)等小文件夹。
    - 确保侧边栏和文件夹页面可以正常点击访问。
【参数说明】：
    --content-dir CONTENT_DIR  - 内容目录路径，默认为 content
    --verbose                 - 启用详细日志
    --classify                - 启用文件自动归类功能
【示例】：
    # 使用默认参数
    python scripts/final_index_tool.py
    
    # 指定内容目录并启用详细日志
    python scripts/final_index_tool.py --content-dir content --verbose
    
    # 启用文件自动归类功能
    python scripts/final_index_tool.py --classify
"""

import os
import argparse
import logging
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description='最终索引工具')
    parser.add_argument('--content-dir', default='content', help='内容目录路径')
    parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    parser.add_argument('--classify', action='store_true', help='启用文件自动归类功能')
    return parser.parse_args()


def classify_files(directory, verbose):
    """将单文件归类到期末试卷和课件等小文件夹"""
    # 定义文件类型与文件夹的映射
    file_types = {
        'exams': ['.pdf', '.docx', '.doc'],  # 试卷文件类型
        'lectures': ['.ppt', '.pptx']  # 课件文件类型
    }
    
    # 获取当前目录名称
    dir_name = os.path.basename(directory)
    
    # 如果当前目录已经是exams或lectures，不再创建子文件夹
    if dir_name in ['exams', 'lectures']:
        return
    
    # 如果当前目录是00-99课程分类文件夹，不再创建exams和lectures子文件夹
    if re.match(r'^\d{2}-', dir_name):
        return
    
    # 确保必要的文件夹存在
    for folder in ['exams', 'lectures']:
        folder_path = os.path.join(directory, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            if verbose:
                logging.info(f"📁 创建文件夹: {folder_path}")
            else:
                print(f"📁 创建文件夹: {folder_path}")
    
    # 遍历目录中的文件
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path) and not file_name == 'index.md' and not file_name.startswith('.'):
            # 获取文件扩展名
            ext = os.path.splitext(file_name)[1].lower()
            
            # 确定文件应该归类到哪个文件夹
            target_folder = None
            if ext in file_types['exams']:
                # 对于PDF、DOC等文件，默认归类到exams文件夹
                target_folder = 'exams'
            elif ext in file_types['lectures']:
                # 对于PPT等文件，默认归类到lectures文件夹
                target_folder = 'lectures'
            
            # 如果确定了目标文件夹，移动文件
            if target_folder:
                target_path = os.path.join(directory, target_folder, file_name)
                try:
                    os.rename(file_path, target_path)
                    if verbose:
                        logging.info(f"📋 已归类文件: {file_name} → {target_folder}/")
                    else:
                        print(f"📋 已归类文件: {file_name} → {target_folder}/")
                except Exception as e:
                    if verbose:
                        logging.error(f"❌ 归类文件失败: {file_name}, 错误: {e}")
                    else:
                        print(f"❌ 归类文件失败: {file_name}, 错误: {e}")


def generate_index(directory):
    """为指定目录生成index.md文件"""
    # 获取目录名称作为默认标题
    dir_name = os.path.basename(directory)
    
    # 生成title（使用目录名称的中文翻译，如果有的话）
    title_map = {
        'ideological-morality': '思想道德修养',
        'modern-history': '中国近现代史纲要',
        'situation-policy': '形势与政策',
        'calculus': '高等数学B上',
        'chemistry': '普通化学',
        'complex-analysis': '复变函数',
        'linear-algebra': '线性代数',
        'mathematical-equations': '数学物理方程',
        'physics': '大学物理',
        'earthquake-engineering': '地震工程学',
        'elasticity': '弹性力学',
        'electromagnetic-fields': '电磁场与电磁波',
        'engineering-materials': '工程材料',
        'engineering-mechanics': '工程力学',
        'groundwater-dynamics': '地下水动力学',
        'auto-theory': '汽车理论',
        'mechanical-computer-control': '机械控制用计算机',
        'medical-statistics': '医学统计学',
        'transportation-engineering': '交通工程学',
        'real-estate-development': '房地产开发与管理',
        'real-estate-valuation': '房地产估价',
        'exams': '期末考试',
        'lectures': '课件',
        '00-general-compulsory': '通识必修课',
        '01-general-elective': '通识选修课',
        '02-public-basic': '公共基础课',
        '03-prof-basic': '专业基础课',
        '04-prof-compulsory': '专业必修课',
        '05-prof-elective': '专业选修课',
        '06-practical': '实践环节',
        '99-unsorted': '未分类课程'
    }
    
    title = title_map.get(dir_name, dir_name)
    
    # 抓取同级文件夹中的其他文件或文件夹
    items = []
    for item in sorted(os.listdir(directory)):
        # 跳过index.md文件本身
        if item == 'index.md':
            continue
        
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            # 文件夹
            item_title = title_map.get(item, item)
            items.append(f"- [{item_title}]({item}/)")
        else:
            # 文件
            items.append(f"- [{item}]({item})")
    
    # 生成index.md内容，不需要#级标题
    content = f"---\ntitle: {title}\n---\n\n欢迎访问本页面。\n"
    
    if items:
        content += "\n## 相关链接\n\n"
        content += "\n".join(items)
    
    # 写入index.md文件
    index_path = os.path.join(directory, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已生成: {index_path}")


def main():
    """主函数"""
    args = parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    content_dir = args.content_dir
    classify = args.classify
    
    try:
        for root, dirs, files in os.walk(content_dir):
            # 跳过.git目录等不需要处理的目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # 获取当前目录名称
            dir_name = os.path.basename(root)
            
            # 如果启用了文件归类，且当前目录不是exams或lectures，且不是00-99课程分类文件夹，先归类文件
            if classify and dir_name not in ['exams', 'lectures'] and not re.match(r'^\d{2}-', dir_name):
                classify_files(root, args.verbose)
            
            # 为每个目录生成index.md文件
            generate_index(root)
        
        print(f"\n📊 统计信息:")
        print(f"✅ 已完成所有索引文件的生成")
        if classify:
            print(f"✅ 已完成文件归类")
        
    except Exception as e:
        if args.verbose:
            logging.error(f"❌ 执行失败: {e}")
        else:
            print(f"❌ 执行失败: {e}")


if __name__ == "__main__":
    main()
