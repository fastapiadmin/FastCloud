<div align="center">
     <p align="center">
          <img src="backend/data/logo.png" width="150" height="150" alt="logo" />  
     </p>
     <h1>FastCloud <sup style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.4em; vertical-align: super; margin-left: 5px;">v2.0.0</h1>
     <h3>现代化全栈快速开发平台</h3>
     <p>如果你喜欢这个项目，给个 ⭐️ 支持一下吧！</p>
     <p align="center">
          <a href="https://gitee.com/fastapiadmin/FastCloud.git" target="_blank">
               <img src="https://gitee.com/fastapiadmin/FastCloud/badge/star.svg?theme=dark" alt="Gitee Stars">
          </a>
          <a href="https://github.com/fastapiadmin/FastCloud.git" target="_blank">
               <img src="https://img.shields.io/github/stars/fastapiadmin/FastCloud?style=social" alt="GitHub Stars">
          </a>
          <a href="https://gitee.com/fastapiadmin/FastCloud/blob/master/LICENSE" target="_blank">
               <img src="https://img.shields.io/badge/License-MIT-orange" alt="License">
          </a>
          <img src="https://img.shields.io/badge/Python-≥3.10-blue"> 
          <img src="https://img.shields.io/badge/NodeJS-≥20.0-blue"> 
          <img src="https://img.shields.io/badge/MySQL-≥8.0-blue"> 
          <img src="https://img.shields.io/badge/Redis-≥7.0-blue"> 
          <img src="https://img.shields.io/badge/-HTML5-E34F26?style=flat-square&logo=html5&logoColor=white"/> 
          <img src="https://img.shields.io/badge/-CSS3-1572B6?style=flat-square&logo=css3"/> 
          <img src="https://img.shields.io/badge/-JavaScript-563D7C?style=flat-square&logo=bootstrap"/> 
     </p>

简体中文 | [English](./README.en.md)

</div>

## 📘 项目介绍

**FastCloud** 是FastapiAdmin工程轻量化版本，旨在帮助开发者高效搭建高质量的企业级中后台系统。该项目采用 **前后端分离架构**，融合 Python 后端框架 `FastAPI` 和前端主流框架 `Vue3` 实现多端统一开发，提供了一站式开箱即用的开发体验。

> **设计初心**: 以模块化、松耦合为核心，追求丰富的功能模块、简洁易用的接口、详尽的开发文档和便捷的维护方式。通过统一框架和组件，降低技术选型成本，遵循开发规范和设计模式，构建强大的代码分层模型，搭配完善的本地中文化支持，专为团队和企业开发场景量身定制。

<a id="packaging-philosophy"></a>

## 📐 分包理念：两种组织方式与本项目选择

讨论的是**源码目录如何划分**（文件夹怎么分包），与是否在代码里做 MVC / Controller–Service–CRUD **逻辑分层**不是同一件事：分层可以有，且本项目仍有；差别在于**第一层**是按「业务域」还是按「技术层」切目录。

| 方式 | 组织方式 | 典型目录（示例） |
|------|----------|------------------|
| **按技术层次分包**（package by layer） | 同一类技术文件归在一起 | 顶层 `models/`、`schemas/`、`cruds/`、`services/`、`controllers/` … |
| **按业务特性分包**（package by feature / vertical slice） | 同一业务域的文件归在一起 | 后端 `app/api/v1/module_*/<子域>/` 下并列 `controller.py`、`service.py`、`crud.py`、`model.py`、`schema.py`；可选能力在 `app/plugin/...` |

**本项目（后端）采用：按业务特性分包（竖切）。**

**设计初心（为何这样选）**

- **解耦的单位是业务边界**：以系统管理、监控、各业务子域等为模块，子域内再分文件；多人协作时尽量落在不同子目录，减少无关冲突，而不是所有人改同一套全局 `models/`、`services/`。
- **面向未来的拆分**：若后续要将某一模块独立成子工程、独立仓库或独立发布，**一整块目录**即是一条自然边界；按层分包则往往需要跨多个顶层目录抽取，迁移成本更高。
- **分层仍然存在**：Controller → Service → CRUD → Model / Schema 的**逻辑分层没有消失**，只是**叠在业务包内部**，而不是用「全项目唯一的分层目录」作为第一维划分。

