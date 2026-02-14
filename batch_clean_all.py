import os
import json
import re
from pathlib import Path

# ================= 配置 =================
CONTENT_DIR = Path("content")

# 必须与 smart_sync.py 保持一致的类型映射
FILE_TYPES = {
    "1": "教材",
    "2": "课件",
    "3": "笔记",
    "4": "作业",
    "5": "试卷",
    "6": "其他"
}

# 垃圾文件特征（直接删除条目）
GARBAGE_PATTERNS = [
    r"^~\$",           # Word 临时锁定文件
    r"^\._",           # macOS 元数据文件
    r"\.DS_Store",
    r"Thumbs\.db"
]

# 副本特征（用于文件名清洗）
# 会把 "Exam(1).pdf" -> "Exam.pdf"
DUPLICATE_PATTERNS = [
    r"\s?\(\d+\)",    # (1)
    r"（\d+）",        # （1）
    r"\s?-\s?副本",
    r"\s?-\s?Copy",
    r"\s?-\s?copy"
]

def clean_filename(filename):
    """去除文件名中的副本标记，还原真身"""
    name, ext = os.path.splitext(filename)
    for p in DUPLICATE_PATTERNS:
        name = re.sub(p, "", name)
    return name.strip() + ext

def is_garbage(filename):
    """判断是否为垃圾文件"""
    for p in GARBAGE_PATTERNS:
        if re.search(p, filename): return True
    return False

def get_course_title(index_path):
    """
    尝试从现有的 index.md 中读取 title
    如果读不到，返回文件夹名称作为保底
    """
    if not index_path.exists():
        return index_path.parent.name
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith("title:"):
                    # 提取 title: 后的内容，去两边空格
                    return line.split(":", 1)[1].strip()
    except Exception as e:
        print(f"⚠️ 警告: 读取 {index_path} 标题失败: {e}")
    
    return index_path.parent.name

def render_index_md(course_name, data):
    """生成 Markdown 内容"""
    grouped = {}
    for f in data['files']:
        t = str(f.get('type', '6'))
        if t not in grouped: grouped[t] = []
        grouped[t].append(f)
        
    md_content = f"---\ntitle: {course_name}\n---\n\n# {course_name}\n\n"
    
    # 按类型排序
    for t_key in sorted(grouped.keys()):
        t_name = FILE_TYPES.get(t_key, "其他").split('(')[0]
        md_content += f"## {t_name}\n"
        
        # 组内按文件名排序
        items = sorted(grouped[t_key], key=lambda x: x['name'])
        
        for item in items:
            icon = "📄"
            fname = item['name'].lower()
            if fname.endswith('pdf'): icon = "📕"
            elif fname.endswith('zip'): icon = "📦"
            elif fname.endswith('ppt') or fname.endswith('pptx'): icon = "📺"
            elif fname.endswith('doc') or fname.endswith('docx'): icon = "📄"
            
            # 兼容 size 可能是字符串或数字的情况
            size_display = item.get('size', 'Unknown')
            
            md_content += f"- {icon} **{item['name']}** <small>({size_display})</small> [☁️ 点击下载]({item['url']})\n"
    
    return md_content

def process_course_folder(folder_path):
    """处理单个课程文件夹"""
    json_path = folder_path / "resources.json"
    index_path = folder_path / "index.md"
    
    # 1. 读取 JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 错误: 无法读取 {json_path}: {e}")
        return

    # 兼容处理：有些 JSON 根节点可能是 list
    items = data if isinstance(data, list) else data.get('files', [])
    if not items:
        return # 空文件，跳过

    original_count = len(items)
    cleaned_groups = {}

    # 2. 清洗数据（去重、标准化）
    for item in items:
        name = item.get('name', '')
        if not name or is_garbage(name):
            continue

        # 计算标准名
        standard_name = clean_filename(name)
        
        if standard_name not in cleaned_groups:
            cleaned_groups[standard_name] = []
        cleaned_groups[standard_name].append(item)

    # 3. 选出最佳条目
    final_files = []
    for std_name, group in cleaned_groups.items():
        # 评分规则：
        # 1. 名字完全匹配标准名的优先 (score=0)
        # 2. URL 长度短的优先 (通常意味着没有 (1) 后缀)
        best_item = sorted(group, key=lambda x: (
            0 if x['name'] == std_name else 1, 
            len(x.get('url', ''))
        ))[0]
        
        # 强制修正显示名称为标准名
        best_item['name'] = std_name
        final_files.append(best_item)

    final_files.sort(key=lambda x: x['name'])
    
    # 4. 获取课程名称（保持原有的 Frontmatter Title）
    course_name = get_course_title(index_path)

    # 5. 写回 JSON
    new_data = {"files": final_files}
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    # 6. 写回 Index.md
    md_content = render_index_md(course_name, new_data)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ 处理: {course_name:<15} \t| 修正前: {original_count} -> 修正后: {len(final_files)} \t| 路径: {folder_path}")

def main():
    if not CONTENT_DIR.exists():
        print(f"❌ 找不到目录: {CONTENT_DIR}")
        return

    print("🚀 开始全量清洗...")
    
    count = 0
    # 遍历 content 下所有子目录
    for root, dirs, files in os.walk(CONTENT_DIR):
        if "resources.json" in files:
            process_course_folder(Path(root))
            count += 1

    print(f"\n🎉 全量清洗完成！共处理了 {count} 个课程节点。")
    print("请务必检查 git diff 确认更改无误。")

if __name__ == "__main__":
    main()