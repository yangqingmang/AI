from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Enterprise Brain"
    APP_VERSION: str = "1.2.0"
    
    # LLM Config
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL_NAME: str = "deepseek-chat"
    TEMPERATURE: float = 0.1
    
    # Vector DB Config
    CHROMA_SERVER_HOST: str = "chroma-server"
    CHROMA_SERVER_PORT: int = 8000
    COLLECTION_NAME: str = "enterprise_knowledge"
    CACHE_COLLECTION_NAME: str = "llm_cache"

    # RAG Engine Config (Local vs RAGFlow)
    RAG_ENGINE: str = "local"  # Options: "local", "ragflow"
    RAGFLOW_BASE_URL: str = "http://localhost:9380"
    RAGFLOW_API_KEY: str = "ragflow-x-api-key"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    HF_ENDPOINT: str = "https://hf-mirror.com"  # For China access

    # Paths
    # 获取当前文件(src/config/settings.py)的上两级目录作为 src 根
    # 再上一级作为项目根
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"  # 忽略多余的环境变量

@lru_cache()
def get_settings():
    return Settings()