**与按层分包的取舍**：按层分包在「小团队、强调整体浏览某一技术层」时也有其价值；本项目在**优先域解耦、优先多团队按模块并行**的前提下，明确采用**按特性竖切**。若更关注单仓库内一眼扫全表结构，可配合 IDE、数据库工具与 Alembic，而不必为此改为全局 `models/` 单目录。

---

## 🎯 核心优势

| 优势 | 描述 |
| ---- | ---- |
| 🔥 **现代化技术栈** | 基于 FastAPI + Vue3 + TypeScript 等前沿技术构建 |
| ⚡ **高性能异步** | 利用 FastAPI 异步特性和 Redis 缓存优化响应速度 |
| 🔐 **安全可靠** | JWT + OAuth2 认证机制，RBAC 权限控制模型 |
| 🧱 **模块化设计** | 高度解耦的系统架构，便于扩展和维护 |
| 🌐 **全栈支持** | Web端 + 移动端(H5) + 后端一体化解决方案 |
| 🚀 **快速部署** | Docker 一键部署，支持生产环境快速上线 |
| 📖 **完善文档** | 详细的开发文档和教程，降低学习成本 |
| 🤖 **智能体框架** | 基于Agno的开发智能体 |

## 🍪 演示环境

- 💻 网页端：[https://service.fastapiadmin.com/web](https://service.fastapiadmin.com/web)
- 📱 移动端：[https://service.fastapiadmin.com/app](https://service.fastapiadmin.com/app)
- 👤 登录账号：`admin` 密码：`123456`


## 📦 工程结构概览

```sh
FastapiAdmin
├─ backend               # 后端工程 (FastAPI + Python)
├─ frontend              # Web前端工程 (Vue3 + Element Plus)
├─ LICENSE               # 开源协议
|─ README.en.md          # 英文文档
└─ README.md             # 中文文档
```

## 🔧 模块展示

### web 端

| 模块名 <div style="width:60px"/> | 截图 |
| ----- | --- |
| 仪表盘   | ![仪表盘](backend/data/dashboard.png) |
| 代码生成  | ![代码生成](backend/data/gencode.png) |
| 智能助手  | ![智能助手](backend/data/ai.png) |


## 🚀 快速开始

### 环境要求

| 类型 | 技术栈 | 版本 |
|------|--------|------|
| 后端 | Python | ≥ 3.10（推荐 3.12） |
| 后端 | FastAPI | 0.109+ |
| 前端 | Node.js | ≥ 20.0 |
| 前端 | Vue3 | 3.3+ |
| 数据库 |  SQLite | 见 `backend/env` 配置 |

### 获取代码

```bash
# 克隆代码到本地
git clone https://gitee.com/fastapiadmin/FastCloud.git
# 或者
git clone https://github.com/fastapiadmin/FastCloud.git
```

### 后端启动

#### 使用 uv（推荐，与 `backend/pyproject.toml` 一致）

```bash
cd backend
uv sync
# 启动
uv run main.py run
```

#### 使用传统 pip / venv

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py run
```

### 前端端启动

#### 使用pnpm或npm

```bash
cd frontend
pnpm install
# 启动
pnpm dev
# 构建生产版本
pnpm build
```

## ℹ️ 帮助

更多详情请查看 [官方文档](https://service.fastapiadmin.com)

## 👥 贡献者

<a href="https://github.com/fastapiadmin/FastCloud/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=fastapiadmin/FastapiAdmin"/>
</a>

## 🙏 特别鸣谢

感谢以下开源项目的贡献和支持：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Vue3](https://cn.vuejs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://github.com/vitejs/vite)
- [Element Plus](https://element-plus.org/)

## 🎨 社区交流

| 群组二维码 | 微信支付二维码 |
| --- | --- |
| ![群组二维码](backend/data/group.jpg) | ![微信支付二维码](backend/data/wechatPay.jpg) |

## ❤️ 支持项目

如果你喜欢这个项目，请给我一个 ⭐️ Star 支持一下吧！非常感谢！

[![Stargazers over time](https://starchart.cc/fastapiadmin/FastCloud.svg?variant=adaptive)](https://starchart.cc/fastapiadmin/FastCloud)
