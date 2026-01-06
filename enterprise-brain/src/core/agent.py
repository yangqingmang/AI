from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool

from src.core.llm import get_llm
from src.core.db import DBFactory
from src.tools.search import get_search_tool
from src.tools.python import get_python_tool
from src.tools.files import get_file_tools

def build_agent(pro_mode: bool, embeddings):
    """
    构建 LangGraph ReAct Agent
    """
    llm = get_llm()
    vector_store = DBFactory.get_vector_store(embeddings)
    
    # 1. 基础知识库工具
    retriever_tool = create_retriever_tool(
        vector_store.as_retriever(search_kwargs={"k": 3}),
        "knowledge_base",
        "搜索企业内部知识库。关于公司战略、SOP、技术文档的问题优先使用此工具。"
    )
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

    # 3. 构建图
    graph = create_react_agent(llm, tools, state_modifier=system_prompt)
    return graph
