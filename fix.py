# fix_paths.py
import json
from pathlib import Path

MEMORY_FILE = Path('scripts/memory.json')

with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 暴力修复：所有反斜杠换成正斜杠
for code, info in data['courses'].items():
    if '\\' in info['path']:
        print(f"🔧 修正路径: {info['path']} -> ", end='')
        info['path'] = info['path'].replace('\\', '/')
        print(info['path'])

with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ memory.json 路径标准化完成。")