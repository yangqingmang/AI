import os
import glob
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config.settings import get_settings
from src.core.db import DBFactory

settings = get_settings()

_bm25_retriever_cache = None

def load_all_docs():
    """Load and split all documents from the data directory for BM25."""
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

def get_retriever(embeddings):
    """
    Returns an EnsembleRetriever combining BM25 (Keyword) and Chroma (Semantic).
    """
    global _bm25_retriever_cache
    
    # 1. Vector Retriever
    vector_store = DBFactory.get_vector_store(embeddings)
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # 2. BM25 Retriever
    # In a real app, we should persist this index or update it incrementally.
    # Here we lazy load it.
    if _bm25_retriever_cache is None:
        docs = load_all_docs()
        if docs:
            _bm25_retriever_cache = BM25Retriever.from_documents(docs)
            _bm25_retriever_cache.k = 3
        else:
            # Fallback if no docs found
            return vector_retriever

    # 3. Ensemble
    ensemble_retriever = EnsembleRetriever(
        retrievers=[_bm25_retriever_cache, vector_retriever],
        weights=[0.4, 0.6] # Adjust weights: 0.4 for keyword, 0.6 for semantic
    )
    
    return ensemble_retriever

def reset_bm25_cache():
    """Call this after ingestion to force reload BM25 index."""
    global _bm25_retriever_cache
    _bm25_retriever_cache = None
