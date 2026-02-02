import os
import argparse
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

# 配置路径
DB_DIR = "chroma_db"

def query_brain(question: str):
    # 1. 初始化 Embedding 模型 (必须与 ingest 时一致)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 2. 加载向量数据库
    vector_store = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )

    # 3. 检索 (Retrieval)
    print(f"🔍 Searching brain for: '{question}'...")
    # k=3 表示找 3 个最相关的片段
    results = vector_store.similarity_search(question, k=3)
    
    if not results:
        print("❌ No relevant information found in the brain.")
        return

    # 将检索到的片段拼接成 Context
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
    
    # 4. 构建 Prompt (RAG 核心)
    # 强制 AI 扮演专家角色，并只依据 Context 回答
    prompt_template = ChatPromptTemplate.from_template("""
    你是一个资深的 AI 战略顾问。请基于以下的【上下文信息】，回答用户的【问题】。
    
    规则：
    1. 如果上下文中没有答案，请直接说“我的知识库中没有相关信息”，不要编造。
    2. 回答要专业、简洁，像工程师对工程师说话。
    3. 引用上下文中的关键数据或观点来支持你的回答。

    【上下文信息】：
    {context}

    【问题】：
    {question}
    """)

    # 5. 调用 LLM (DeepSeek)
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL_NAME", "deepseek-chat"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
        temperature=0.1  # 低温模式，确保准确性
    )

    # 6. 生成回答
    chain = prompt_template | llm
    print("🤖 Thinking...")
    response = chain.invoke({"context": context_text, "question": question})

    print("\n" + "="*50)
    print(f"💡 Answer:\n{response.content}")
    print("="*50 + "\n")
    
    # 调试：显示引用来源
    print("📚 Sources used:")
    for doc in results:
        source = doc.metadata.get('source', 'Unknown')
        print(f" - {source}")

if __name__ == "__main__":
    # 支持命令行参数
    parser = argparse.ArgumentParser(description="Ask the Enterprise Brain")
    parser.add_argument("question", type=str, nargs="?", help="The question to ask", default="What is the strategy for Week 1?")
    args = parser.parse_args()
    
    query_brain(args.question)
