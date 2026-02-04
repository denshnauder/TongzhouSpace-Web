---
title: 贡献指南
---

# 贡献指南

欢迎加入 TongzhouSpace 项目！本指南将帮助你了解如何为项目做出贡献。

## 项目介绍

TongzhouSpace 是一个学习资源共享平台，旨在收集和整理各类学习资料，方便学生和教育工作者使用。

## 贡献方式

### 1. 直接上传文件

你可以通过网站上的文件上传功能直接上传学习资料：

1. 访问网站首页
2. 点击「文件上传」按钮
3. 选择目标文件夹路径
4. 选择要上传的文件
5. 点击「上传」按钮

### 2. GitHub 贡献

如果你熟悉 Git 和 GitHub，可以通过以下方式贡献：

1. Fork 本仓库
2. 克隆到本地：`git clone https://github.com/denshnauder/TongzhouSpace-Web.git`
3. 创建分支：`git checkout -b feature/your-feature`
4. 提交更改：`git commit -m "feat: add your feature"`
5. 推送到远程：`git push origin feature/your-feature`
6. 创建 Pull Request

## 文件结构

项目采用以下文件结构：

```
content/
├── 00-通识教育/
├── 01-专业基础/
├── 02-专业核心/
├── ...
└── contribution-guide/
```

- **00-99 文件夹**：课程分类文件夹，不含「期末文件夹」和「课件文件夹」子文件夹
- **index.md**：每个文件夹中的索引文件，包含中文标题
- **其他文件**：学习资料文件，会被自动转换为幽灵文件

## 幽灵文件架构

为了减少仓库大小和避免 Vercel 构建超时，项目采用「幽灵文件架构」：

1. 二进制文件（如 PDF、视频等）会被上传到 ModelScope
2. 本地仓库中会创建对应的 `.md` 幽灵文件，包含下载链接
3. 当用户访问时，会通过链接从 ModelScope 下载原始文件

### 幽灵文件示例

```markdown
---
title: 汽车理论课件.pdf
type: file
download_link: https://modelscope.cn/api/v1/models/DenShnauder/Tongji-Res-Archive/repo?Revision=master&FilePath=content%2F02-%E4%B8%93%E4%B8%9A%E6%A0%B8%E5%BF%83%2F%E6%B1%BD%E8%BD%A6%E7%90%86%E8%AE%BA%2F%E6%B1%BD%E8%BD%A6%E7%90%86%E8%AE%BA%E8%AF%BE%E4%BB%B6.pdf
---

# 汽车理论课件.pdf

[点击下载](https://modelscope.cn/api/v1/models/DenShnauder/Tongji-Res-Archive/repo?Revision=master&FilePath=content%2F02-%E4%B8%93%E4%B8%9A%E6%A0%B8%E5%BF%83%2F%E6%B1%BD%E8%BD%A6%E7%90%86%E8%AE%BA%2F%E6%B1%BD%E8%BD%A6%E7%90%86%E8%AE%BA%E8%AF%BE%E4%BB%B6.pdf)
```

## 自动幽灵文件迁移

项目配置了 GitHub Actions 工作流，会在每次推送代码时自动执行幽灵文件迁移：

1. 检测新添加的二进制文件
2. 上传到 ModelScope 仓库
3. 创建对应的幽灵文件
4. 删除原始二进制文件
5. 提交并推送更改

## 注意事项

1. **文件大小限制**：单个文件不超过 20MB
2. **文件类型**：优先支持 PDF、Markdown 等文档格式
3. **命名规范**：文件名建议使用中文，清晰描述文件内容
4. **目录结构**：请将文件放在合适的分类文件夹中
5. **重复文件**：请先检查是否已有相同或相似的文件

## 代码规范

如果你贡献代码，请遵循以下规范：

- 使用 4 个空格缩进
- 遵循 TypeScript/JavaScript 标准规范
- 保持代码简洁明了
- 添加必要的注释

## 提交规范

提交信息请遵循以下格式：

```
type: subject

body (optional)

footer (optional)
```

其中 `type` 可以是：
- `feat`：新功能
- `fix`：修复 bug
- `docs`：文档修改
- `style`：代码风格调整
- `refactor`：代码重构
- `test`：测试相关
- `chore`：构建或依赖更新

## 联系我们

如果有任何问题或建议，欢迎联系项目维护者。

感谢你的贡献！
