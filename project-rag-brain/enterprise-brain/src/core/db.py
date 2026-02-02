import chromadb
from langchain_chroma import Chroma
from src.config.settings import get_settings

settings = get_settings()

class DBFactory:
    @staticmethod
    def get_client():
        return chromadb.HttpClient(
            host=settings.CHROMA_SERVER_HOST,
            port=settings.CHROMA_SERVER_PORT
        )

    @staticmethod
    def get_vector_store(embeddings):
        client = DBFactory.get_client()
        return Chroma(
            client=client,
            collection_name=settings.COLLECTION_NAME,
            embedding_function=embeddings,
        )

    @staticmethod
    def get_cache_collection(embeddings):
        # Cache usually uses raw chromadb collection for simple query
        client = DBFactory.get_client()
        return client.get_or_create_collection(
            name=settings.CACHE_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
