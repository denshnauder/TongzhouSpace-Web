# 同舟空间 (Tongji Share)

同舟空间是一个基于 **Quartz** 和 **ModelScope** 构建的同济大学开源资料分享平台。
本项目采用“云端存储资源 + 本地管理索引”的架构，实现了低成本、高可用的静态站点部署。

## 🏗 核心架构

* **前端**: [Quartz 4](https://quartz.jzhao.xyz/) (静态站点生成器)
* **存储**: [ModelScope](https://modelscope.cn/) (提供直链存储)
* **部署**: Vercel (托管静态页面)
* **管理**: Python ETL 脚本 (自动化清洗、分类、上传)

---

## 📂 目录结构说明

    /
    ├── _inbox/                  # [入口] 脏数据投放区 (手动放入)
    ├── _staging/                # [缓冲区] 清洗后的待上传文件
    ├── content/                 # [仓库] 网站正文与资源索引
    ├── scripts/                 # [核心] 自动化脚本模块
    │   ├── config.py            # 全局配置
    │   └── core/                # 核心逻辑模块
    ├── manage.py                # [主控] 唯一的命令行入口
    └── quartz.config.ts         # 网站样式与插件配置

---

## 🚀 管理员工作流 (Admin Workflow)

维护流程分为两个阶段：**处理 (Process)** 和 **上传 (Upload)**。

### 1. 预处理 (Public Step)
此步骤不需要令牌。

    python manage.py process

* ✅ 扫描 content 目录，构建课程地图。
* ✅ 清洗文件名（去除副本标记）。
* ✅ 识别课程归属并移动到 _staging。

### 2. 上传与发布 (Private Step)
此步骤需要 ModelScope 令牌。

    python manage.py upload

* ☁️ 上传 _staging 文件到 ModelScope。
* 📝 更新课程索引与 index.md。
* 📤 自动推送到 GitHub 触发部署。

---

## 🧠 智能配置 (Configuration)

规则均定义在 `scripts/config.py` 中。

* **添加课程别名**: 修改 `COURSE_ALIAS_MAP`。
* **修改分类关键词**: 调整 `TYPE_KEYWORDS`。

---

## 🛠️ 开发环境安装

1. **安装依赖 (Python)**: `pip install modelscope python-dotenv`
2. **安装依赖 (Node.js)**: `npm install`
3. **本地预览**: `npx quartz build --serve`

---

## ⚖️ 协议
本仓库遵循 MIT 协议。
资料内容仅供交流学习使用。