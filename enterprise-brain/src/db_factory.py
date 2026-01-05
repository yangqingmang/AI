import os
from langchain_huggingface import HuggingFaceEmbeddings
# 按需导入，避免未安装依赖时报错
try:
    from langchain_chroma import Chroma
    import chromadb
except ImportError:
    Chroma = None

try:
    from langchain_postgres import PGVector
except ImportError:
    PGVector = None

class DBFactory:
    @staticmethod
    def get_vector_store(embeddings):
        """
        根据环境变量 VECTOR_STORE_TYPE 返回对应的 VectorStore 实例
        """
        store_type = os.getenv("VECTOR_STORE_TYPE", "chroma").lower()
        collection_name = "enterprise_docs"

        if store_type == "chroma":
            if not Chroma:
                raise ImportError("langchain-chroma not installed.")
            
            # 连接独立服务
            client = chromadb.HttpClient(
                host=os.getenv("CHROMA_SERVER_HOST", "localhost"),
                port=os.getenv("CHROMA_SERVER_PORT", "8000")
            )
            return Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=embeddings
            )

        elif store_type == "pgvector":
            if not PGVector:
                raise ImportError("langchain-postgres not installed. Please pip install it.")
            
            # 构造 PG 连接串
            # 格式: postgresql+psycopg2://user:pass@host:port/db
            connection = f"postgresql+psycopg2://{os.getenv('PG_USER', 'admin')}:{os.getenv('PG_PASS', 'password')}@{os.getenv('PG_HOST', 'localhost')}:{os.getenv('PG_PORT', '5432')}/{os.getenv('PG_DB', 'vector_db')}"
            
            return PGVector(
                embeddings=embeddings,
                collection_name=collection_name,
                connection=connection,
                use_jsonb=True,
            )

        else:
            raise ValueError(f"Unsupported VECTOR_STORE_TYPE: {store_type}")

    @staticmethod
    def get_cache_collection(embeddings):
        """
        获取语义缓存的 Collection (目前仅支持 Chroma 实现)
        未来可扩展为 Redis 或 GPTCache
        """
        # 简单起见，缓存依然默认用 Chroma，即使主库用了 PG
        # 生产环境建议这里也做抽象
        client = chromadb.HttpClient(
            host=os.getenv("CHROMA_SERVER_HOST", "localhost"),
            port=os.getenv("CHROMA_SERVER_PORT", "8000")
        )
        return client.get_or_create_collection(
            name="semantic_cache",
            metadata={"description": "Cache for RAG responses"}
        )
