import streamlit as st
import os
import glob
import sys
import time
import hashlib
import uuid

# 将 src 目录加入 Python 路径，以便导入 ingest 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 引入工厂
try:
    from db_factory import DBFactory
    from ingest import ingest_docs
except ImportError:
    from src.db_factory import DBFactory
    from src.ingest import ingest_docs

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置页面
st.set_page_config(
    page_title="Enterprise Brain",
    page_icon="🧠",
    layout="wide"
)

# 路径配置
DB_DIR = "chroma_db"
DATA_DIR = "data"

# 确保 data 目录存在
os.makedirs(DATA_DIR, exist_ok=True)

@st.cache_resource
def load_chain():
    """
    初始化 RAG 链 (Embedding + VectorStore + LLM)
    使用工厂模式解耦数据库实现
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 1. 工厂生产向量库 (Chroma 或 Pgvector，由 .env 决定)
    vector_store = DBFactory.get_vector_store(embeddings)
    
    # 2. 获取语义缓存 (目前固定为 Chroma)
    cache_collection = DBFactory.get_cache_collection(embeddings)
    
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL_NAME", "deepseek-chat"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
        temperature=0.1,
        streaming=True
    )
    
    return vector_store, llm, cache_collection, embeddings

def main():
    st.title("🧠 Enterprise Brain (RAG System)")
    st.markdown("---")

    # --- 侧边栏：知识库管理 ---
    with st.sidebar:
        st.header("📂 Knowledge Base")
        
        # 1. 文件列表
        files = glob.glob(os.path.join(DATA_DIR, "*.* المحتوى"))
        if files:
            st.info(f"Loaded {len(files)} documents")
            with st.expander("📄 View File List"):
                for f in files:
                    st.text(os.path.basename(f))
        else:
            st.warning("No documents found.")

        st.markdown("---")
        
        # 2. 上传新文档
        st.subheader("📥 Add Documents")
        uploaded_files = st.file_uploader(
            "Upload .md or .txt", 
            type=["md", "txt"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("💾 Save & Process"):
                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    # 保存文件
                    save_path = os.path.join(DATA_DIR, uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.success(f"Saved {len(uploaded_files)} files!")
                
                # 触发重建
                with st.spinner("🧠 Re-building Brain (Ingesting)..."):
                    ingest_docs()
                    st.cache_resource.clear() # 清除缓存，强制重载向量库
                
                st.success("✅ Brain Updated Successfully!")
                st.rerun()

        # 3. 手动重建按钮 (用于手动放入文件后)
        if st.button("🔄 Re-build Brain (Force)"):
             with st.spinner("🧠 Re-building Brain..."):
                ingest_docs()
                st.cache_resource.clear()
             st.success("Brain reloaded!")
             st.rerun()
            
        st.markdown("---")
        st.caption("Backend: LangChain + DeepSeek + ChromaDB")

    # --- 主聊天界面 ---
    
    # 顶部工具栏
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # 1. 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是你的 AI 战略顾问。基于你上传的战略文档，有什么我可以帮你的吗？"}
        ]

    # 2. 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 3. 处理用户输入
    if prompt := st.chat_input("Ask a question about your strategy..."):
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成 AI 回答
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # --- RAG 逻辑开始 ---
            try:
                # 获取组件
                vector_store, llm, cache_collection, embeddings = load_chain()
                
                # Step 1: 语义缓存检索 (Semantic Cache Lookup)
                start_cache = time.time()
                
                # 计算问题向量
                prompt_vector = embeddings.embed_query(prompt)
                
                # 在缓存库中搜最相似的 1 条
                cache_results = cache_collection.query(
                    query_embeddings=[prompt_vector],
                    n_results=1
                )
                
                cache_hit = False
                # 判定阈值：Chroma 默认使用 L2 距离，越小越相似
                # 0.2 大约对应余弦相似度 0.9+，非常严格，防止答非所问
                CACHE_THRESHOLD = 0.2
                
                if cache_results['ids'] and cache_results['distances'][0][0] < CACHE_THRESHOLD:
                    cached_answer = cache_results['metadatas'][0][0]['answer']
                    message_placeholder.markdown(cached_answer + " (🚀 Semantic Cache)")
                    full_response = cached_answer
                    cache_hit = True
                    
                    st.divider()
                    st.caption(f"⚡ Semantic Cache Hit (Distance: {cache_results['distances'][0][0]:.4f})")
                
                # Step 2: 缓存未命中，走 RAG
                if not cache_hit:
                    # ... 原有 RAG 检索逻辑 ...
                    start_time = time.time()
                    with st.spinner("🔍 Searching..."):
                        results = vector_store.similarity_search(prompt, k=3)
                    retrieval_time = time.time() - start_time
                    
                    if not results:
                        full_response = "⚠️ 知识库中没有找到相关信息，请尝试上传相关文档。"
                        message_placeholder.markdown(full_response)
                    else:
                        context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
                        
                        # ... Prompt 构建 ...
                        prompt_template = ChatPromptTemplate.from_template("""
                        你是一个资深的 AI 战略顾问。请基于以下的【上下文信息】，回答用户的【问题】。
                        
                        规则：
                        1. 引用上下文中的关键数据或观点来支持你的回答。
                        2. 使用 Markdown 格式优化排版（如列表、粗体）。
                        3. 如果上下文中没有答案，请明确告知。

                        【上下文信息】：
                        {context}

                        【问题】：
                        {question}
                        """)
                        
                        chain = prompt_template | llm
                        
                        start_gen = time.time()
                        full_response = ""
                        for chunk in chain.stream({"context": context_text, "question": prompt}):
                            if chunk.content:
                                full_response += chunk.content
                                message_placeholder.markdown(full_response + "▌")
                        
                        generation_time = time.time() - start_gen
                        message_placeholder.markdown(full_response)
                        
                        # Step 3: 写入语义缓存
                        # 使用 uuid 作为 ID
                        cache_id = str(uuid.uuid4())
                        cache_collection.add(
                            ids=[cache_id],
                            embeddings=[prompt_vector], # 复用刚才算的向量
                            metadatas=[{"answer": full_response, "question": prompt}]
                        )
                        
                        st.divider()
                        cols = st.columns(4)
                        cols[0].caption(f"⏱️ Retrieval: **{retrieval_time:.3f}s**")
                        cols[1].caption(f"🧠 Generation: **{generation_time:.3f}s**")
                        cols[2].caption(f"⚡ Total: **{retrieval_time + generation_time:.3f}s**")
                        
                        # ... Source 显示 ...
                        with st.expander("📚 View Sources"):
                            for i, doc in enumerate(results):
                                source = doc.metadata.get('source', 'Unknown')
                                st.markdown(f"**Source {i+1}**: `{os.path.basename(source)}`")
                                st.caption(doc.page_content[:200] + "...")

            except Exception as e:
                full_response = f"❌ Error: {str(e)}"
                message_placeholder.error(full_response)
            
            # --- RAG 逻辑结束 ---

        # 保存 AI 回答到历史
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()