"""
【工具名称】：sync.py (外部资源自动同步工具)
【使用方法】：
    python sync.py [--config CONFIG] [--verbose] [--parallel]
【功能说明】：
    - 自动克隆外部仓库到临时目录。
    - 强制清洗文件名（全小写、去空格、去特殊字符）以符合 Quartz 规范。
    - 自动生成符合 Quartz 样式的目录索引 index.md。
【注意事项】：
    - 运行前请确保本地已安装 Git。
    - 会自动覆盖 target_path 下的同名文件，请勿在该目录下手动修改重要笔记。
"""

import os
import shutil
import subprocess
import logging
import stat
import re
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_args():
    parser = argparse.ArgumentParser(description='外部资源自动同步工具')
    parser.add_argument('--config', default='sync_config.yaml', help='配置文件路径')
    parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    parser.add_argument('--parallel', action='store_true', help='启用并行处理')
    return parser.parse_args()

def load_config(config_path):
    if not os.path.exists(config_path):
        # 默认配置
        return {
            'temp_dir': '.temp_cache_runtime',
            'content_root': 'content',
            'allowed_extensions': {
                '.pdf', '.docx', '.pptx', '.doc', '.ppt',
                '.md', '.markdown', '.txt',
                '.m', '.mat', '.py', '.ipynb', '.c', '.cpp', '.h',
                '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'
            },
            'exclude_dirs': {'.git', '.github', '.obsidian', '__pycache__', '.idea', '.vscode', 'node_modules'},
            'repo_configs': [
                {
                    'url': 'https://github.com/VipaiLab/Signals-and-Systems-course.git',
                    'repo_name': 'zju_signals_temp',
                    'target_path': 'signal-and-system/archives/zju-vipailab'
                }
            ]
        }
    
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        logging.warning("⚠️  未安装 yaml 模块，使用默认配置")
        return {
            'temp_dir': '.temp_cache_runtime',
            'content_root': 'content',
            'allowed_extensions': {
                '.pdf', '.docx', '.pptx', '.doc', '.ppt',
                '.md', '.markdown', '.txt',
                '.m', '.mat', '.py', '.ipynb', '.c', '.cpp', '.h',
                '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'
            },
            'exclude_dirs': {'.git', '.github', '.obsidian', '__pycache__', '.idea', '.vscode', 'node_modules'},
            'repo_configs': [
                {
                    'url': 'https://github.com/VipaiLab/Signals-and-Systems-course.git',
                    'repo_name': 'zju_signals_temp',
                    'target_path': 'signal-and-system/archives/zju-vipailab'
                }
            ]
        }

def sanitize_name(name):
    """清洗文件名：转小写、去空格、去特殊字符，确保 URL 不会断掉"""
    name = str(name).lower()
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^\u4e00-\u9fa5a-z0-9\-.]', '', name)
    name = re.sub(r'-+', '-', name)
    return name

def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, check=True, cwd=cwd, shell=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"命令执行失败: {cmd}")
        logging.error(f"错误输出: {e.stderr}")
        raise e

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repos(temp_dir, repo_configs):
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, onerror=remove_readonly)
    os.makedirs(temp_dir, exist_ok=True)
    
    cloned_repos = []
    for config in repo_configs:
        url = config['url']
        name = config['repo_name']
        logging.info(f"⬇️  正在下载: {name} ...")
        try:
            run_command(f"git clone --depth 1 {url} {name}", cwd=temp_dir)
            cloned_repos.append(config)
        except Exception as e:
            logging.error(f"❌ 克隆失败: {name}, 错误: {e}")
    
    return cloned_repos

