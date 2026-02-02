import os
import sys
import glob
from typing import List, Dict, Any
from dotenv import load_dotenv
from anthropic import Anthropic
from termcolor import colored

# 加载环境变量
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print(colored("错误: 未找到 ANTHROPIC_API_KEY，请在 .env 文件中配置。", "red"))
    print("请复制 .env.example 为 .env 并填入你的 Key。")
    sys.exit(1)

client = Anthropic(api_key=api_key)

# --- 1. 定义工具 (Tools) ---

def list_files(directory: str = ".", pattern: str = "**/*.py") -> List[str]:
    """
    列出指定目录下的文件。
    :param directory: 根目录路径
    :param pattern: 匹配模式 (例如 **/*.py)
    """
    print(colored(f"🛠️  Agent正在列出文件: {directory} ({pattern})..."), "cyan"))
    files = []
    try:
        # 使用 glob 递归查找
        search_path = os.path.join(directory, pattern)
        for file in glob.glob(search_path, recursive=True):
            if os.path.isfile(file):
                # 转为相对路径以便阅读
                files.append(os.path.relpath(file, start="."))
    except Exception as e:
        return [f"Error listing files: {str(e)}"]
    
    # 限制返回数量，避免 Token 爆炸
    return files[:50] 

def read_file(file_path: str) -> str:
    """
    读取文件内容。
    """
    print(colored(f"🛠️  Agent正在读取文件: {file_path}..."), "cyan"))
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# 工具定义 (JSON Schema)
tools = [
    {
        "name": "list_files",
        "description": "Recursively list files in a directory to understand the project structure. Use patterns like '**/*.py' or '**/*.js' to filter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Root directory to start search (default: '.')"},
                "pattern": {"type": "string", "description": "Glob pattern to filter files (default: '**/*')"}
            }
        }
    },
    {
        "name": "read_file",
        "description": "Read the full content of a specific file. Use this to analyze code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The relative path of the file to read"}
            },
            "required": ["file_path"]
        }
    }
]

# --- 2. 主循环 (Agent Loop) ---

def run_agent(task: str):
    print(colored(f"\n🤖 任务: {task}\n"), "green", attrs=['bold'])
    
    messages = []
    messages.append({"role": "user", "content": task})

    # 简单的循环，防止无限运行，设置最大交互次数
    MAX_TURNS = 10
    
    for i in range(MAX_TURNS):
        print(f"--- 第 {i+1} 回合 ---")
        
        # 1. 调用 Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022", # 使用最新的 Sonnet 模型
            max_tokens=4096,
            system="""你是一个资深代码审计专家 Agent。你的目标是扫描用户的代码库，理解架构，并发现潜在的错误、安全漏洞或代码风格问题。
            
            工作流程建议：
            1. 首先使用 list_files 了解项目结构。
            2. 选择关键文件使用 read_file 读取内容。
            3. 分析代码逻辑。
            4. 最后给出一份简短的总结报告，包含发现的问题和改进建议。
            
            不要一次性读取所有文件，先看概览，再深入关键部分。""",
            messages=messages,
            tools=tools
        )

        # 2. 处理响应
        # 检查是否有工具调用
        if response.stop_reason == "tool_use":
            tool_outputs = []
            
            # 这里可能会有多个工具调用并行
            for content in response.content:
                if content.type == "text":
                    print(colored(f"Claude: {content.text}"), "yellow")
                
                elif content.type == "tool_use":
                    tool_name = content.name
                    tool_input = content.input
                    tool_use_id = content.id
                    
                    result = ""
                    if tool_name == "list_files":
                        result = list_files(
                            directory=tool_input.get("directory", "."),
                            pattern=tool_input.get("pattern", "**/*")
                        )
                        result = str(result) # 转换为字符串
                        
                    elif tool_name == "read_file":
                        result = read_file(file_path=tool_input.get("file_path"))
                    
                    # 记录工具输出
                    tool_outputs.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    })

            # 将工具结果添加回对话历史
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_outputs})
            
        else:
            # 没有工具调用，说明 Agent 完成了任务或正在提问
            print(colored(f"\n✅ 完成:\n{response.content[0].text}"), "green")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_task = sys.argv[1]
    else:
        user_task = "请扫描当前目录下的代码，分析其主要功能并指出潜在问题。"
    
    run_agent(user_task)
