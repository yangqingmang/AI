from langchain.tools import tool
from langchain_core.documents import Document
from typing import List

def format_docs(docs: List[Document]) -> str:
    formatted = []
    for doc in docs:
        source = doc.metadata.get("filename") or doc.metadata.get("source") or "Unknown"
        content = doc.page_content.replace("\n", " ")
        formatted.append(f"Source: {source}\nContent: {content}")
    return "\n\n".join(formatted)

def get_retrieval_tool(retriever):
    @tool(name="knowledge_base")
    def retrieve_docs(query: str) -> str:
        """
        搜索企业内部知识库。关于公司战略、SOP、技术文档的问题优先使用此工具。
        返回结果包含文档来源和内容片段。
        """
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant documents found."
        return format_docs(docs)
    
    return retrieve_docs
