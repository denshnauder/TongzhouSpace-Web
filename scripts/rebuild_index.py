import sys
import os
from pathlib import Path

# ================= 核心修复：强制定位项目根目录 =================
# 获取当前脚本所在目录 (D:\...\scripts)
current_dir = Path(__file__).resolve().parent
# 获取项目根目录 (D:\...\TongzhouSpace)
project_root = current_dir.parent
# 将根目录加入 Python 搜索路径，这样才能识别 'scripts.config'
sys.path.append(str(project_root))
# ==========================================================

import json
from scripts.config import CONTENT_DIR, CATEGORY_MAP, DIR_DISPLAY_MAP, FILE_TYPES

def render_category_index(category_dir):
    """强制重写分类索引 (父级)"""
    index_file = category_dir / "index.md"
    cat_key = category_dir.name
    cat_title = CATEGORY_MAP.get(cat_key, cat_key)
    
    content = ["---", f"title: {cat_title}", "---", "", ""]
    
    # 扫描子目录
    sub_dirs = [d for d in category_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    sub_dirs.sort(key=lambda x: x.name)
    
    for d in sub_dirs:
        # 核心逻辑：查字典
        d_name = d.name.lower()
        display_name = DIR_DISPLAY_MAP.get(d_name, d.name) # 查不到就回退到文件夹名
        content.append(f"- 📂 [{display_name}](./{d.name})")
        
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    print(f"✅ [Category] 已刷新: {cat_title}")

def render_course_index(course_dir):
    """强制重写课程索引 (子级)"""
    index_file = course_dir / "index.md"
    json_path = course_dir / "resources.json"
    dir_name = course_dir.name.lower()
    
    # 核心逻辑：查字典
    title = DIR_DISPLAY_MAP.get(dir_name, course_dir.name)
    
    # 读取资源列表
    files_data = []
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                files_data = data.get('files', [])
        except Exception as e:
            print(f"❌ JSON损坏: {json_path}")
            return

    # 生成内容
    md_content = f"---\ntitle: {title}\n---\n\n"
    
    # 分组渲染
    grouped = {}
    for f in files_data:
        t = str(f.get('type', '6'))
        if t not in grouped: grouped[t] = []
        grouped[t].append(f)
        
    for t_key in sorted(grouped.keys()):
        t_name = FILE_TYPES.get(t_key, "其他")
        md_content += f"## {t_name}\n"
        items = sorted(grouped[t_key], key=lambda x: x['name'])
        for item in items:
            icon = "📄"
            fname = item['name'].lower()
            if fname.endswith('pdf'): icon = "📕"
            elif fname.endswith('zip'): icon = "📦"
            elif fname.endswith('ppt') or fname.endswith('pptx'): icon = "📺"
            md_content += f"- {icon} [{item['name']}]({item['url']}) <small style='opacity:0.6'>({item.get('size','-')})</small>\n"

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"   Refreshed: {title}")

def main():
    print("🚀 开始强制重构所有索引...")
    if not CONTENT_DIR.exists():
        print("❌ Content 目录不存在")
        return

    # 遍历所有分类目录 (00-xxx, 03-xxx)
    for cat_dir in CONTENT_DIR.iterdir():
        if not cat_dir.is_dir() or cat_dir.name not in CATEGORY_MAP:
            continue
            
        # 1. 刷新分类页
        render_category_index(cat_dir)
        
        # 2. 刷新该分类下的所有课程页
        for course_dir in cat_dir.iterdir():
            if course_dir.is_dir() and not course_dir.name.startswith('.'):
                render_course_index(course_dir)

    print("\n🎉 重构完成！请检查 Quartz 预览。")

if __name__ == "__main__":
    main()