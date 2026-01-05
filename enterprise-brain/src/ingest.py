import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

# 配置路径
DATA_DIR = "data"
DB_DIR = "chroma_db"

import chromadb

def ingest_docs():
    print(f"📂 Loading documents from {DATA_DIR}...")
    
    documents = []
    for f in files:
        try:
            loader = TextLoader(f, encoding='utf-8')
            docs = loader.load()
            # 丰富元数据：添加文件名、文件路径
            for doc in docs:
                doc.metadata["source"] = f
                doc.metadata["filename"] = os.path.basename(f)
            documents.extend(docs)
            print(f"   - Loaded: {f}")
        except Exception as e:
            print(f"   ❌ Failed to load {f}: {e}")

    # 3. 初始化 Embedding 模型
    print("🧠 Initializing embedding model (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. 连接服务器并入库 (Client/Server 模式)
    print(f"💾 Sending vectors to Chroma Server...")
    
    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_SERVER_HOST", "localhost"),
        port=os.getenv("CHROMA_SERVER_PORT", "8000")
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name="enterprise_docs"
    )
    
    print("✅ Ingestion complete! The Brain (Server) is ready.")

if __name__ == "__main__":
    ingest_docs()
