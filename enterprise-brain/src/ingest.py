import os
import glob
import hashlib
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import chromadb

# 加载环境变量
load_dotenv()

DATA_DIR = "data"
COLLECTION_NAME = "enterprise_docs"

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

def ingest_docs():
    """
    全量同步 data/ 目录到 ChromaDB：
    1. 新增：新文件入库
    2. 更新：文件内容变化，重新入库 (删旧增新)
    3. 删除：文件被删，库中也删除
    """
    print("🔌 Connecting to ChromaDB Server...")
    try:
        client = chromadb.HttpClient(
            host=os.getenv("CHROMA_SERVER_HOST", "localhost"),
            port=os.getenv("CHROMA_SERVER_PORT", "8000")
        )
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"❌ Could not connect to ChromaDB: {e}")
        return

    # --- 1. 获取数据库现有状态 ---
    # 获取所有记录的 source 和 file_hash 元数据
    print("🔍 Scanning database state...")
    existing_data = collection.get(include=["metadatas"])
    
    # 建立映射: source_path -> {ids: [id1, id2...], hash: "abc..."}
    db_state = {} 
    
    if existing_data and existing_data["ids"]:
        for i, doc_id in enumerate(existing_data["ids"]):
            meta = existing_data["metadatas"][i]
            if not meta: continue
            
            source = meta.get("source")
            if not source: continue
            
            # 统一路径格式以便比较
            norm_source = os.path.normpath(source)
            
            if norm_source not in db_state:
                db_state[norm_source] = {"ids": [], "hash": meta.get("file_hash", "")}
            db_state[norm_source]["ids"].append(doc_id)

    print(f"👀 DB contains chunks from {len(db_state)} files.")

    # --- 2. 获取本地文件状态 ---
    local_files = glob.glob(os.path.join(DATA_DIR, "**/*.md"), recursive=True) +
                  glob.glob(os.path.join(DATA_DIR, "**/*.txt"), recursive=True)
    
    local_state = {} # path -> hash
    for f in local_files:
        norm_path = os.path.normpath(f)
        local_state[norm_path] = calculate_file_hash(norm_path)

    print(f"📂 Local folder contains {len(local_state)} files.")

    # --- 3. 计算差异 ---
    to_add = []      # (path, hash)
    to_update = []   # (path, hash, old_ids)
    to_delete = []   # (path, all_ids)

    # 检查本地文件 (新增或更新)
    for f_path, f_hash in local_state.items():
        if f_path not in db_state:
            # 新增
            to_add.append((f_path, f_hash))
        else:
            # 检查是否修改
            db_info = db_state[f_path]
            # 如果数据库里的 hash 是空的（旧数据），或者 hash 不一致，都视为更新
            if db_info["hash"] != f_hash:
                to_update.append((f_path, f_hash, db_info["ids"]))

    # 检查已删除文件
    for db_path, info in db_state.items():
        if db_path not in local_state:
            to_delete.append((db_path, info["ids"]))

    print(f"📊 Sync Plan: +Add {len(to_add)} | ~Update {len(to_update)} | -Delete {len(to_delete)}")

    if not to_add and not to_update and not to_delete:
        print("✅ Everything is up to date.")
        return

    # --- 4. 执行同步 ---
    
    # 4.1 删除操作 (Delete & Update-Delete)
    ids_to_remove = []
    for item in to_delete:
        print(f"   🗑️  Marked for deletion: {os.path.basename(item[0])}")
        ids_to_remove.extend(item[1])
    
    for item in to_update:
        print(f"   🔄 Marked for update: {os.path.basename(item[0])}")
        ids_to_remove.extend(item[2])
        
    if ids_to_remove:
        # 批量删除，避免请求过大，分批删（虽然 Chroma 支持较大 batch，但稳妥起见）
        batch_size = 5000 
        for i in range(0, len(ids_to_remove), batch_size):
            batch = ids_to_remove[i:i+batch_size]
            print(f"   🔥 Deleting batch of {len(batch)} chunks...")
            collection.delete(ids=batch)

    # 4.2 新增/重新插入操作 (Add & Update-Add)
    files_to_process = [x[0] for x in to_add] + [x[0] for x in to_update]
    
    if not files_to_process:
        print("✅ Sync complete (Only deletions performed).")
        return

    # 加载并切分
    documents = []
    for f in files_to_process:
        try:
            # 原始路径可能在 local_state 的 key 里被 normpath 了，这里尽量用原始glob出来的路径或还原
            # 但 TextLoader 只要路径存在即可。f 是 normpath 过的。
            loader = TextLoader(f, encoding='utf-8')
            docs = loader.load()
            
            current_hash = local_state[f]

            for doc in docs:
                doc.metadata["source"] = f
                doc.metadata["filename"] = os.path.basename(f)
                doc.metadata["file_hash"] = current_hash # 关键：存入 Hash
            documents.extend(docs)
            print(f"   - Loaded: {os.path.basename(f)}")
        except Exception as e:
            print(f"   ❌ Failed to load {f}: {e}")

    if documents:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        print("🧠 Initializing embedding model (HuggingFace)...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        vector_store = Chroma(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings
        )
        
        # 分批插入以防内存溢出或超时
        batch_size = 100
        total_chunks = len(chunks)
        print(f"💾 Ingesting {total_chunks} chunks...")
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i+batch_size]
            vector_store.add_documents(batch)
            print(f"      ...ingested {min(i+batch_size, total_chunks)}/{total_chunks}")

    print("✅ Sync complete!")

if __name__ == "__main__":
    ingest_docs()
