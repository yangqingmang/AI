#!/bin/bash

# 颜色
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Starting Local Development Environment...${NC}"

# 1. 激活虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: .venv not found."
    exit 1
fi

# 2. 启动 ChromaDB (后台)
echo -e "${GREEN}📦 Starting ChromaDB Server (Port 8000)...${NC}"
chroma run --path ./chroma_db --port 8000 &
CHROMA_PID=$!

# 等待启动
sleep 3

# 捕获退出信号 (Ctrl+C)，确保杀掉 Chroma 进程
trap "echo '🛑 Stopping ChromaDB...'; kill $CHROMA_PID; exit" INT TERM EXIT

# 3. 启动 Streamlit
echo -e "${GREEN}🌐 Starting Streamlit App...${NC}"
streamlit run src/app.py
