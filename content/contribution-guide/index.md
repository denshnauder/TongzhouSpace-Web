---
title: "🤝 资源贡献指南"
date: 2026-01-31
---

欢迎来到同舟空间！本站是一个由同济学子自发维护的资源共享站。为了保证网站结构清晰、避免 404 错误，并充分利用我们的自动化脚本，请参考以下指南进行贡献。

> [!IMPORTANT]
> 本站的核心逻辑是 **“自动化归档”**。能用脚本解决的事情，我们绝不手动操作。

---

## 📂 方式一：快速贡献（推荐）

### 1.1 侧边栏直接提交（最简单）

如果你访问网站首页，你可以直接在侧边栏找到“文件上传”组件：

1. **进入网站**：访问 [同舟空间](https://tongzhou-space.vercel.app) 首页。
2. **找到组件**：在侧边栏中找到“文件上传”卡片。
3. **选择文件夹**：在“目标文件夹”输入框中选择或输入文件要存放的位置。
4. **选择文件**：点击“选择文件”按钮，选择要上传的文件（支持 PDF、Markdown 等）。
5. **点击上传**：等待上传完成，系统会自动处理文件并同步到网站。

### 1.2 GitHub Issues 提交

如果你无法访问网站或需要上传更多文件，请使用 GitHub 的 Issue 功能：

1. **进入入口**：点击 [GitHub Issues](https://github.com/denshnauder/TongzhouSpace/issues)。
2. **新建任务**：点击 **"New Issue"**。
3. **上传资料**：将你的文件（PDF、Zip、图片、笔记等）直接拖入对话框。
4. **填写分类**：在描述中注明资料所属的学科（如：工程热力学-历年卷）。
5. **完成**：管理员（DenShnauder）收到后会通过自动化脚本将其同步至网站。

---

## 🛠️ 方式二：维护者贡献（本地环境）

如果你已经克隆了仓库并在本地整理资料，请遵循以下流程以确保 Quartz 正常构建。

### 1. 文件存放规范
* **位置**：所有资料必须放在 `content/` 文件夹下。
* **命名**：**全小写英文 + 短横线**（例如：`signal-and-system`）。
* **禁止**：路径中禁止出现空格、中文或特殊字符。
* **模式**：必须采用 **文件夹模式 (Folder Note)**。即：`学科名/index.md`。

### 2. 自动化脚本工具包 (The Toolkit)
我们在 `scripts` 目录准备了多个 Python 脚本来帮你"偷懒"。**在提交代码前，请按需运行它们：**

| 脚本名称 | 功能说明 | 何时使用 |
| :--- | :--- | :--- |
| `scripts/main.py` | **统一工具管理脚本**，提供一致的命令行接口 | 推荐使用，可管理所有其他工具。 |
| `scripts/md_to_folder.py` | 将落单的 `.md` 自动转为 `文件夹/index.md` | **解决 404 的核心脚本**。当你直接丢入 Markdown 文件后运行。 |
| `scripts/auto_index.py` | 扫描所有目录，为缺失 `index.md` 的地方自动补齐 | 快速新建大量文件夹后使用。 |
| `scripts/process_files.py` | 自动解压 zip 文件并处理大文件 | 上传包含多个文件的压缩包后运行。 |
| `scripts/smart_migrate.py` | 智能迁移内容到分类结构 | 整理大量历史资料时运行。 |

#### 使用方法

**统一工具管理（推荐）：**
```bash
# 查看帮助
python scripts/main.py --help

# 智能迁移内容到分类结构
python scripts/main.py migrate

# 处理文件（解压、大文件处理）
python scripts/main.py process

# 生成缺失的 index.md 文件
python scripts/main.py index --content-dir content --verbose

# 将 MD 文件转换为文件夹结构
python scripts/main.py folderize --content-dir content --verbose

# 运行所有命令
python scripts/main.py all --content-dir content --verbose
```

**单个脚本使用：**
```bash
# 自动补全索引
python scripts/auto_index.py --content-dir content --verbose

# Markdown 文件转文件夹
python scripts/md_to_folder.py --content-dir content --verbose

# 处理文件（解压、大文件处理）
python scripts/process_files.py

# 智能迁移内容
python scripts/smart_migrate.py
```

### 3. 大文件处理流程
禁止将大型二进制文件（>100MB）直接 Push 到 GitHub。我们的脚本会自动处理大文件：

1. **上传文件**：将大文件放入 `content` 目录中的对应位置。
2. **运行脚本**：执行文件处理脚本：
   ```bash
   # 使用统一工具
   python scripts/main.py process
   
   # 或直接使用脚本
   python scripts/process_files.py
   ```
3. **自动处理**：脚本会：
   - 检测大于 100MB 的文件
   - 为大文件创建同名文件夹
   - 生成包含下载链接的 `index.md` 文件
   - （未来版本）自动上传到 ModelScope 并获取直链
4. **检查结果**：脚本执行完成后，会在控制台显示处理结果。

---

## ✅ 提交前自检 (Checklist)

1. [ ] 是否已运行 `python scripts/main.py folderize --content-dir content`？
2. [ ] 是否已运行 `python scripts/main.py index --content-dir content`？
3. [ ] 文件名是否包含空格或中文？（如有，请重命名）。
4. [ ] 本地预览 `npx quartz build --serve` 是否一切正常？
5. [ ] 上传的压缩包是否已被正确解压？（运行 `python scripts/main.py process` 检查）。

---