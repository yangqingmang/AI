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

def ingest_docs():
    print(f"📂 Loading documents from {DATA_DIR}...")
    
    # 1. 扫描所有 .md 和 .MD 文件
    files = glob.glob(os.path.join(DATA_DIR, "*.md")) + glob.glob(os.path.join(DATA_DIR, "*.MD"))
    
    if not files:
        print("❌ No markdown files found!")
        return

    documents = []
    for f in files:
        try:
            loader = TextLoader(f, encoding='utf-8')
            documents.extend(loader.load())
            print(f"   - Loaded: {f}")
        except Exception as e:
            print(f"   ❌ Failed to load {f}: {e}")

    # 2. 文本分块 (Chunking)
    # 对于 RAG，1000 字符左右的块通常效果较好，overlap 用于保持上下文连贯
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️  Split into {len(chunks)} chunks.")

    # 3. 初始化 Embedding 模型 (本地运行，无需 API Key)
    # all-MiniLM-L6-v2 是目前最流行的轻量级 RAG 模型
    print("🧠 Initializing embedding model (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. 向量化并入库 (ChromaDB)
    print(f"💾 Saving to vector store at {DB_DIR}...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print("✅ Ingestion complete! The Brain is ready.")

if __name__ == "__main__":
    ingest_docs()
