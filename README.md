# TongzhouSpace - Static Frontend

## 项目简介
同舟空间是我在课余时间独立开发的一个面向校园社交圈的资源共享平台。本仓库为该项目的静态前端部分。

开发初衷是为了解决同学间学习资料和笔记共享不便的问题。

## 技术栈
* TypeScript / JavaScript
* Quartz (基于 Markdown 的静态化站点生成框架)
* CSS / SCSS 

## 核心工作
* 利用 Quartz 框架搭建了整体的页面路由与文档树结构。
* 自定义了部分页面布局与样式（如双向链接、大纲视图）。
* 配置了一套文件上传的脚本，实现了文件的整理归档生成链接一站式管理。

## 运行与构建
1. 安装依赖: `npm install`
2. 本地预览: `npx quartz build --serve`
3. 生成静态文件: `npx quartz build`

注：因个人学业与车队精力有限，该项目目前处于暂停维护状态，但其完整走通了从本地 Markdown 渲染到线上部署的全流程。
