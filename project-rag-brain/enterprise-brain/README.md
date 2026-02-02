# 🧠 Enterprise Brain (RAG System)

> **定位**：基于 LangChain + DeepSeek + 本地 Embedding 的企业级知识库原型。
> **目标**：实现对私有文档（Markdown/PDF）的精准语义检索与智能问答。

---

## 🏗 项目架构

- **LLM**: DeepSeek-V3 (via OpenAI SDK)
- **Embedding**: `all-MiniLM-L6-v2` (Running locally on CPU)
- **Vector DB**: ChromaDB (Local persistence)
- **Orchestration**: LangChain
- **Frontend**: Streamlit

---

## 📂 目录结构

```text
enterprise-brain/
├── src/
│   ├── app.py          # Streamlit Web 界面
│   ├── ingest.py       # 数据入库与向量化脚本
│   └── query.py        # 命令行查询工具
├── tests/
│   └── test_api.py     # API 连通性测试
├── data/               # 存放原始 Markdown 文档
├── chroma_db/          # 向量数据库持久化文件
├── .env                # API 密钥配置 (已 Git 忽略)
└── .venv/              # Python 虚拟环境
```

---

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 3.10+。

```powershell
# 进入项目目录
cd enterprise-brain

# 创建并激活虚拟环境
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key
在 `enterprise-brain/.env` 文件中填入你的 Key：
```text
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 3. 数据入库 (Ingestion)
将你的 `.md` 或 `.pdf` 文件放入 `data/` 目录，然后运行：
```powershell
python src/ingest.py
```

### 4. 启动 Web 界面
```powershell
streamlit run src/app.py
```

---

## 🛠 开发进阶

- **命令行测试**：
  `python src/query.py "你的问题"`
- **调优建议**：
  - 修改 `src/ingest.py` 中的 `chunk_size` 和 `chunk_overlap` 以适应不同长度的文档。
  - 在 `src/app.py` 中调整 `temperature` 参数（0.1 适合事实问答，0.7 适合创意写作）。

---

## 🛡 安全声明
- `.env` 文件已加入 `.gitignore`，请勿将其提交至任何公共仓库。
- 建议定期备份 `chroma_db/` 目录。
