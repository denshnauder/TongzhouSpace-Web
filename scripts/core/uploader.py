import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from modelscope.hub.api import HubApi
# 引入 DIR_DISPLAY_MAP 以便自动生成中文标题
# 如果你的 config.py 还没更新这个变量，这里会报错，所以请确保 config.py 是最新的
from scripts.config import STAGING_DIR, CONTENT_DIR, FILE_TYPES, DIR_DISPLAY_MAP

class Uploader:
    def __init__(self, token, repo_id):
        self.api = HubApi()
        self.api.login(token)
        self.repo_id = repo_id

    def run(self):
        print("☁️  [Stage 2] 开始上传 Staging (需要 Token)...")
        if not STAGING_DIR.exists():
            print("   Staging 为空。")
            return

        # 遍历 Staging 下的所有文件
        # 结构: _staging/CATEGORY/COURSE/TYPE/file
        for cat_dir in STAGING_DIR.iterdir():
            if not cat_dir.is_dir(): continue
            
            for course_dir in cat_dir.iterdir():
                if not course_dir.is_dir(): continue
                
                # 对应的 content 目录
                target_content_dir = CONTENT_DIR / cat_dir.name / course_dir.name
                
                # ================= 核心修改：自动创建目录 =================
                if not target_content_dir.exists():
                    print(f"   ✨ 发现新课程，自动创建目录: {target_content_dir.name}")
                    target_content_dir.mkdir(parents=True, exist_ok=True)
                # =======================================================

                json_path = target_content_dir / "resources.json"
                # 读取现有的 resources.json
                resources = {"files": []}
                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        resources = json.load(f)

                updated = False
                
                # 遍历类型文件夹 (1, 2, 3...)
                for type_dir in course_dir.iterdir():
                    if not type_dir.is_dir(): continue
                    type_id = type_dir.name # "1", "2"...

                    for f in type_dir.iterdir():
                        if not f.is_file(): continue
                        
                        print(f"   🚀 正在上传: {f.name}")
                        # 1. 上传到 ModelScope
                        try:
                            self.api.upload_file(
                                repo_id=self.repo_id,
                                path_or_fileobj=str(f),
                                path_in_repo=f.name, # 简单起见放在根目录
                                revision='master'
                            )
                            # 生成 URL
                            url = f"https://modelscope.cn/models/{self.repo_id}/resolve/master/{f.name}"
                            
                            # 2. 更新 Metadata
                            new_entry = {
                                "name": f.name,
                                "url": url,
                                "size": f"{f.stat().st_size / 1024:.1f}KB",
                                "type": type_id,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            }
                            # 检查去重 (可选)
                            resources['files'].append(new_entry)
                            updated = True
                            
                            # 3. 删除 Staging 文件
                            f.unlink()
                            
                        except Exception as e:
                            print(f"   ❌ 上传失败: {e}")

                # 4. 如果有更新，保存 JSON 并刷新 Index
                if updated:
                    # 去重逻辑 (简单按 URL 去重)
                    unique_files = {v['url']: v for v in resources['files']}.values()
                    resources['files'] = list(unique_files)
                    
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(resources, f, indent=2, ensure_ascii=False)
                    
                    self.render_index(target_content_dir, resources)
                    print(f"   📝 已更新索引: {course_dir.name}")

    def render_index(self, course_dir, data):
        """重新生成 index.md"""
        index_file = course_dir / "index.md"
        dir_name = course_dir.name.lower()
        
        # ================= 核心修改：优先查字典 =================
        # 1. 优先查 Config 里的中文名
        title = DIR_DISPLAY_MAP.get(dir_name)
        
        # 2. 查不到就尝试读旧文件 (兼容性)
        if not title and index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith("title:"):
                            title = line.split(":", 1)[1].strip()
                            break
            except: pass
        
        # 3. 实在没有，只能用英文文件夹名，并打印警告
        if not title:
            title = course_dir.name
            print(f"   ⚠️  警告: 新课程 {dir_name} 未在 config.py 中注册中文名！")
        # ======================================================
        
        # 2. 准备 Markdown 内容
        md_content = f"---\ntitle: {title}\n---\n\n"
        
        # 3. 分组与排序
        grouped = {}
        for f in data.get('files', []):
            t = str(f.get('type', '6'))
            if t not in grouped: grouped[t] = []
            grouped[t].append(f)
            
        # 4. 生成列表
        for t_key in sorted(grouped.keys()):
            t_name = FILE_TYPES.get(t_key, "其他")
            md_content += f"## {t_name}\n"
            
            # 简单的文件名排序
            items = sorted(grouped[t_key], key=lambda x: x['name'])
            
            for item in items:
                icon = "📄"
                fname = item['name'].lower()
                if fname.endswith('pdf'): icon = "📕"
                elif fname.endswith('zip'): icon = "📦"
                elif fname.endswith('ppt') or fname.endswith('pptx'): icon = "📺"
                
                md_content += f"- {icon} [{item['name']}]({item['url']}) <small style='opacity:0.6'>({item.get('size','-')})</small>\n"
        
        # 5. 写入文件
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(md_content)