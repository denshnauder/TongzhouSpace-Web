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
                                path_in_repo=f.name, # 简单起见放在根目录，或者你可以按结构放
                                revision='master'
                            )
                            # 生成 URL (假设是公开仓库)
                            url = f"https://modelscope.cn/models/{self.repo_id}/resolve/master/{f.name}"
                            
                            # 2. 更新 Metadata
                            new_entry = {
                                "name": f.name,
                                "url": url,
                                "size": f"{f.stat().st_size / 1024:.1f}KB",
                                "type": type_id,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            }
                            resources['files'].append(new_entry)
                            updated = True
                            
                            # 3. 移动文件到 content (可选，作为本地备份) 或直接删除
                            # 这里选择删除 Staging 文件，保持干净
                            f.unlink()
                            
                        except Exception as e:
                            print(f"   ❌ 上传失败: {e}")

                # 4. 如果有更新，保存 JSON 并刷新 Index
                if updated:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(resources, f, indent=2, ensure_ascii=False)
                    self.render_index(target_content_dir, resources)
                    print(f"   📝 已更新索引: {course_dir.name}")

    def render_index(self, course_dir, data):
        # 简单的 Index 渲染逻辑，你可以复用之前 batch_clean_all 的逻辑
        # 这里仅作示意
        pass # 请将之前的 render_index_md 函数逻辑放这里