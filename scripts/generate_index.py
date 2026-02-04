import os

def generate_index():
    # 定义要处理的根目录
    root_dir = 'content'
    
    if not os.path.exists(root_dir):
        print(f"Error: {root_dir} directory not found!")
        return
    
    print(f"Starting index generation in {root_dir}...")
    print("=" * 50)
    
    processed_dirs = 0
    
    # 遍历content目录及其所有子目录
    for dir_path, subdirs, files in os.walk(root_dir):
        # 获取当前目录的名称
        folder_name = os.path.basename(dir_path)
        
        # 收集非空子目录
        non_empty_subdirs = []
        for subdir in subdirs:
            subdir_path = os.path.join(dir_path, subdir)
            if os.listdir(subdir_path):  # 检查子目录是否非空
                non_empty_subdirs.append(subdir)
        
        # 收集.md文件（排除index.md）
        md_files = [file for file in files if file.endswith('.md') and file != 'index.md']
        
        # 如果没有项目，跳过
        if not non_empty_subdirs and not md_files:
            continue
        
        # 生成index.md内容
        index_content = f"---\ntitle: {folder_name}\n---\n\n"
        
        # 添加子目录链接
        if non_empty_subdirs:
            index_content += "## 子目录\n\n"
            for subdir in sorted(non_empty_subdirs):
                index_content += f"* [[{subdir}]]\n"
            index_content += "\n"
        
        # 添加文件链接
        if md_files:
            index_content += "## 文件\n\n"
            for md_file in sorted(md_files):
                # 移除.md扩展名
                file_name = os.path.splitext(md_file)[0]
                index_content += f"* [[{file_name}]]\n"
        
        # 写入index.md文件
        index_path = os.path.join(dir_path, 'index.md')
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            processed_dirs += 1
            print(f"Generated: {os.path.relpath(index_path, root_dir)}")
        except Exception as e:
            print(f"Error writing {index_path}: {e}")
    
    print("=" * 50)
    print(f"Index generation completed!")
    print(f"Processed {processed_dirs} directories.")

if __name__ == '__main__':
    generate_index()
