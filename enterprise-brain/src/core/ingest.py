import os
import glob
import hashlib
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from src.config.settings import get_settings
from src.core.db import DBFactory
from src.core.llm import get_embeddings
from src.core.retriever import reset_bm25_cache

settings = get_settings()

def calculate_file_hash(filepath):
    """计算文件的 MD5 哈希值"""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return ""

def ingest_docs(progress_callback=None):
    """
    全量同步 data/ 目录到 ChromaDB
    progress_callback: 用于 Streamlit 显示进度的回调函数 func(text)
    """
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log("🔌 Connecting to ChromaDB Server...")
    try:
        client = DBFactory.get_client()
        collection = client.get_or_create_collection(name=settings.COLLECTION_NAME)
    except Exception as e:
        log(f"❌ Could not connect to ChromaDB: {e}")
        return

    # --- 1. 获取数据库现有状态 ---
    log("🔍 Scanning database state...")
    existing_data = collection.get(include=["metadatas"])
    
    db_state = {} 
    
    if existing_data and existing_data["ids"]:
        for i, doc_id in enumerate(existing_data["ids"]):
            meta = existing_data["metadatas"][i]
            if not meta: continue
            
            source = meta.get("source")
            if not source: continue
            
            norm_source = os.path.normpath(source)
            
            if norm_source not in db_state:
                db_state[norm_source] = {"ids": [], "hash": meta.get("file_hash", "")}
            db_state[norm_source]["ids"].append(doc_id)

    # --- 2. 获取本地文件状态 ---
    # 支持 txt, md, pdf
    patterns = ["**/*.md", "**/*.txt", "**/*.pdf"]
    local_files = []
    for p in patterns:
        local_files.extend(glob.glob(os.path.join(settings.DATA_DIR, p), recursive=True))
    
    local_state = {} 
    for f in local_files:
        norm_path = os.path.normpath(f)
        local_state[norm_path] = calculate_file_hash(norm_path)

    log(f"📂 Local folder contains {len(local_state)} files.")

    # --- 3. 计算差异 ---
    to_add = []      
    to_update = []   
    to_delete = []   

    for f_path, f_hash in local_state.items():
        if f_path not in db_state:
            to_add.append((f_path, f_hash))
        else:
            db_info = db_state[f_path]
            if db_info["hash"] != f_hash:
                to_update.append((f_path, f_hash, db_info["ids"]))

    for db_path, info in db_state.items():
        if db_path not in local_state:
            to_delete.append((db_path, info["ids"]))

    log(f"📊 Sync Plan: +{len(to_add)} | ~{len(to_update)} | -{len(to_delete)}")

    if not to_add and not to_update and not to_delete:
        log("✅ Knowledge Base is up to date.")
        return

    # --- 4. 执行同步 ---
    ids_to_remove = []
    for item in to_delete:
        ids_to_remove.extend(item[1])
    for item in to_update:
        ids_to_remove.extend(item[2])
        
    if ids_to_remove:
        batch_size = 5000 
        for i in range(0, len(ids_to_remove), batch_size):
            batch = ids_to_remove[i:i+batch_size]
            log(f"   🗑️ Deleting {len(batch)} old chunks...")
            collection.delete(ids=batch)

    files_to_process = [x[0] for x in to_add] + [x[0] for x in to_update]
    
    if not files_to_process:
        log("✅ Sync complete (Only deletions performed).")
        return

    # 加载并切分
    documents = []
    for f in files_to_process:
        try:
            ext = os.path.splitext(f)[1].lower()
            if ext == '.pdf':
                loader = PyPDFLoader(f)
            else:
                loader = TextLoader(f, encoding='utf-8')
                
            docs = loader.load()
            current_hash = local_state[f]

            for doc in docs:
                doc.metadata["source"] = f
                doc.metadata["filename"] = os.path.basename(f)
                doc.metadata["file_hash"] = current_hash
            documents.extend(docs)
            log(f"   - Loaded: {os.path.basename(f)}")
        except Exception as e:
            log(f"   ❌ Failed to load {f}: {e}")

    if documents:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        log("🧠 Initializing embeddings...")
        embeddings = get_embeddings()
        
        vector_store = DBFactory.get_vector_store(embeddings)
        
        batch_size = 100
        total_chunks = len(chunks)
        log(f"💾 Ingesting {total_chunks} chunks...")
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i+batch_size]
            vector_store.add_documents(batch)
            log(f"      ...ingested {min(i+batch_size, total_chunks)}/{total_chunks}")

    # Reset BM25 Cache to reflect new data
    reset_bm25_cache()
    log("✅ Sync complete!")

if __name__ == "__main__":
    # 简单的命令行调用
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ingest_docs()
