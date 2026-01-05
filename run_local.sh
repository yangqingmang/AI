#!/bin/bash

# 颜色
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Starting Local Development Environment...${NC}"

# 使用子 shell 运行，避免污染当前 shell 的目录
(
    ROOT_DIR=$(pwd)

    # 1. 检查环境
    if [ ! -d ".venv" ]; then
        echo "Error: .venv not found in root."
        exit 1
    fi

    # 2. 启动 ChromaDB (后台)
    echo -e "${GREEN}📦 Starting ChromaDB Server (Port 8000)...${NC}"
    (source .venv/bin/activate && cd enterprise-brain && chroma run --path ./chroma_db --port 8000) &
    CHROMA_PID=$!

    sleep 3

    # 捕获退出信号
    trap "echo '🛑 Stopping ChromaDB...'; kill $CHROMA_PID; exit" INT TERM EXIT

    # 3. 启动 Streamlit
    echo -e "${GREEN}🌐 Starting Streamlit App...${NC}"
    cd enterprise-brain
    ../.venv/bin/python -m streamlit run src/app.py
)
