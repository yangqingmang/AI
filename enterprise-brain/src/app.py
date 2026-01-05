import streamlit as st
import os
import sys
import time
import hashlib
import uuid

# 引入工厂
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from db_factory import DBFactory
except ImportError:
    from src.db_factory import DBFactory

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置页面
st.set_page_config(
    page_title="Enterprise Brain Chat",
    page_icon="💬",
    layout="centered" # 聊天界面通常居中更好看
)

@st.cache_resource
def load_chain():
    """初始化 RAG 链"""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = DBFactory.get_vector_store(embeddings)
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
    st.title("💬 Enterprise Assistant")
    st.caption("🚀 Powered by RAG & DeepSeek")
    
    # 顶部工具栏
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是你的 AI 助手。请问有什么可以帮你？"}
        ]

    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 处理用户输入
    if prompt := st.chat_input("Input your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                vector_store, llm, cache_collection, embeddings = load_chain()
                
                # --- Semantic Cache ---
                prompt_vector = embeddings.embed_query(prompt)
                cache_results = cache_collection.query(
                    query_embeddings=[prompt_vector],
                    n_results=1
                )
                
                cache_hit = False
                CACHE_THRESHOLD = 0.2
                
                if (cache_results['ids'] and 
                    cache_results['distances'] and 
                    len(cache_results['distances']) > 0 and 
                    len(cache_results['distances'][0]) > 0 and
                    cache_results['distances'][0][0] < CACHE_THRESHOLD):
                    
                    cached_answer = cache_results['metadatas'][0][0]['answer']
                    message_placeholder.markdown(cached_answer + " (🚀 Cached)")
                    full_response = cached_answer
                    cache_hit = True
                    st.divider()
                    st.caption(f"⚡ Semantic Cache Hit (Distance: {cache_results['distances'][0][0]:.4f})")
                
                if not cache_hit:
                    # --- RAG ---
                    results = vector_store.similarity_search(prompt, k=3)
                    
                    context_text = ""
                    sources = []
                    if results:
                        context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
                        sources = results
                    
                    prompt_template = ChatPromptTemplate.from_template("""
                    你是一个专业的企业级 AI 战略顾问（Enterprise Brain）。
                    你的任务是基于【上下文信息】回答用户的【问题】。
                    核心规则：
                    1. 如果【上下文信息】包含答案，请精准引用并回答。
                    2. 如果【上下文信息】为空或与问题无关（例如用户在打招呼“你好”），请忽略上下文，用礼貌、专业的口吻进行自我介绍或闲聊。
                    3. 自我介绍话术参考：“你好！我是你的 AI 战略顾问。我熟知你上传的所有战略文档，可以帮你解答关于技术架构、副业路线、SOP 流程等问题。”
                    
                    【上下文信息】:
                    {context}
                    【问题】:
                    {question}
                    """)
                    
                    chain = prompt_template | llm
                    
                    full_response = ""
                    for chunk in chain.stream({"context": context_text, "question": prompt}):
                        if chunk.content:
                            full_response += chunk.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                    # 写入缓存
                    cache_id = str(uuid.uuid4())
                    cache_collection.add(ids=[cache_id], embeddings=[prompt_vector], metadatas=[{"answer": full_response, "question": prompt}])
                    
                    if sources:
                        with st.expander("📚 Reference"):
                            for i, doc in enumerate(sources):
                                st.caption(f"Source: {os.path.basename(doc.metadata.get('source', 'Unknown'))}")

            except Exception as e:
                full_response = f"Error: {str(e)}"
                message_placeholder.error(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()