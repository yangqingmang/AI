# 🧠 Enterprise Brain (RAG System)

> **定位**：企业级 RAG 知识库解决方案，支持私有化部署、模型热切换与高并发检索。
> **核心优势**：架构解耦、语义缓存、一键交付。

---

## 🏗 系统架构 (v1.2)

本项目采用 **Client/Server 分离架构**，支持水平扩展与组件热插拔。

| 组件 | 技术栈 | 说明 |
| :--- | :--- | :--- |
| **LLM Engine** | `LangChain` + `OpenAI SDK` | 支持 DeepSeek、ChatGPT、vLLM (Llama3/Qwen) 等任意兼容模型。 |
| **Embedding** | `all-MiniLM-L6-v2` | 本地 CPU 推理，数据不出内网。 |
| **Vector DB** | `ChromaDB` (Server Mode) | 独立容器部署，支持持久化与并发读写。可通过配置切换至 `Pgvector`。 |
| **Caching** | `Semantic Cache` (Chroma) | 基于向量相似度的意图缓存，大幅降低 Token 消耗与延迟。 |
| **Frontend** | `Streamlit` | 交互式 Web 界面，支持文件上传与多轮对话。 |

---

## 🚀 快速部署 (ToB Delivery)

### 1. 环境准备
确保服务器已安装 `Docker` 和 `Docker Compose`。

### 2. 配置 (关键一步)
复制模板并填入你的 Key 或内网模型地址。

```bash
cp .env.example .env
vi .env
```

**配置项说明：**
```ini
# --- 模型配置 ---
DEEPSEEK_API_KEY=sk-xxxxxx          # 或是 "empty" (如果是本地无鉴权模型)
DEEPSEEK_BASE_URL=https://api.deepseek.com  # 或 http://192.168.1.10:8000/v1
LLM_MODEL_NAME=deepseek-chat        # 或 custom-qwen-72b

# --- 数据库配置 ---
VECTOR_STORE_TYPE=chroma            # 可选: chroma, pgvector
CHROMA_SERVER_HOST=chroma-server    # Docker 服务名
CHROMA_SERVER_PORT=8000
```

### 3. 一键启动
使用我们提供的自动化脚本（支持 Linux/Windows WSL）：

```bash
bash deploy.sh
```

或者手动启动：
```bash
docker-compose up -d --build
```

访问地址：`http://localhost:8501`

---

## 🛠 开发指南

### 本地调试 (Local Development)
由于代码已升级为 **Client/Server 架构**，在本地不使用 Docker 运行时，**必须**手动启动一个 ChromaDB 服务端。

1.  **启动向量数据库 (Terminal 1)**：
    ```powershell
    # 激活虚拟环境后运行
    chroma run --path ./chroma_db --port 8000
    ```
    *保持此窗口开启，不要关闭。*

2.  **启动 Web 应用 (Terminal 2)**：
    ```powershell
    # 确保 .env 中 CHROMA_SERVER_HOST=localhost
    streamlit run src/app.py
    ```

### 架构升级
详见 [docs/ENTERPRISE_GUIDE.md](docs/ENTERPRISE_GUIDE.md)，包含：
*   如何切换到 **PostgreSQL (pgvector)** 以支持千万级数据。
*   如何集成 **GPTCache** 实现更高级的缓存策略。

---

## 📂 目录结构

```text
enterprise-brain/
├── src/
│   ├── app.py          # Web 主程序 (含语义缓存逻辑)
│   ├── ingest.py       # 数据清洗与入库 (Client 端)
│   ├── query.py        # 命令行测试工具
│   └── db_factory.py   # [核心] 数据库工厂模式实现
├── docs/               # 架构文档与升级指南
├── data/               # 知识库源文件 (Markdown/TXT)
├── deploy.sh           # 客户服务器一键部署脚本
├── package.sh          # 交付包打包脚本
└── docker-compose.yml  # 容器编排配置
```

## 🛡 安全声明
*   **API Key 安全**：所有 Key 均通过环境变量注入，不硬编码在代码中。
*   **数据隐私**：默认 Embedding 模型完全本地运行，知识库数据仅存储在私有 `chroma_db/` 卷中。
