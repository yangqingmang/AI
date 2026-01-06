import os
from langchain_core.tools import Tool
from src.config.settings import get_settings

settings = get_settings()

def list_files(_=None):
    try:
        if not os.path.exists(settings.DATA_DIR):
            return "Data directory does not exist."
        return str(os.listdir(settings.DATA_DIR))
    except Exception as e:
        return f"Error listing files: {str(e)}"

def write_file(file_content_pair):
    """
    输入格式: "filename|content"
    例如: "report.md|# Weekly Report..."
    """
    try:
        if "|" not in file_content_pair:
            return "Error: Input must be in format 'filename|content'"
            
        filename, content = file_content_pair.split("|", 1)
        filepath = os.path.join(settings.DATA_DIR, filename.strip())
        
        # Ensure data directory exists
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {e}"

def get_file_tools() -> list[Tool]:
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
