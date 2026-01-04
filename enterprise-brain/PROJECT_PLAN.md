# Enterprise Brain - 企业级 RAG 知识库引擎项目规划

## 1. 项目愿景 (Vision)
构建一个通用的、模块化的 **RAG (检索增强生成)** 知识库引擎，旨在帮助企业将非结构化数据（PDF、文档、报表）转化为可交互的智能问答服务。
该项目不仅作为技术转型（35+ 高级研发切入 AI）的实战演练，更致力于沉淀为一套可复用的**企业级 AI 解决方案脚手架 (Boilerplate)**。

## 2. 总体架构 (Architecture)

采用 **"Python 后端 (核心 AI 逻辑) + 动静分离"** 的架构设计，确保工程化落地能力。

```mermaid
graph TD
    User[用户/客户端] --> |HTTP Request| API_Gateway[FastAPI 服务层]
    
    subgraph "Python Core (AI Engine)"
        API_Gateway --> Ingestion[数据摄入管道]
        API_Gateway --> Retrieval[检索模块]
        API_Gateway --> Generation[生成模块]
        
        Ingestion --> |1. 解析 & 切片| Chunker[文本切片器]
        Chunker --> |2. Embedding| EmbedModel[嵌入模型 (OpenAI/HuggingFace)]
        EmbedModel --> |3. 存储| VectorDB[(ChromaDB 向量库)]
        
        Retrieval --> |4. 语义搜索| VectorDB
        Retrieval --> |5. 重排序 (Rerank)| Reranker[重排序模型]
        
        Generation --> |6. 组装 Prompt| ContextWindow[上下文窗口]
        ContextWindow --> |7. 推理| LLM[大语言模型 (DeepSeek/GPT-4)]
    end
    
    subgraph "Infrastructure"
        Config[配置管理 (.env)]
        Logs[日志监控]
    end
```

## 3. 技术栈选型 (Tech Stack)

| 模块 | 技术选型 | 理由 |
| :--- | :--- | :--- |
| **语言** | **Python 3.10+** | AI 领域一等公民，生态最丰富，数据处理能力强。 |
| **Web 框架** | **FastAPI** | 高性能异步框架，原生支持 Swagger 文档，适合 IO 密集型 AI 任务。 |
| **编排框架** | **LangChain** | 业界标准编排库，组件丰富，适合快速构建 Pipeline。 |
| **LLM 模型** | **OpenAI (GPT-4o) / DeepSeek-V3** | DeepSeek 性价比极高，适合开发测试；GPT-4o 用于生产兜底。 |
| **Embedding** | **text-embedding-3-small** | OpenAI 提供的高性价比嵌入模型。 |
| **向量数据库** | **ChromaDB** | 本地轻量级向量库，无需 Docker 即可运行，部署简单。 |
| **文档解析** | **PyPDF / Unstructured** | 处理 PDF、Markdown、Excel 等非结构化数据的核心库。 |
| **包管理** | **Pip + venv** (初期) / **Poetry** (后期) | 初期保持简单，后期引入 Poetry 进行严格版本控制。 |
| **前端交互** | **Streamlit** (MVP) / **Next.js** (Prod) | Streamlit 用于快速验证；Next.js 用于生产级交互。 |

## 4. 实施路线图 (Roadmap)

### 阶段一：MVP 原型 (Core Logic)
**目标**：跑通“文档 -> 向量 -> 问答”的最小闭环，无 API，纯 CLI 脚本。
- [ ] **环境搭建**：初始化 Python 虚拟环境，配置 `.gitignore`, `.env`。
- [ ] **数据清洗 (ETL)**：编写脚本加载本地 PDF/Markdown 文件。
- [ ] **切片策略 (Chunking)**：实现基于 Tokens 的文本切片 (RecursiveCharacterTextSplitter)。
- [ ] **向量化 (Indexing)**：调用 Embedding API 将数据存入 ChromaDB。
- [ ] **检索验证 (Retrieval)**：在控制台输入问题，验证召回的文档片段是否准确。
- [ ] **生成回答 (Generation)**：结合 Context 和 Prompt，让 LLM 生成最终答案。

### 阶段二：服务化与工程化 (API & Server)
**目标**：将脚本封装为 RESTful Web 服务，支持文件上传与流式响应。
- [ ] **API 骨架**：初始化 FastAPI 项目，定义 Pydantic 数据模型。
- [ ] **文件上传接口**：实现 `POST /upload`，后台异步处理文档解析与入库。
- [ ] **问答接口**：实现 `POST /chat`，连接核心 RAG 逻辑。
- [ ] **流式响应 (Streaming)**：实现 Server-Sent Events (SSE)，提升用户体验。
- [ ] **异步处理**：利用 `BackgroundTasks` 优化大文件处理流程。

### 阶段三：前端交互与体验 (Frontend)
**目标**：提供可视化界面，完成从“代码”到“产品”的跨越。
- [ ] **UI 原型**：使用 Streamlit 快速搭建聊天窗口与文件上传面板。
- [ ] **引用溯源**：在 UI 上展示 AI 回答所引用的原文片段（Source Citation）。
- [ ] **参数调试**：在前端提供调节 Temperature、Chunk Size 的滑块（Debug 模式）。

### 阶段四：高级特性迭代 (Advanced)
**目标**：解决复杂场景问题，提升准确率与鲁棒性。
- [ ] **混合检索 (Hybrid Search)**：引入 BM25 关键词检索，结合向量检索提升准确度。
- [ ] **多轮对话记忆**：引入 Redis/Postgres 存储 History，支持上下文追问。
- [ ] **Prompt 优化**：针对特定业务场景（合同、代码、财报）定制 System Prompt。
- [ ] **Agent 能力**：(可选) 引入 Tool Calling，允许 AI 调用外部搜索或计算器。

## 5. 项目结构规范 (Project Structure)

```text
enterprise-brain/
├── data/               # 存放原始文档 (本地测试用)
├── src/
│   ├── core/           # RAG 核心逻辑 (LLM, Embedding, VectorStore)
│   ├── api/            # FastAPI 路由与控制器
│   ├── utils/          # 工具函数 (PDF解析, 文本处理)
│   └── config.py       # 配置管理
├── tests/              # 单元测试
├── .env                # 环境变量 (API Keys)
├── main.py             # 程序入口
├── requirements.txt    # 依赖列表
└── PROJECT_PLAN.md     # 本规划文件
```

---
*Last Updated: 2025-12-31*
