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
    from tool_factory import ToolFactory
except ImportError:
    from src.db_factory import DBFactory
    from src.tool_factory import ToolFactory

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置页面
st.set_page_config(
    page_title="Enterprise Agent",
    page_icon="🤖",
    layout="centered"
)

@st.cache_resource
def load_agent(pro_mode=False):
    """
    初始化 Agent (使用 LangGraph)
    :param pro_mode: 是否开启高级工具 (联网、代码、文件)
    """
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
    
    # 1. 基础工具 (Free Plan)
    retriever_tool = create_retriever_tool(
        vector_store.as_retriever(search_kwargs={"k": 3}),
        "knowledge_base",
        "搜索企业内部知识库。关于公司战略、SOP、技术文档的问题优先使用此工具。"
    )
    tools = [retriever_tool]
    
    system_prompt = """你是一个专业的企业级 AI 战略顾问。
    你的主要任务是基于内部知识库回答用户问题。
    """

    # 2. 高级工具 (Pro Plan)
    if pro_mode:
        search_tool = ToolFactory.get_search_tool()
        python_tool = ToolFactory.get_python_tool()
        file_tools = ToolFactory.get_file_tools()
        tools.extend([search_tool, python_tool] + file_tools)
        
        system_prompt = """你是一个全能的企业级 AI 智能体（Autonomous Agent）。
        你不仅能回答问题，还能编写代码、分析数据、管理文件、联网搜索。
        """
    
    # 3. 使用 LangGraph 构建 ReAct Agent
    # state_modifier 相当于 System Prompt
    agent_executor = create_react_agent(llm, tools, state_modifier=system_prompt)
    
    return agent_executor, cache_collection, embeddings

def main():
    st.title("💬 Enterprise Assistant")
    
    # --- 侧边栏功能开关 ---
    with st.sidebar:
        st.header("💎 Subscription")
        pro_mode = st.checkbox("Enable Pro Mode (Agent)", value=False, help="Unlock Web Search, Code Execution, and File Management.")
        if pro_mode:
            st.success("🚀 Pro Features Active")
        else:
            st.info("🌱 Free Plan (RAG Only)")
        st.markdown("---")

    st.caption("🚀 Powered by RAG & LangGraph & DeepSeek")
    
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是你的 AI 助手。请问有什么可以帮你？"}
        ]

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
                # 传入 pro_mode 开关状态
                agent_executor, cache_collection, embeddings = load_agent(pro_mode)
                
                # ... 缓存逻辑 (不变) ...
                prompt_vector = embeddings.embed_query(prompt)
                
                cache_results = cache_collection.query(query_embeddings=[prompt_vector], n_results=1)
                
                cache_hit = False
                if (cache_results['ids'] and 
                    cache_results['distances'] and 
                    len(cache_results['distances']) > 0 and 
                    len(cache_results['distances'][0]) > 0 and 
                    cache_results['distances'][0][0] < 0.2):
                    
                    cached_answer = cache_results['metadatas'][0][0]['answer']
                    message_placeholder.markdown(cached_answer + " (🚀 Cached)")
                    full_response = cached_answer
                    cache_hit = True
                
                if not cache_hit:
                    start_time = time.time()
                    with st.status("🤖 Thinking...", expanded=True) as status:
                        # LangGraph 调用方式: 传入 messages 列表
                        response = agent_executor.invoke({"messages": [HumanMessage(content=prompt)]})
                        status.update(label="✅ Finished!", state="complete", expanded=False)
                    
                    # 从 LangGraph 返回的消息列表中提取最后一条 (AIMessage) 的内容
                    full_response = response["messages"][-1].content
                    message_placeholder.markdown(full_response)
                    
                    cache_id = str(uuid.uuid4())
                    cache_collection.add(ids=[cache_id], embeddings=[prompt_vector], metadatas=[{"answer": full_response, "question": prompt}])

            except Exception as e:
                full_response = f"Error: {str(e)}"
                message_placeholder.error(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()