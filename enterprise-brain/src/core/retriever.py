from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List
from src.config.settings import get_settings
from src.core.db import DBFactory
from src.core.kb_interface import get_kb_client, RAGFlowKnowledgeBase

# Local mode imports
import os
import glob
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

settings = get_settings()

_bm25_retriever_cache = None

# --- Local Helper Functions ---
def load_all_docs():
    """Load and split all documents from the data directory for BM25 (Local Mode)."""
    patterns = ["**/*.md", "**/*.txt", "**/*.pdf"]
    documents = []
    
    if not os.path.exists(settings.DATA_DIR):
        return []

    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(settings.DATA_DIR, p), recursive=True))

    for f in files:
        try:
            ext = os.path.splitext(f)[1].lower()
            if ext == '.pdf':
                loader = PyPDFLoader(f)
            else:
                loader = TextLoader(f, encoding='utf-8')
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {f} for BM25: {e}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

# --- Wrapper for Unified Interface ---
class UnifiedRetriever(BaseRetriever):
    """
    A LangChain-compatible retriever that delegates to either 
    Local KB or RAGFlow based on settings.
    """
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        
        kb = get_kb_client()
        
        # If using RAGFlow, call it directly
        if isinstance(kb, RAGFlowKnowledgeBase):
            results = kb.retrieve(query, k=5)
            documents = []
            for item in results:
                documents.append(Document(
                    page_content=item.get("content", ""),
                    metadata={
                        "source": item.get("source"),
                        "score": item.get("score")
                    }
                ))
            return documents
            
        # If using Local, we shouldn't really be here via this wrapper for efficiency, 
        # but as a fallback/simplification:
        return []

def get_retriever(embeddings):
    """
    Factory function to return the correct LangChain retriever.
    """
    global _bm25_retriever_cache
    
    # 1. Check Mode
    if settings.RAG_ENGINE == "ragflow":
        return UnifiedRetriever()

    # 2. Local Mode: Build Ensemble (Vector + BM25)
    vector_store = DBFactory.get_vector_store(embeddings)
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    if _bm25_retriever_cache is None:
        docs = load_all_docs()
        if docs:
            _bm25_retriever_cache = BM25Retriever.from_documents(docs)
            _bm25_retriever_cache.k = 3
        else:
            return vector_retriever

    ensemble_retriever = EnsembleRetriever(
        retrievers=[_bm25_retriever_cache, vector_retriever],
        weights=[0.4, 0.6]
    )
    
    return ensemble_retriever

def reset_bm25_cache():
    """Call this after ingestion to force reload BM25 index."""
    global _bm25_retriever_cache
    _bm25_retriever_cache = None
