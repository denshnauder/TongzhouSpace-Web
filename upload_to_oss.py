"""
【工具名称】：upload_to_oss.py (ModelScope 大文件上传工具)
【使用方法】：
    python upload_to_oss.py [--file FILE] [--config CONFIG] [--verbose]
【功能说明】：
    - 自动清洗文件名，确保 URL 链接不含空格/中文。
    - 通过 Git LFS 将大文件推送到 ModelScope 托管。
    - 运行成功后，直接从控制台复制生成的 Markdown 下载块到笔记中。
【注意事项】：
    - 本脚本会创建临时工作目录 temp_git_workdir，运行结束后自动删除。
    - 如果上传失败，请检查网络（建议开启代理）或 Token 权限。
"""

import os
import stat
import shutil
import subprocess
import re
import argparse
import logging
from dotenv import load_dotenv

def parse_args():
    parser = argparse.ArgumentParser(description='ModelScope 大文件上传工具')
    parser.add_argument('--file', help='要上传的文件路径')
    parser.add_argument('--config', default='upload_config.yaml', help='配置文件路径')
    parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    return parser.parse_args()

def load_config(config_path):
    if not os.path.exists(config_path):
        # 默认配置
        return {
            'username': 'DenShnauder',
            'repo_name': 'Tongji-Res-Archive',
            'work_dir': './temp_git_workdir'
        }
    
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        logging.warning("⚠️  未安装 yaml 模块，使用默认配置")
        return {
            'username': 'DenShnauder',
            'repo_name': 'Tongji-Res-Archive',
            'work_dir': './temp_git_workdir'
        }

def sanitize_name(name):
    """清洗文件名：转小写、去空格、去特殊字符，确保 URL 不会断掉"""
    name = name.lower()
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^\u4e00-\u9fa5a-z0-9\-.]', '', name)
    return name

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def force_delete_dir(dir_path):
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path, onerror=remove_readonly)
        except Exception as e:
            logging.error(f"❌ 删除目录失败: {dir_path}, 错误: {e}")

def run_git_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ 命令执行失败: {cmd}")
        logging.error(f"错误输出: {e.stderr}")
        raise e

def upload_file(file_path, config, access_token):
    """上传单个文件"""
    try:
        username = config['username']
        repo_name = config['repo_name']
        work_dir = config['work_dir']
        
        # 预先清洗文件名
        original_filename = os.path.basename(file_path)
        clean_filename = sanitize_name(original_filename)
        
        git_url = f"https://oauth2:{access_token}@www.modelscope.cn/datasets/{username}/{repo_name}.git"
        
        # 清理工作目录
        force_delete_dir(work_dir)
        
        logging.info(f"📥 正在连接 ModelScope 仓库...")
        run_git_cmd(f"git clone --depth 1 {git_url} {work_dir}")
        
        dest_path = os.path.join(work_dir, clean_filename)
        
        # 复制文件
        if os.path.isdir(file_path):
            shutil.copytree(file_path, dest_path)
        else:
            shutil.copy(file_path, dest_path)
        
        # Git LFS 和 推送
        logging.info(f"🚀 正在上传文件: {clean_filename} ...")
        run_git_cmd(f"git lfs track \"{clean_filename}\"", cwd=work_dir)
        run_git_cmd("git add .", cwd=work_dir)
        run_git_cmd(f'git commit -m "Upload: {clean_filename}"', cwd=work_dir)
        run_git_cmd("git push", cwd=work_dir)
        
        # 【核心改进】自动生成直链
        # ModelScope 的文件直链格式如下：
        download_url = f"https://www.modelscope.cn/datasets/{username}/{repo_name}/resolve/master/{clean_filename}"
        
        print("\n" + "="*50)
        print("✅ 上传成功！")
        print("📂 文件名:", clean_filename)
        print("🔗 下载直链:", download_url)
        print("\n📝 请复制下方 Markdown 代码到你的 Quartz 笔记中：")
        print(f"> [!DOWNLOAD] 资源下载\n> [{original_filename}]({download_url})")
        print("="*50)
        
        return True
        
    except Exception as e:
        logging.error(f"❌ 上传失败: {e}")
        return False
    finally:
        # 清理工作目录
        force_delete_dir(work_dir)

def main():
    args = parse_args()
    
    # 配置日志
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')
    
    # 加载环境变量
    load_dotenv()
    access_token = os.getenv("MODELSCOPE_TOKEN")
    
    if not access_token:
        print("❌ 错误：未在 .env 中找到 MODELSCOPE_TOKEN")
        return
    
    # 加载配置
    config = load_config(args.config)
    
    # 上传文件
    if args.file:
        if os.path.exists(args.file):
            upload_file(args.file, config, access_token)
        else:
            print(f"❌ 错误：文件不存在: {args.file}")
    else:
        print("❌ 错误：请指定要上传的文件路径，使用 --file 参数")
        print("例如：python upload_to_oss.py --file \"G:\工程热力学.zip\"")

if __name__ == "__main__":
    main()