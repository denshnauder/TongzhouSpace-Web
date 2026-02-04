import os
import re

# 定义要查找的模式
patterns = [
    r'- \[期末考试\]\(exams/\)\s*',
    r'- \[课件\]\(lectures/\)\s*',
    r'## 相关链接\s*'
]

def update_index_files():
    # 遍历 content 目录
    for root, dirs, files in os.walk('content'):
        for file in files:
            if file == 'index.md':
                file_path = os.path.join(root, file)
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 保存原始内容以便比较
                    original_content = content
                    
                    # 应用所有模式
                    for pattern in patterns:
                        content = re.sub(pattern, '', content, flags=re.MULTILINE)
                    
                    # 移除多余的空行
                    content = re.sub(r'\n{3,}', '\n\n', content)
                    
                    # 如果内容有变化，写回文件
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f'Updated: {file_path}')
                except Exception as e:
                    print(f'Error updating {file_path}: {e}')

if __name__ == '__main__':
    update_index_files()
    print('\nUpdate completed!')
