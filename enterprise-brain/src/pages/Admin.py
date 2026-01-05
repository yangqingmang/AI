import streamlit as st
import os
import glob
import sys
import shutil

# 将父目录 (src) 加入路径，以便导入同级模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 延迟导入 ingest 避免 import 错误阻塞页面加载
# from ingest import ingest_docs 

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

st.set_page_config(page_title="Knowledge Base Admin", page_icon="⚙️", layout="wide")

# --- 0. 简单的密码保护 ---
# 建议在 .env 中设置 ADMIN_PASSWORD，默认 fallback 为 "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

if "auth" not in st.session_state:
    st.session_state.auth = False

def check_password():
    if st.session_state.password == ADMIN_PASSWORD:
        st.session_state.auth = True
    else:
        st.error("Incorrect password")

if not st.session_state.auth:
    st.title("🔒 Admin Access")
    st.write("Please log in to manage the knowledge base.")
    st.text_input("Enter Admin Password", type="password", key="password", on_change=check_password)
    st.stop() # 停止渲染下面的内容

# --- 以下内容只有登录后可见 ---

st.title("⚙️ Knowledge Base Admin")

# 登出按钮
if st.sidebar.button("Log out"):
    st.session_state.auth = False
    st.rerun()

st.markdown("---")

# 路径配置
DATA_DIR = os.path.join(parent_dir, "../data") # 指向 enterprise-brain/data
DATA_DIR = os.path.abspath(DATA_DIR)

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 辅助函数：触发 Ingest
def run_ingest():
    with st.spinner("🧠 Syncing with Brain (this may take a moment)..."):
        try:
            # 切换工作目录以便 ingest 正确找到 chroma_db
            original_cwd = os.getcwd()
            project_root = os.path.dirname(parent_dir)
            os.chdir(project_root)
            
            # 动态导入，确保每次都运行最新的逻辑
            from ingest import ingest_docs
            ingest_docs()
            
            os.chdir(original_cwd)
            st.cache_resource.clear()
            st.toast("✅ Knowledge Base Synced!", icon="🎉")
        except Exception as e:
            st.error(f"Sync Error: {e}")

# 1. 知识库管理区
st.header("📂 Knowledge Management")

# 获取文件列表
files = glob.glob(os.path.join(DATA_DIR, "*.*"))
# 尝试按时间排序，最新的在前面
try:
    files.sort(key=os.path.getmtime, reverse=True)
except:
    pass

col_left, col_right = st.columns([0.6, 0.4])

with col_left:
    st.subheader(f"Current Documents ({len(files)})")
    
    if not files:
        st.info("No documents found in the library.")
    else:
        # 创建一个整洁的列表视图
        for f in files:
            filename = os.path.basename(f)
            # 使用容器增加视觉分组
            with st.container():
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.text(f"📄 {filename}")
                with c2:
                    # 删除按钮
                    if st.button("🗑️", key=f"del_{filename}", help=f"Delete {filename}"):
                        try:
                            os.remove(f)
                            st.warning(f"Deleted {filename}. Syncing...")
                            run_ingest() # 触发同步，数据库会自动删除对应向量
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete: {e}")
                st.divider()

with col_right:
    st.subheader("📥 Upload New")
    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Upload .md, .txt files", 
            type=["md", "txt"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            if st.button("💾 Save & Sync", type="primary"):
                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    save_path = os.path.join(DATA_DIR, uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.success(f"Saved {len(uploaded_files)} files!")
                run_ingest()
                st.rerun()

    st.markdown("### 🔧 Tools")
    if st.button("🔄 Force Full Resync"):
        run_ingest()
    st.caption("Click this if the database seems out of sync with the file list.")