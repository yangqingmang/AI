import streamlit as st
import time
import uuid
import sys
import os

# 确保 src 目录在 path 中 (解决 docker 运行时的导入问题)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from src.core.agent import build_agent
from src.core.db import DBFactory
from src.core.llm import get_embeddings
from src.config.settings import get_settings

# 加载环境
load_dotenv()
settings = get_settings()

# 配置页面
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🤖",
    layout="centered"
)

@st.cache_resource
def init_resources(pro_mode=False):
    """
    初始化资源 (Cached)
    """
    embeddings = get_embeddings()
    cache_collection = DBFactory.get_cache_collection(embeddings)
    agent_graph = build_agent(pro_mode, embeddings)
    return agent_graph, cache_collection, embeddings

def main():
    st.title(f"💬 {settings.APP_NAME}")
    
    # --- Sidebar ---
    with st.sidebar:
        st.header("💎 Subscription")
        pro_mode = st.checkbox("Enable Pro Mode (Agent)", value=False, help="Unlock Web Search, Code Execution, and File Management.")
        if pro_mode:
            st.success("🚀 Pro Features Active")
        else:
            st.info("🌱 Free Plan (RAG Only)")
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
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Input your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Load resources
                agent_graph, cache_collection, embeddings = init_resources(pro_mode)
                
                # 1. Cache Check
                prompt_vector = embeddings.embed_query(prompt)
                cache_results = cache_collection.query(query_embeddings=[prompt_vector], n_results=1)
                
                cache_hit = False
                if (cache_results['ids'] and 
                    len(cache_results['distances'][0]) > 0 and 
                    cache_results['distances'][0][0] < 0.2):
                    
                    cached_answer = cache_results['metadatas'][0][0]['answer']
                    message_placeholder.markdown(cached_answer + " (🚀 Cached)")
                    full_response = cached_answer
                    cache_hit = True
                
                # 2. Agent Execution
                if not cache_hit:
                    with st.status("🤖 Thinking...", expanded=True) as status:
                        response = agent_graph.invoke({"messages": [HumanMessage(content=prompt)]})
                        status.update(label="✅ Finished!", state="complete", expanded=False)
                    
                    # Extract final answer
                    full_response = response["messages"][-1].content
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
