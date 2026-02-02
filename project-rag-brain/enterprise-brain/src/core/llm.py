from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from src.config.settings import get_settings

settings = get_settings()

def get_llm():
    return ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        temperature=settings.TEMPERATURE,
        streaming=True
    )

def get_embeddings():
    # Set HuggingFace endpoint for China
    import os
    os.environ["HF_ENDPOINT"] = settings.HF_ENDPOINT
    
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
