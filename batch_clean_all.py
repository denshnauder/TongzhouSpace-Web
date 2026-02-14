import os
import json
import re
from pathlib import Path

# ================= 配置 =================
CONTENT_DIR = Path("content")

FILE_TYPES = {
    "1": "教材", "2": "课件", "3": "笔记", 
    "4": "作业", "5": "试卷", "6": "其他"
}

GARBAGE_PATTERNS = [r"^~\$", r"^\._", r"\.DS_Store", r"Thumbs\.db"]
DUPLICATE_PATTERNS = [r"\s?\(\d+\)", r"（\d+）", r"\s?-\s?副本", r"\s?-\s?Copy"]

def clean_filename(filename):
    name, ext = os.path.splitext(filename)
    for p in DUPLICATE_PATTERNS:
        name = re.sub(p, "", name)
    return name.strip() + ext

def is_garbage(filename):
    for p in GARBAGE_PATTERNS:
        if re.search(p, filename): return True
    return False

def get_course_title(index_path):
    if not index_path.exists():
        return index_path.parent.name
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith("title:"):
                    return line.split(":", 1)[1].strip()
    except: pass
    return index_path.parent.name

def natural_sort_key(s):
    """
    核心修改：自然排序算法
    将字符串拆分为 [文本, 数字, 文本, 数字...] 的列表，
    使得 "Chapter 2" 排在 "Chapter 10" 前面。
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def render_index_md(course_name, data):
    """生成 Markdown 内容"""
    grouped = {}
    for f in data['files']:
        t = str(f.get('type', '6'))
        if t not in grouped: grouped[t] = []
        grouped[t].append(f)
        
    # 修改 1：只保留 Frontmatter，移除正文中的 # 标题
    md_content = f"---\ntitle: {course_name}\n---\n\n"
    
    # 按类型排序
    for t_key in sorted(grouped.keys()):
        t_name = FILE_TYPES.get(t_key, "其他").split('(')[0]
        md_content += f"## {t_name}\n"
        
        # 修改 2：使用自然排序
        items = sorted(grouped[t_key], key=lambda x: natural_sort_key(x['name']))
        
        for item in items:
            icon = "📄"
            fname = item['name'].lower()
            if fname.endswith('pdf'): icon = "📕"
            elif fname.endswith('zip'): icon = "📦"
            elif fname.endswith('ppt') or fname.endswith('pptx'): icon = "📺"
            elif fname.endswith('doc') or fname.endswith('docx'): icon = "📄"
            
            size_display = item.get('size', 'Unknown')
            md_content += f"- {icon} **{item['name']}** <small>({size_display})</small> [☁️ 点击下载]({item['url']})\n"
    
    return md_content

def process_course_folder(folder_path):
    json_path = folder_path / "resources.json"
    index_path = folder_path / "index.md"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except: return

    items = data if isinstance(data, list) else data.get('files', [])
    if not items: return

    cleaned_groups = {}
    for item in items:
        name = item.get('name', '')
        if not name or is_garbage(name): continue
        standard_name = clean_filename(name)
        if standard_name not in cleaned_groups: cleaned_groups[standard_name] = []
        cleaned_groups[standard_name].append(item)

    final_files = []
    for std_name, group in cleaned_groups.items():
        best_item = sorted(group, key=lambda x: (0 if x['name'] == std_name else 1, len(x.get('url', ''))))[0]
        best_item['name'] = std_name
        final_files.append(best_item)

    # 对 JSON 数据本身也做一次自然排序，保持整洁
    final_files.sort(key=lambda x: natural_sort_key(x['name']))
    
    course_name = get_course_title(index_path)

    new_data = {"files": final_files}
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    md_content = render_index_md(course_name, new_data)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ 处理: {course_name} ({folder_path.name})")

def main():
    if not CONTENT_DIR.exists(): return
    print("🚀 开始执行 v2 清洗（去重标题 + 自然排序）...")
    for root, dirs, files in os.walk(CONTENT_DIR):
        if "resources.json" in files:
            process_course_folder(Path(root))
    print("\n🎉 完成！请检查预览。")

if __name__ == "__main__":
    main()