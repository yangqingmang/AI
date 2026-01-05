import os
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from langchain_experimental.tools import PythonREPLTool

class ToolFactory:
    @staticmethod
    def get_search_tool():
        """
        初始化 DuckDuckGo 搜索工具
        """
        search = DuckDuckGoSearchRun()
        return Tool(
            name="web_search",
            func=search.run,
            description="当知识库中没有答案，或者用户询问实时信息（如新闻、股价、天气）时使用此工具。输入应该是具体的搜索关键词。"
        )

    @staticmethod
    def get_python_tool():
        """
        初始化 Python 代码执行工具
        """
        repl = PythonREPLTool()
        return Tool(
            name="python_interpreter",
            func=repl.run,
            description="一个 Python 代码执行环境。当你需要进行数学计算、数据分析、绘制图表或者处理复杂逻辑时，请使用此工具。输入必须是合法的 Python 代码字符串。"
        )

    @staticmethod
    def get_file_tools():
        """
        初始化文件操作工具集
        """
        def list_files(_=None):
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            return str(os.listdir(data_dir))

        def write_file(file_content_pair):
            """
            输入格式: "filename|content"
            例如: "report.md|# Weekly Report..."
            """
            try:
                filename, content = file_content_pair.split("|", 1)
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                filepath = os.path.join(data_dir, filename.strip())
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote to {filename}"
            except Exception as e:
                return f"Error writing file: {e}"

        return [
            Tool(
                name="list_documents",
                func=list_files,
                description="列出知识库(data目录)中现有的所有文件。无需输入。"
            ),
            Tool(
                name="write_document",
                func=write_file,
                description="在知识库中创建或覆盖一个文件。输入格式必须是 'filename|content'。例如：'summary.txt|This is the content'."
            )
        ]