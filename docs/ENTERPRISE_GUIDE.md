# 🏗️ 企业级架构升级指南 (Enterprise Upgrade Guide)

> **适用场景**：当客户对**并发性能**（>1000 QPS）、**数据规模**（>100万向量）或**运维标准**（要求统一数据库）有严格要求时，请参照本指南进行架构升级。

---

## 🚀 场景一：升级语义缓存 (GPTCache)

**背景**：目前的 `app.py` 使用的是简单的 Chroma 向量匹配。当需要更复杂的缓存淘汰策略（如 LRU/LFU）、更精准的相似度评估（Re-ranking）或多节点共享缓存时，应切换到业界标准库 **GPTCache**。

### 1. 安装依赖
```bash
pip install gptcache
```

### 2. 代码改造 (`src/app.py`)

**原代码 (DIY 缓存)**:
```python
# 手动计算向量并查询 Chroma
prompt_vector = embeddings.embed_query(prompt)
cache_results = cache_collection.query(...)
```

**升级代码 (GPTCache)**:
```python
from gptcache import cache
from gptcache.adapter.langchain_models import LangChainLLMs
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

# 1. 初始化 GPTCache (只需一次)
onnx = Onnx()
data_manager = get_data_manager(CacheBase("sqlite"), VectorBase("faiss", dimension=384))
cache.init(
    pre_embedding_func=lambda x: x, # 预处理
    embedding_func=onnx.to_embeddings, # 向量化
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(),
)

# 2. 包装 LLM
# 这一步最关键：LangChainLLMs 会自动拦截请求，先查缓存，再调大模型
llm = LangChainLLMs(llm=original_llm)

# 3. 正常调用 (业务逻辑完全不用变)
chain = prompt_template | llm 
response = chain.invoke(...)
```

---

## 🐘 场景二：切换向量存储 (Pgvector)

**背景**：客户 IT 部门不想维护 ChromaDB，或者数据量级达到千万级，或者需要结合 SQL 做复杂的元数据关联查询（例如：`WHERE date > '2024-01-01' AND department = 'IT'`）。此时，**PostgreSQL (pgvector)** 是最佳选择。

### 1. 基础设施升级 (`docker-compose.yml`)

替换 `chroma-server` 服务：

```yaml
services:
  # 移除 chroma-server，新增 postgres
  db:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=vector_db
    volumes:
      - ./pg_data:/var/lib/postgresql/data
```

### 2. 安装依赖
```bash
pip install langchain-postgres psycopg2-binary
```

### 3. 代码改造 (`src/ingest.py` & `src/app.py`)

**原代码 (Chroma)**:
```python
from langchain_chroma import Chroma

vector_store = Chroma(
    client=client,
    collection_name="enterprise_docs",
    embedding_function=embeddings
)
```

**升级代码 (Pgvector)**:
```python
from langchain_postgres import PGVector

# 连接字符串
CONNECTION_STRING = "postgresql+psycopg2://admin:secure_password@db:5432/vector_db"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="enterprise_docs",
    connection=CONNECTION_STRING,
    use_jsonb=True,
)
```

---

## 📊 选型决策表 (Cheat Sheet)

| 维度 | 方案 A: Chroma (当前) | 方案 B: Pgvector (升级) | 方案 C: Milvus (顶配) |
| :--- | :--- | :--- | :--- |
| **数据量级** | < 100 万 | < 1000 万 | > 1000 万 |
| **运维难度** | ⭐ (开箱即用) | ⭐⭐ (需维护 PG) | ⭐⭐⭐ (复杂集群) |
| **元数据查询** | 弱 (基本过滤) | **强 (SQL 混合查询)** | 强 (标量索引) |
| **适用客户** | 创业公司、部门级应用 | **银行、传统国企** | 互联网巨头 |

