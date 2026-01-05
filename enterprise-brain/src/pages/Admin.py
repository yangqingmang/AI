import streamlit as st
import os
import glob
import sys

# 将父目录 (src) 加入路径，以便导入同级模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from ingest import ingest_docs
except ImportError:
    st.error("Failed to import ingest module. Check sys.path.")

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

st.set_page_config(page_title="Knowledge Base Admin", page_icon="⚙️", layout="wide")

st.title("⚙️ Knowledge Base Admin")
st.markdown("---")

# 路径配置
DATA_DIR = os.path.join(parent_dir, "../data") # 指向 enterprise-brain/data
DATA_DIR = os.path.abspath(DATA_DIR)

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 1. 知识库状态
st.header("📂 Current Documents")
files = glob.glob(os.path.join(DATA_DIR, "*.*"))

col1, col2 = st.columns([3, 1])
with col1:
    if files:
        st.info(f"📚 Total Documents: {len(files)}")
        with st.expander("📄 View File List"):
            for f in files:
                st.code(os.path.basename(f), language="text")
    else:
        st.warning("No documents found in knowledge base.")

with col2:
    if st.button("🔄 Force Re-build Brain"):
        with st.spinner("🧠 Ingesting documents..."):
            try:
                # 切换工作目录以便 ingest 正确找到 chroma_db
                # (ingest.py 默认假设在项目根目录运行，这里做一个兼容处理)
                original_cwd = os.getcwd()
                project_root = os.path.dirname(parent_dir)
                os.chdir(project_root)
                
                ingest_docs()
                
                # 恢复目录
                os.chdir(original_cwd)
                
                # 清除 Streamlit 缓存，让 app.py 重新加载最新数据
                st.cache_resource.clear()
                st.success("✅ Brain updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# 2. 上传区域
st.header("📥 Upload New Knowledge")
uploaded_files = st.file_uploader(
    "Upload .md, .txt files to the knowledge base", 
    type=["md", "txt"], 
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("💾 Save & Process"):
        progress_bar = st.progress(0)
        for i, uploaded_file in enumerate(uploaded_files):
            # 保存文件
            save_path = os.path.join(DATA_DIR, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.success(f"Saved {len(uploaded_files)} files!")
        
        # 自动触发重建
        with st.spinner("🧠 Auto-updating Brain..."):
            original_cwd = os.getcwd()
            project_root = os.path.dirname(parent_dir)
            os.chdir(project_root)
            ingest_docs()
            os.chdir(original_cwd)
            st.cache_resource.clear()
        
        st.success("✅ Knowledge base updated!")
        st.rerun()
