# 🧠 Enterprise Brain (Agentic RAG System)

> **定位**：企业级自主智能体解决方案。不仅是知识库，更是具备**联网搜索、代码执行、文件管理**能力的 AI 员工。
> **核心优势**：架构解耦、语义缓存、多模态工具链。

---

## 🌟 核心特性 (v1.3)

### 1. 双模态引擎 (Dual Mode)
*   **🌱 Free Mode (纯 RAG)**：专注内部知识库问答，安全、可控。
*   **🚀 Pro Mode (Agent)**：解锁自主能力，AI 可自动判断是查库、搜网、还是写代码分析数据。

### 2. 角色分离 (Multi-Page UI)
*   **用户端 (`App`)**：极简聊天界面，无干扰。
*   **管理端 (`Admin`)**：独立后台，负责文件上传、索引重建、系统维护。

### 3. 企业级架构
*   **Client/Server**：向量库独立容器化，支持水平扩展。
*   **Semantic Cache**：基于向量相似度的意图缓存，响应速度提升 100 倍。
*   **Model Agnostic**：支持 DeepSeek, OpenAI, vLLM 等任意兼容模型热切换。

---

## 🚀 快速部署

### 1. 环境准备
确保服务器已安装 `Docker` 和 `Docker Compose`。

### 2. 配置
```bash
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 3. 启动
使用自动化脚本（自动处理后台服务与前台应用）：

*   **Windows**: 双击 `run_local.bat` 或运行 `.\run_local.ps1`
*   **Linux/Mac**: 运行 `bash run_local.sh`
*   **Docker 生产部署**: `bash deploy.sh`

访问地址：`http://localhost:8501`

---

## 📚 使用指南

### 普通用户
直接在主页提问。
*   *示例*：“公司最新的报销政策是什么？”

### 开启 Pro 模式 (Agent)
1.  在左侧边栏勾选 **Enable Pro Mode**。
2.  *示例 1 (联网)*：“搜索一下 DeepSeek 今天的股价新闻。”
3.  *示例 2 (代码)*：“计算 1 到 100 的斐波那契数列总和。”
4.  *示例 3 (文件)*：“把刚才的分析结果保存为 report.txt。”

### 管理员
点击左侧边栏的 **> 箭头**，选择 **Admin** 页面。
*   上传 `.md/.txt` 文档。
*   点击 **Force Re-build Brain** 强制刷新知识库。

---

## 📂 目录结构

```text
enterprise-brain/
├── src/
│   ├── app.py          # [用户端] 聊天主程序 (含 Agent 调度)
│   ├── pages/
│   │   └── Admin.py    # [管理端] 知识库管理
│   ├── tool_factory.py # [工具箱] 搜索、代码、文件工具定义
│   ├── db_factory.py   # [工厂] 数据库连接池
│   └── ingest.py       # [核心] 数据清洗与入库
├── docs/               # 架构升级指南 (GPTCache/Pgvector)
├── data/               # 知识库源文件
└── docker-compose.yml  # 微服务编排
```

## 🛡 安全声明
*   **代码沙箱**：Pro 模式下的 Python 执行器仅用于演示，生产环境建议配合 Docker 隔离或 E2B 沙箱使用。
*   **数据隐私**：默认 Embedding 模型完全本地运行，数据不出内网。