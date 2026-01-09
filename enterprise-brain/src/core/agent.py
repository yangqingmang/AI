from langgraph.prebuilt import create_react_agent
from langchain_core.tools.retriever import create_retriever_tool

from src.core.llm import get_llm
from src.core.db import DBFactory
from src.core.retriever import get_retriever
from src.core.tools.retrieval import get_retrieval_tool
from src.tools.search import get_search_tool
from src.tools.python import get_python_tool
from src.tools.files import get_file_tools

def build_agent(pro_mode: bool, embeddings, checkpointer=None):
    """
    构建 LangGraph ReAct Agent
    """
    llm = get_llm()
    # 使用混合检索器 (BM25 + Vector)
    retriever = get_retriever(embeddings)
    
    # 1. 基础知识库工具 (使用自定义 Tool 以保留 Source 信息)
    retriever_tool = get_retrieval_tool(retriever)
    
    tools = [retriever_tool]
    
    system_prompt = """你是一个专业的企业级 AI 战略顾问。
    你的主要任务是基于内部知识库回答用户问题。
    """

    # 2. 高级工具
    if pro_mode:
        tools.append(get_search_tool())
        tools.append(get_python_tool())
        tools.extend(get_file_tools())
        
        system_prompt = """你是一个全能的企业级 AI 智能体（Autonomous Agent）。
    你不仅能回答问题，还能编写代码、分析数据、管理文件、联网搜索。
    """

    # 3. 构建图 (传入 checkpointer 以支持记忆)
    graph = create_react_agent(llm, tools, checkpointer=checkpointer)
    return graph, system_prompt
