from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool

def get_search_tool() -> Tool:
    """
    初始化 DuckDuckGo 搜索工具
    """
    search = DuckDuckGoSearchRun()
    return Tool(
        name="web_search",
        func=search.run,
        description="当知识库中没有答案，或者用户询问实时信息（如新闻、股价、天气）时使用此工具。输入应该是具体的搜索关键词。"
    )
