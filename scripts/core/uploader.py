import os
import json
import shutil
from pathlib import Path
from datetime import datetime
# 假设你已经安装了 modelscope SDK
from modelscope.hub.api import HubApi
from scripts.config import STAGING_DIR, CONTENT_DIR, CATEGORY_MAP, FILE_TYPES

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
                if not target_content_dir.exists():
                    print(f"   ❌ 目标课程目录不存在: {target_content_dir}")
                    continue

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
        
        # 1. 获取课程标题 (保持原样)
        title = course_dir.name
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith("title:"):
                            title = line.split(":", 1)[1].strip()
                            break
            except: pass
        
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
                
                md_content += f"- {icon} **{item['name']}** <small>({item.get('size','')})</small> [☁️ 点击下载]({item['url']})\n"
        
        # 5. 写入文件
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(md_content)