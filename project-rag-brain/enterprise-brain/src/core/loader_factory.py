import os
import psutil
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# Try importing MarkItDown (Microsoft's tool), handle if not installed
try:
    from markitdown import MarkItDown
    HAS_MARKITDOWN = True
except ImportError:
    HAS_MARKITDOWN = False

class AdaptiveLoader:
    """
    智能文档加载器工厂
    根据系统资源和配置自动选择最佳解析策略
    """
    
    @staticmethod
    def get_system_ram_gb():
        """获取系统总内存 (GB)"""
        try:
            return psutil.virtual_memory().total / (1024 ** 3)
        except:
            return 4.0 # Default fallback

    @staticmethod
    def load(file_path: str) -> List[Document]:
        """
        根据环境自动选择最佳 Loader 加载文档
        """
        ext = os.path.splitext(file_path)[1].lower()
        ram_gb = AdaptiveLoader.get_system_ram_gb()
        
        # 1. 优先策略: 云端解析 (如果配置了 LlamaCloud)
        # TODO: 集成 LlamaParse (未来扩展点)
        # if os.getenv("LLAMA_CLOUD_API_KEY"):
        #     return LlamaParseLoader(file_path).load()

        # 2. PDF 处理策略
        if ext == ".pdf":
            # 策略 A: 高性能本地模式 (RAM >= 8GB 且安装了 MarkItDown)
            if ram_gb >= 8 and HAS_MARKITDOWN:
                print(f"🚀 [High-Spec] Using Microsoft MarkItDown for {os.path.basename(file_path)}")
                return AdaptiveLoader._load_with_markitdown(file_path)
            
            # 策略 B: 节能/兼容模式 (默认)
            print(f"🍃 [Eco-Mode] Using PyPDFLoader for {os.path.basename(file_path)}")
            return PyPDFLoader(file_path).load()

        # 3. 默认文本处理
        return TextLoader(file_path, encoding='utf-8').load()

    @staticmethod
    def _load_with_markitdown(file_path: str) -> List[Document]:
        """使用 MarkItDown 将文档转换为 Markdown 格式的 Document"""
        try:
            md = MarkItDown()
            result = md.convert(file_path)
            
            # MarkItDown 返回的是整个转换后的文本内容
            # 我们将其封装为一个 Document 对象，保留元数据
            content = result.text_content
            
            metadata = {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "parser": "markitdown"
            }
            
            return [Document(page_content=content, metadata=metadata)]
        except Exception as e:
            print(f"⚠️ MarkItDown failed, falling back to basic loader: {e}")
            return PyPDFLoader(file_path).load()
