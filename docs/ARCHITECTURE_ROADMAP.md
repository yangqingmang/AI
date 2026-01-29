# Enterprise Brain 技术架构演进路线图 (2026版)

## 1. 现状评估 (Current State - v1.2)

目前系统处于 **MVP (最小可行性产品)** 向 **POC (概念验证)** 过渡的阶段。核心 AI 能力已具备，但基础设施尚显单薄，缺乏企业级所需的稳定性、安全性和多租户能力。

| 维度 | 当前状态 | 评价 | 风险点 |
| :--- | :--- | :--- | :--- |
| **AI 核心** | LangGraph + DeepSeek + ChromaDB | ⭐⭐⭐⭐ (强) | 依赖本地文件解析，复杂文档处理能力受限。 |
| **后端架构** | FastAPI (单体) + SQLite | ⭐⭐ (弱) | 并发能力差，无法横向扩展，数据无持久化保障。 |
| **前端交互** | Streamlit | ⭐⭐ (弱) | 交互受限，无法定制复杂 UI，难以实现精细权限控制。 |
| **基础设施** | Docker Compose (基础) | ⭐⭐⭐ (中) | 缺乏监控、日志聚合和对象存储。 |

---

## 2. 演进路线 (Evolution Roadmap)

### 阶段一：稳固内核 (v1.5 - "Solid Core")
**目标**: 解决“单机依赖”问题，提升数据可靠性和文档解析能力，使其能稳定运行于客户的小型服务器上。

*   **[已完成] 智能解析工厂**: 引入 `AdaptiveLoader`，集成 Microsoft MarkItDown，根据硬件自动切换解析策略。
*   **[已完成] 双引擎架构**: 支持 `RAG_ENGINE` 切换，预埋 RAGFlow 对接能力。
*   **[待执行] 存储升级**:
    *   **SQLite -> PostgreSQL**: 迁移聊天记录、用户元数据到 PG，支持事务和高并发。
    *   **Local FS -> MinIO**: 引入对象存储，所有上传文件通过 MinIO 管理，解耦应用服务器与文件系统。
*   **[待执行] 可观测性基础**:
    *   接入 **Langfuse (Self-hosted)**: 监控 Agent 的 Token 消耗、延迟和 Trace 链路。

### 阶段二：商业交付 (v2.0 - "Enterprise Ready")
**目标**: 满足中大型企业私有化部署需求，具备基本的用户管理和安全隔离能力。

*   **后端重构**:
    *   **Auth 服务**: 引入 OAuth2 / JWT 认证体系。不再是所有人共享一个 Admin 账号。
    *   **多租户隔离**: 在 PG 和 Vector DB 中增加 `tenant_id` 字段，实现数据逻辑隔离。
*   **基础设施增强**:
    *   **Celery / Redis**: 引入异步任务队列。由后台 Worker 异步处理大文件解析，避免阻塞 API 主线程。
    *   **Nginx 网关**: 用于 SSL 终结、负载均衡和静态资源缓存。
*   **前端升级 (可选)**:
    *   如果客户对 UI 要求高，启动 **Vue3 / React** 重构计划，替代 Streamlit。

### 阶段三：云原生平台 (v3.0 - "SaaS Platform")
**目标**: 真正的分布式架构，支持大规模 SaaS 运营或集团级内部部署。

*   **微服务化**: 将 `Ingestion` (解析)、`Retrieval` (检索)、`Chat` (对话) 拆分为独立微服务。
*   **Kubernetes (K8s) 编排**: 编写 Helm Chart，支持在 K8s 集群中一键拉起整套环境。
*   **全面 RAGFlow 化**: 彻底废弃本地解析代码，全量对接 RAGFlow 集群，利用其 ElasticSearch + Infinity 组合实现亿级文档检索。

---

## 3. 关键技术债清单 (Tech Debt Backlog)

| 优先级 | 任务 | 描述 | 解决建议 |
| :--- | :--- | :--- | :--- |
| **P0** | **引入 MinIO** | 当前文件直接存 `data/` 目录，容器重启或迁移时数据极易丢失。 | 在 `docker-compose` 中添加 MinIO 服务，并重写 `files.py` 工具。 |
| **P0** | **引入 PostgreSQL** | SQLite 不支持并发写入，且无法与其它服务共享数据。 | 替换 SQLite，使用 SQLAlchemy 连接 PG。 |
| **P1** | **异步解析** | 当前上传大文件时，API 会 hang 住直到解析完成。 | 引入 `Celery` + `Redis`，上传后立即返回 Task ID，前端轮询进度。 |
| **P1** | **Langfuse 监控** | 目前无法知道 AI 为什么回答错误，无法评估 Token 成本。 | 部署 Langfuse 容器，通过 Decorator 接入 Agent 代码。 |
| **P2** | **前端分离** | Streamlit 每次交互都重跑脚本，性能差，体验卡顿。 | 启动 Next.js 项目，逐步迁移核心 Chat 功能。 |

---

## 4. 架构对比总结

| 特性 | **Current (v1.2)** | **Target (v2.0)** |
| :--- | :--- | :--- |
| **User Identity** | Single User / Basic Auth | **RBAC (Role-Based Access Control)** |
| **Data Storage** | Local Disk + SQLite | **MinIO (S3) + PostgreSQL** |
| **Task Processing**| Synchronous (Blocking) | **Asynchronous (Celery/Redis)** |
| **Observability** | Console Logs | **Langfuse Tracing** |
| **Parsing** | Local Scripts | **Adaptive (Local/Cloud/RAGFlow)** |
