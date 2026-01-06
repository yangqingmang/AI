from langchain_experimental.tools import PythonREPLTool
from langchain_core.tools import Tool

def get_python_tool() -> Tool:
    """
    初始化 Python 代码执行工具
    """
    repl = PythonREPLTool()
    return Tool(
        name="python_interpreter",
        func=repl.run,
        description="一个 Python 代码执行环境。当你需要进行数学计算、数据分析、绘制图表或者处理复杂逻辑时，请使用此工具。输入必须是合法的 Python 代码字符串。"
    )
