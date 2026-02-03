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
我们在根目录准备了多个 Python 脚本来帮你"偷懒"。**在提交代码前，请按需运行它们：**

| 脚本名称 | 功能说明 | 何时使用 |
| :--- | :--- | :--- |
| `tools.py` | **统一工具管理脚本**，提供一致的命令行接口 | 推荐使用，可管理所有其他工具。 |
| `md_to_folder.py` | 将落单的 `.md` 自动转为 `文件夹/index.md` | **解决 404 的核心脚本**。当你直接丢入 Markdown 文件后运行。 |
| `auto_index.py` | 扫描所有目录，为缺失 `index.md` 的地方自动补齐 | 快速新建大量文件夹后使用。 |
| `sync.py` | 自动从外校（如浙大、交大）仓库拉取最新资料 | 需要同步外部开源资源时运行。 |
| `upload_to_oss.py` | 将 >50MB 的大文件上传至 ModelScope | 处理大体积压缩包、视频，获取下载直链。 |

#### 使用方法

**统一工具管理（推荐）：**
```bash
# 查看帮助
python tools.py --help

# 自动补全索引
python tools.py index --content-dir content --verbose

# Markdown 文件转文件夹
python tools.py md2folder --content-dir content --verbose

# 同步外部资源
python tools.py sync --config sync_config.yaml --verbose --parallel

# 上传大文件
python tools.py upload --file "G:\工程热力学.zip" --verbose
```

**单个脚本使用：**
```bash
# 自动补全索引
python auto_index.py --content-dir content --verbose

# Markdown 文件转文件夹
python md_to_folder.py --content-dir content --verbose

# 同步外部资源
python sync.py --config sync_config.yaml --verbose --parallel

# 上传大文件
python upload_to_oss.py --file "G:\工程热力学.zip" --verbose
```

### 3. 大文件处理流程
禁止将大型二进制文件（>100MB）直接 Push 到 GitHub。
1. **使用命令行参数**：运行脚本时通过 `--file` 参数指定文件路径。
   ```bash
   # 使用统一工具
   python tools.py upload --file "G:\工程热力学.zip" --verbose
   
   # 或直接使用脚本
   python upload_to_oss.py --file "G:\工程热力学.zip" --verbose
   ```
2. 等待上传完成。
3. **复制输出**：脚本会自动在控制台打印出一段 Markdown 下载块（带图标）。
4. **粘贴**：将这段代码粘贴到对应学科的 `index.md` 中。

---

## ✅ 提交前自检 (Checklist)

1. [ ] 是否已运行 `python tools.py md2folder --content-dir content`？
2. [ ] 是否已运行 `python tools.py index --content-dir content`？
3. [ ] 文件名是否包含空格或中文？（如有，请重命名或运行 `python tools.py sync` 的清洗逻辑）。
4. [ ] 本地预览 `npx quartz build --serve` 是否一切正常？

---