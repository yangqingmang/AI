from abc import ABC, abstractmethod
import requests
import json
from typing import List, Dict, Any
from src.config.settings import get_settings
from src.core.db import DBFactory
from src.core.llm import get_embeddings
from langchain_chroma import Chroma

settings = get_settings()

class KnowledgeBase(ABC):
    """知识库抽象基类"""
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        检索知识
        Returns: List of {"content": str, "source": str, "score": float}
        """
        pass

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """获取知识库状态"""
        pass

class LocalKnowledgeBase(KnowledgeBase):
    """本地模式: 基于 ChromaDB + LangChain"""
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        try:
            embeddings = get_embeddings()
            vector_store = DBFactory.get_vector_store(embeddings)
            
            # 使用相似度搜索
            docs_with_score = vector_store.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_with_score:
                results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("filename", "unknown"),
                    "page": doc.metadata.get("page", 0),
                    "score": float(score) # Chroma distance (lower is better usually, or similarity)
                })
            return results
        except Exception as e:
            print(f"❌ Local KB Search Error: {e}")
            return []

    def status(self) -> Dict[str, Any]:
        return {"engine": "Local (ChromaDB)", "status": "active"}


class RAGFlowKnowledgeBase(KnowledgeBase):
    """企业模式: 对接 RAGFlow API"""
    
    def __init__(self):
        self.base_url = settings.RAGFLOW_BASE_URL
        self.api_key = settings.RAGFLOW_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # RAGFlow API 规范 (假设 v1 接口)
        # 具体 endpoint 需参考 RAGFlow 官方文档
        url = f"{self.base_url}/api/v1/retrieval" 
        payload = {
            "question": query,
            "similarity_threshold": 0.2,
            "top_k": k
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # 适配 RAGFlow 返回格式 -> 统一格式
            results = []
            for item in data.get("data", []):
                results.append({
                    "content": item.get("chunk_content"),
                    "source": item.get("doc_name"),
                    "score": item.get("similarity"),
                    "reference": item
                })
            return results
        except Exception as e:
            print(f"❌ RAGFlow API Error: {e}")
            return []

    def status(self) -> Dict[str, Any]:
        try:
            # 简单的健康检查
            resp = requests.get(f"{self.base_url}/health", timeout=2)
            return {"engine": "RAGFlow", "status": "connected" if resp.status_code == 200 else "error"}
        except:
            return {"engine": "RAGFlow", "status": "disconnected"}

def get_kb_client() -> KnowledgeBase:
    """工厂方法: 获取当前配置的知识库客户端"""
    if settings.RAG_ENGINE == "ragflow":
        return RAGFlowKnowledgeBase()
    else:
        return LocalKnowledgeBase()
