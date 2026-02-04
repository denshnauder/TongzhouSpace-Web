import os

def cleanup_mess():
    # 定义要清理的根目录
    root_dir = 'content'
    
    if not os.path.exists(root_dir):
        print(f"Error: {root_dir} directory not found!")
        return
    
    print(f"Starting cleanup in {root_dir}...")
    print("=" * 50)
    
    # 步骤1: 删除所有非.md文件
    print("Step 1: Removing non-Markdown files...")
    removed_files = 0
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if not file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    removed_files += 1
                    # 只打印前10个文件，避免输出过多
                    if removed_files <= 10:
                        print(f"  Removed: {os.path.relpath(file_path, root_dir)}")
                except Exception as e:
                    print(f"  Error removing {file_path}: {e}")
    
    if removed_files > 10:
        print(f"  ... and {removed_files - 10} more files")
    print(f"Total non-Markdown files removed: {removed_files}")
    print()
    
    # 步骤2: 自下而上清理空目录和shell目录
    print("Step 2: Pruning empty and shell directories (bottom-up)...")
    removed_dirs = 0
    
    # 收集所有目录并按深度排序（从深到浅）
    all_dirs = []
    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # 计算目录深度
            depth = dir_path.count(os.sep) - root_dir.count(os.sep)
            all_dirs.append((depth, dir_path))
    
    # 按深度降序排序（先处理深层目录）
    all_dirs.sort(key=lambda x: -x[0])
    
    # 处理每个目录
    for depth, dir_path in all_dirs:
        try:
            # 获取目录中的内容
            items = os.listdir(dir_path)
            
            # 条件A: 完全空的目录
            if len(items) == 0:
                os.rmdir(dir_path)
                removed_dirs += 1
                print(f"🗑️ Removed empty directory: {os.path.relpath(dir_path, root_dir)}")
            # 条件B: 只包含index.md的目录
            elif len(items) == 1 and items[0] == 'index.md':
                # 删除index.md文件
                index_path = os.path.join(dir_path, 'index.md')
                os.remove(index_path)
                # 删除目录
                os.rmdir(dir_path)
                removed_dirs += 1
                print(f"🗑️ Removed empty shell: {os.path.relpath(dir_path, root_dir)}")
        except Exception as e:
            print(f"Error processing {dir_path}: {e}")
    
    print(f"Total directories removed: {removed_dirs}")
    print()
    print("=" * 50)
    print("Cleanup completed!")

if __name__ == '__main__':
    cleanup_mess()
