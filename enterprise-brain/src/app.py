import streamlit as st
import time
import uuid
import sys
import os

# 确保项目根目录在 path 中 (解决 docker 运行时的导入问题)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

from src.core.agent import build_agent
from src.core.db import DBFactory
from src.core.llm import get_embeddings
from src.core.ingest import ingest_docs
from src.config.settings import get_settings

# 加载环境
load_dotenv()
settings = get_settings()

# 配置页面
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🤖",
    layout="wide"
)

# 自定义 CSS 稍微美化一下对话气泡 (可选)
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_resources(pro_mode=False):
    """
    初始化资源 (Cached)
    """
    embeddings = get_embeddings()
    cache_collection = DBFactory.get_cache_collection(embeddings)
    # build_agent 现在返回 (graph, system_prompt)
    agent_graph, system_prompt = build_agent(pro_mode, embeddings)
    return agent_graph, system_prompt, cache_collection, embeddings

def main():
    st.markdown(f"<h1 style='text-align: center;'>💬 {settings.APP_NAME}</h1>", unsafe_allow_html=True)
    
    # --- Sidebar ---
    with st.sidebar:
        st.header("💎 Subscription")
        pro_mode = st.checkbox("Enable Pro Mode (Agent)", value=False, help="Unlock Web Search, Code Execution, and File Management.")
        if pro_mode:
            st.success("🚀 Pro Features Active")
        else:
            st.info("🌱 Free Plan (RAG Only)")
        
        st.markdown("---")
        st.header("📚 Knowledge Base")
        uploaded_files = st.file_uploader("Upload Docs (TXT/MD/PDF)", accept_multiple_files=True)
        
        if uploaded_files:
            if st.button("📥 Ingest Files"):
                with st.status("Processing Documents...", expanded=True) as status:
                    # Save files
                    os.makedirs(settings.DATA_DIR, exist_ok=True)
                    for uploaded_file in uploaded_files:
                        save_path = os.path.join(settings.DATA_DIR, uploaded_file.name)
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        status.write(f"Saved: {uploaded_file.name}")
                    
                    # Run Ingestion
                    status.write("Starting Vectorization...")
                    # Capture ingest logs
                    ingest_docs(progress_callback=status.write)
                    status.update(label="✅ Knowledge Base Updated!", state="complete", expanded=False)
                    time.sleep(1) # feedback delay

        st.markdown("---")
        st.caption(f"Version: {settings.APP_VERSION}")

    # --- Session State ---
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是你的 AI 助手。请问有什么可以帮你？"}
        ]

    # --- Chat UI ---
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            # 用户消息：自定义 HTML 实现靠右显示
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin-bottom: 10px;">
                <div style="background-color: #e6f3ff; color: #000; padding: 10px; border-radius: 15px; border-top-right-radius: 0; max-width: 75%; box-shadow: 1px 1px 5px rgba(0,0,0,0.1);">
                    {msg["content"]}
                </div>
                <div style="min-width: 40px; height: 40px; background-color: #f0f2f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 10px; font-size: 20px;">
                    👤
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 助手消息：使用原生组件 (保留 Markdown 渲染能力)
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Input your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 渲染用户新消息 (即时显示)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin-bottom: 10px;">
            <div style="background-color: #e6f3ff; color: #000; padding: 10px; border-radius: 15px; border-top-right-radius: 0; max-width: 75%; box-shadow: 1px 1px 5px rgba(0,0,0,0.1);">
                {prompt}
            </div>
            <div style="min-width: 40px; height: 40px; background-color: #f0f2f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 10px; font-size: 20px;">
                👤
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 助手回答 (左侧)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Load resources with visible status
                with st.spinner("Initializing AI Engine..."):
                    agent_graph, system_prompt, cache_collection, embeddings = init_resources(pro_mode)
                
                # 1. Cache Check (Hybrid Strategy)
                cache_hit = False
                
                # A. 精确匹配 (Exact Match): 优先检查字面完全一样的问题
                # 这能完美解决短语(如"你好")的误判，且完全免费
                exact_match = cache_collection.get(where={"question": prompt})
                if exact_match and exact_match['ids']:
                    cached_answer = exact_match['metadatas'][0]['answer']
                    message_placeholder.markdown(cached_answer + " (🚀 Cached)")
                    full_response = cached_answer
                    cache_hit = True
                
                # B. 向量模糊匹配 (Vector Match): 仅针对长问题
                if not cache_hit and len(prompt) > 10:
                    prompt_vector = embeddings.embed_query(prompt)
                    cache_results = cache_collection.query(query_embeddings=[prompt_vector], n_results=1)
                    
                    if (cache_results['ids'] and 
                        len(cache_results['distances'][0]) > 0 and 
                        cache_results['distances'][0][0] < 0.1):
                        
                        cached_answer = cache_results['metadatas'][0][0]['answer']
                        message_placeholder.markdown(cached_answer + " (🚀 Cached)")
                        full_response = cached_answer
                        cache_hit = True
                
                # 2. Agent Execution
                if not cache_hit:
                    # 使用流式输出来降低首字延迟
                    full_response = ""
                    
                    # 构造消息
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=prompt)
                    ]
                    
                    # 这里的 stream_mode="messages" 会返回每一步的消息更新
                    stream = agent_graph.stream({"messages": messages}, stream_mode="messages")
                    
                    for event in stream:
                        # event 是 (message, metadata) 元组或者直接是 message (取决于版本)
                        # 在 LangGraph prebuilt agent 中，通常返回 (message, metadata)
                        # 我们只关心 AIMessageChunk 且 content 不为空的部分
                        
                        msg_chunk, _ = event if isinstance(event, tuple) else (event, None)
                        
                        # 只处理来自 AI 的内容块
                        if msg_chunk.content and msg_chunk.type == "ai":
                            full_response += msg_chunk.content
                            # 实时更新 UI (加个光标效果)
                            message_placeholder.markdown(full_response + "▌")
                    
                    # 最终移除光标
                    message_placeholder.markdown(full_response)
                    
                    # Update Cache
                    cache_id = str(uuid.uuid4())
                    cache_collection.add(
                        ids=[cache_id], 
                        embeddings=[prompt_vector], 
                        metadatas=[{"answer": full_response, "question": prompt}]
                    )

            except Exception as e:
                full_response = f"Error: {str(e)}"
                message_placeholder.error(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()