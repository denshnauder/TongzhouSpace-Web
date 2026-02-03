"""
【工具名称】：tools.py (统一工具管理脚本)
【使用方法】：
    python tools.py [command] [options]
【功能说明】：
    统一管理所有 Python 工具脚本，提供一致的命令行接口。
【命令列表】：
    index       - 缺失索引自动补全
    md2folder   - Markdown 文件转文件夹模式
    sync        - 外部资源自动同步
    upload      - ModelScope 大文件上传
"""

import argparse
import subprocess
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='统一工具管理脚本')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # index 命令
    index_parser = subparsers.add_parser('index', help='缺失索引自动补全')
    index_parser.add_argument('--content-dir', default='content', help='内容目录路径')
    index_parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    
    # md2folder 命令
    md2folder_parser = subparsers.add_parser('md2folder', help='Markdown 文件转文件夹模式')
    md2folder_parser.add_argument('--content-dir', default='content', help='内容目录路径')
    md2folder_parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    
    # sync 命令
    sync_parser = subparsers.add_parser('sync', help='外部资源自动同步')
    sync_parser.add_argument('--config', default='sync_config.yaml', help='配置文件路径')
    sync_parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    sync_parser.add_argument('--parallel', action='store_true', help='启用并行处理')
    
    # upload 命令
    upload_parser = subparsers.add_parser('upload', help='ModelScope 大文件上传')
    upload_parser.add_argument('--file', help='要上传的文件路径')
    upload_parser.add_argument('--config', default='upload_config.yaml', help='配置文件路径')
    upload_parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    
    return parser.parse_args()

def run_command(cmd):
    """运行命令"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False

def main():
    args = parse_args()
    
    if not args.command:
        print("❌ 错误：请指定命令")
        print("使用 --help 查看可用命令")
        return
    
    if args.command == 'index':
        cmd = f"python auto_index.py --content-dir \"{args.content_dir}\""
        if args.verbose:
            cmd += " --verbose"
        run_command(cmd)
    
    elif args.command == 'md2folder':
        cmd = f"python md_to_folder.py --content-dir \"{args.content_dir}\""
        if args.verbose:
            cmd += " --verbose"
        run_command(cmd)
    
    elif args.command == 'sync':
        cmd = f"python sync.py --config \"{args.config}\""
        if args.verbose:
            cmd += " --verbose"
        if args.parallel:
            cmd += " --parallel"
        run_command(cmd)
    
    elif args.command == 'upload':
        cmd = f"python upload_to_oss.py --config \"{args.config}\""
        if args.file:
            cmd += f" --file \"{args.file}\""
        if args.verbose:
            cmd += " --verbose"
        run_command(cmd)
    
    else:
        print(f"❌ 错误：未知命令: {args.command}")

if __name__ == "__main__":
    main()