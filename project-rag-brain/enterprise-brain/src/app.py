import streamlit as st
import requests
import json
import os
import sys
import uuid

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import get_settings

settings = get_settings()

# Backend API Base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Page Config
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🧠",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .stButton button {
        border-radius: 20px;
        border: 1px solid #e0e0e0;
    }
    .stChatMessage {
        border-radius: 10px;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    # --- Sidebar ---
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=60)
        st.title(settings.APP_NAME)
        st.caption(f"Enterprise Knowledge Engine v{settings.APP_VERSION}")
        
        st.markdown("---")
        
        # 1. Pro Mode
        st.subheader("⚙️ Settings")
        pro_mode = st.toggle("Pro Mode (Agent)", value=False, help="Unlock Web Search, Code Execution, and File Management.")
        if pro_mode:
            st.caption("🚀 Agent capabilities enabled")
        
        st.markdown("---")
        
        # 2. Knowledge Base Manager
        st.subheader("📚 Knowledge Base")
        
        # Upload
        uploaded_files = st.file_uploader("Add Documents", accept_multiple_files=True, type=["txt", "md", "pdf"])
        if uploaded_files:
            if st.button("📥 Upload & Index", use_container_width=True):
                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(f"{API_BASE_URL}/upload", files=files)
                        if response.status_code != 200:
                            st.error(f"Failed: {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    progress_bar.progress((i + 1) / len(uploaded_files))
                st.success("Indexing triggered!")
                st.rerun() # Refresh list

        # File List (Feature 1)
        with st.expander("📂 Indexed Files", expanded=True):
            try:
                response = requests.get(f"{API_BASE_URL}/files")
                if response.status_code == 200:
                    files = response.json()
                    if files:
                        for f in files:
                            st.text(f"📄 {f}")
                    else:
                        st.caption("No documents found.")
                else:
                    st.warning("Could not fetch file list.")
            except Exception:
                st.caption("Backend offline")

        st.markdown("---")
        if st.button("🗑️ Reset Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

    # --- Main Chat Area ---
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是你的企业知识助手。你可以问我关于公司政策、技术文档或战略规划的问题。"}
        ]

    # Display Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggestion Chips (Feature 3)
    # Only show if history is empty (or just welcome message)
    if len(st.session_state.messages) <= 1:
        st.markdown("#### 💡 You might want to ask:")
        cols = st.columns(3)
        suggestions = ["咱们公司的远程办公政策是啥？", "如何申请 VPN 权限？", "总结一下最新的战略规划"]
        
        prompt_from_suggestion = None
        for i, col in enumerate(cols):
            if col.button(suggestions[i], key=f"sugg_{i}"):
                prompt_from_suggestion = suggestions[i]

    # Chat Input
    prompt = st.chat_input("Ask anything...")
    
    # Handle Input (Either from text box or suggestion click)
    final_prompt = prompt or prompt_from_suggestion
    
    if final_prompt:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        with st.chat_message("user"):
            st.markdown(final_prompt)

        # Assistant Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            sources = set()
            
            # Chain of Thought UI (Feature 2)
            # We use a status container that updates as we receive tool events
            status_container = st.status("Thinking...", expanded=False)
            
            try:
                payload = {
                    "message": final_prompt, 
                    "pro_mode": pro_mode,
                    "session_id": st.session_state.session_id
                }
                
                with requests.post(f"{API_BASE_URL}/chat/stream", json=payload, stream=True) as r:
                    if r.status_code != 200:
                        st.error(f"Backend Error: {r.status_code} - {r.text}")
                        status_container.update(label="Error", state="error")
                    else:
                        for line in r.iter_lines():
                            if line:
                                decoded_line = line.decode('utf-8')
                                if decoded_line.startswith("data: "):
                                    data_content = decoded_line[len("data: "):]
                                    
                                    if data_content == "[DONE]":
                                        break
                                    
                                    try:
                                        data_json = json.loads(data_content)
                                        
                                        # 1. Token (Text Content)
                                        if "token" in data_json:
                                            full_response += data_json["token"]
                                            message_placeholder.markdown(full_response + "▌")
                                        
                                        # 2. Tool Start (CoT)
                                        elif "tool_start" in data_json:
                                            tool_name = data_json["tool_start"]
                                            tool_input = data_json.get("input", "")
                                            # Update status
                                            status_container.write(f"🛠️ Using tool: **{tool_name}**")
                                            if tool_input:
                                                status_container.caption(f"Input: {tool_input}")
                                        
                                        # 3. Source Citation
                                        elif "source" in data_json:
                                            sources.add(data_json["source"])
                                            
                                        elif "error" in data_json:
                                            st.error(f"AI Error: {data_json['error']}")
                                            
                                    except json.JSONDecodeError:
                                        pass
                
                # Finalize UI
                status_container.update(label="Finished!", state="complete", expanded=False)
                message_placeholder.markdown(full_response)
                
                # Render Sources
                if sources:
                    sources_html = "<div style='font-size: 0.8em; color: gray; margin-top: 10px;'>📚 Sources: "
                    for src in sources:
                         sources_html += f"<span style='background-color: #f0f0f0; padding: 2px 6px; border-radius: 4px; margin-right: 5px;'>{src}</span>"
                    sources_html += "</div>"
                    st.markdown(sources_html, unsafe_allow_html=True)
                    full_response += f"\n\n**Sources:** {', '.join(sources)}"

                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Force rerun if using suggestion to clear button state
                if prompt_from_suggestion:
                    st.rerun()

            except Exception as e:
                st.error(f"Connection Error: {e}")
                status_container.update(label="Connection Failed", state="error")

if __name__ == "__main__":
    main()