def generate_index_md(directory, title, allowed_extensions):
    """生成索引页，确保链接也能匹配到被 sanitize 后的文件名"""
    files = [f for f in directory.iterdir() if f.is_file() and f.name != 'index.md' and f.suffix in allowed_extensions]
    if not files:
        return
    
    files.sort(key=lambda x: x.name)
    content_lines = [
        "---",
        f"title: {title}",
        "---",
        "",
        "## 📂 自动归档文件列表",
        "> 以下文件已自动处理命名规范，点击即可预览或下载。",
        ""
    ]
    
    for f in files:
        icon = "📄"
        if f.suffix in ['.md', '.txt']:
            icon = "📝"
        elif f.suffix in ['.pdf']:
            icon = "📕"
        elif f.suffix in ['.ppt', '.pptx']:
            icon = "📊"
        
        content_lines.append(f"- {icon} [{f.name}]({f.name})")
    
    index_path = directory / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content_lines))

def sync_repo(config, temp_dir, content_root, allowed_extensions, exclude_dirs):
    """同步单个仓库"""
    try:
        repo_name = config['repo_name']
        target_path = config['target_path']
        
        target_dir = Path(content_root) / target_path
        source_dir = Path(temp_dir) / repo_name
        
        if not source_dir.exists():
            logging.warning(f"⚠️  源目录不存在: {source_dir}")
            return 0
        
        sync_count = 0
        
        for root, dirs, files in os.walk(source_dir):
            # 排除掉不需要的文件夹
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in allowed_extensions:
                    # 关键：彻底清洗每一级路径
                    rel_path = file_path.relative_to(source_dir)
                    # 对每一层文件夹名、文件名都调用 sanitize_name
                    sanitized_parts = [sanitize_name(part) for part in rel_path.parts]
                    final_rel_path = Path(*sanitized_parts)
                    
                    final_dest = target_dir / final_rel_path
                    final_dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(file_path, final_dest)
                    sync_count += 1
        
        # 处理索引
        for root, dirs, files in os.walk(target_dir):
            current_path = Path(root)
            # 这里的标题我们稍微温柔点，把短横线换成空格，首字母大写，好看一点
            folder_title = current_path.name.replace("-", " ").title()
            generate_index_md(current_path, folder_title, allowed_extensions)
        
        logging.info(f"✅ 成功同步 {sync_count} 个文件到 {target_path}")
        return sync_count
        
    except Exception as e:
        logging.error(f"❌ 同步失败: {config['repo_name']}, 错误: {e}")
        return 0

def sync_files(temp_dir, content_root, repo_configs, allowed_extensions, exclude_dirs, parallel):
    """同步文件"""
    total_sync_count = 0
    
    if parallel:
        # 并行处理
        with ThreadPoolExecutor() as executor:
            futures = []
            for config in repo_configs:
                future = executor.submit(sync_repo, config, temp_dir, content_root, allowed_extensions, exclude_dirs)
                futures.append(future)
            
            for future in as_completed(futures):
                total_sync_count += future.result()
    else:
        # 串行处理
        for config in repo_configs:
            total_sync_count += sync_repo(config, temp_dir, content_root, allowed_extensions, exclude_dirs)
    
    return total_sync_count

def clean_up(temp_dir):
    if os.path.exists(temp_dir):
        logging.info("🧹 正在清理临时文件...")
        try:
            shutil.rmtree(temp_dir, onerror=remove_readonly)
        except Exception as e:
            logging.error(f"❌ 清理临时文件失败: {e}")

def main():
    args = parse_args()
    
    # 配置日志
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        temp_dir = config['temp_dir']
        content_root = config['content_root']
        allowed_extensions = set(config['allowed_extensions'])
        exclude_dirs = set(config['exclude_dirs'])
        repo_configs = config['repo_configs']
        
        # 克隆仓库
        cloned_repos = clone_repos(temp_dir, repo_configs)
        
        if not cloned_repos:
            logging.warning("⚠️  没有成功克隆的仓库")
        else:
            # 同步文件
            logging.info("🔄 开始处理并归档文件...")
            total_sync_count = sync_files(temp_dir, content_root, cloned_repos, allowed_extensions, exclude_dirs, args.parallel)
            logging.info(f"📊 总计同步 {total_sync_count} 个文件")
        
    except Exception as e:
        logging.error(f"❌ 发生错误: {e}")
    finally:
        # 清理临时文件
        clean_up(temp_dir)

if __name__ == "__main__":
    main()