import os
import json
import re
from urllib.parse import unquote

# 配置
CONTENT_DIR = "content"

# 1. 垃圾文件特征（直接删除条目）
GARBAGE_PATTERNS = [
    r"^~\$",           # Word 临时锁定文件
    r"^\._",           # macOS 元数据文件
    r"\.DS_Store",
    r"Thumbs\.db"
]

# 2. 文件名清洗特征（用于归一化名称，判断重复）
# 会把 "Exam(1).pdf" -> "Exam.pdf"
CLEAN_NAME_PATTERNS = [
    r"\(\d+\)",          # (1), (2)
    r"（\d+）",          # （1）
    r" - 副本",
    r" - Copy",
    r" - copy",
    r"_\d{13,}",         # 有时会出现的时间戳后缀
]

def is_garbage(filename):
    """判断是否为毫无价值的临时文件"""
    for pattern in GARBAGE_PATTERNS:
        if re.search(pattern, filename):
            return True
    return False

def get_clean_name(filename):
    """
    计算“理想文件名”。
    例如：'笔记(1).pdf' -> '笔记.pdf'
    """
    name, ext = os.path.splitext(filename)
    for pattern in CLEAN_NAME_PATTERNS:
        name = re.sub(pattern, "", name)
    return name.strip() + ext

def score_candidate(item, clean_name):
    """
    为候选条目打分，分数越低越好（越接近正主）。
    用于在多个重复项中决定保留哪一个链接。
    """
    original_name = item.get('name', '')
    url = item.get('url', '')
    
    score = 0
    
    # 1. 如果名字本身就是干净的，优先级最高
    if original_name == clean_name:
        score -= 100
        
    # 2. 检查 URL 是否包含副本特征（URL 越短通常越正宗）
    # 解码 URL 以便检查中文
    decoded_url = unquote(url)
    if any(re.search(p, decoded_url) for p in CLEAN_NAME_PATTERNS):
        score += 50 # URL 脏了，扣分
        
    # 3. URL 长度惩罚（通常 (1) 的 URL 会更长）
    score += len(url) * 0.01
    
    return score

def process_resources_file(filepath):
    """处理单个 resources.json"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[错误] 无法读取 {filepath}: {e}")
        return

    # 兼容处理：有些可能是 list，有些是 dict
    if isinstance(data, list):
        items = data
    else:
        items = data.get('files', [])

    if not items:
        return

    # 分组容器：{ "CleanedName.pdf": [item1, item2...] }
    groups = {}
    
    # 1. 分组与初筛
    for item in items:
        name = item.get('name', '')
        if not name or is_garbage(name):
            continue # 丢弃垃圾
            
        clean_key = get_clean_name(name)
        if clean_key not in groups:
            groups[clean_key] = []
        groups[clean_key].append(item)

    # 2. 组内竞争，选出最佳链接
    final_items = []
    
    for clean_name, candidates in groups.items():
        # 如果只有一个候选，直接保留，但强制修正展示名称
        if len(candidates) == 1:
            best_item = candidates[0]
            if best_item['name'] != clean_name:
                print(f"  [修正名称] {best_item['name']} -> {clean_name}")
                best_item['name'] = clean_name
            final_items.append(best_item)
        else:
            # 有多个副本，进行PK
            # 按分数排序（越小越好）
            candidates.sort(key=lambda x: score_candidate(x, clean_name))
            best_item = candidates[0]
            
            # 记录被剔除的项
            removed_names = [c['name'] for c in candidates[1:]]
            print(f"  [去重合并] 保留: {best_item['name']}")
            print(f"            剔除: {', '.join(removed_names)}")
            
            # 同样强制修正名称
            best_item['name'] = clean_name
            final_items.append(best_item)

    # 3. 排序（按文件名首字母）
    final_items.sort(key=lambda x: x['name'])

    # 4. 写回文件
    # 保持原有结构（如果是dict就包一层，如果是list就直接存）
    output_data = {"files": final_items} if isinstance(data, dict) else final_items
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"错误: 找不到目录 '{CONTENT_DIR}'")
        return

    print("正在清理 resources.json 索引...")
    
    count = 0
    for root, dirs, files in os.walk(CONTENT_DIR):
        if "resources.json" in files:
            file_path = os.path.join(root, "resources.json")
            # print(f"扫描: {file_path}")
            process_resources_file(file_path)
            count += 1

    print(f"\n清理完成！共处理了 {count} 个索引文件。")
    print("现在所有的链接应该都是唯一的，且文件名已去除 '(1)' 等后缀。")

if __name__ == "__main__":
    main()
    