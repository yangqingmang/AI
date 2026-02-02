#!/bin/bash

# Enterprise Brain 最终版自动化部署脚本 (代码/数据/配置彻底分离)
# 架构: 
#   ../.env        (配置)
#   ../data/       (数据)
#   ../chroma_db/  (数据库)
#   ./             (代码)

set -e

# 颜色定义
INFO='\033[0;36m'
SUCCESS='\033[0;32m'
WARN='\033[1;33m'
ERROR='\033[0;31m'
NC='\033[0m'

echo -e "${INFO}>>> Starting Enterprise Brain Ultimate Deployment...${NC}"

# 1. 环境检查与网络优化
git config --global http.version HTTP/1.1
git config --global http.sslVerify false

# 2. 基础环境检查: Git
if ! [ -x "$(command -v git)" ]; then
    echo -e "${WARN}Installing Git...${NC}"
    if [ -f /etc/redhat-release ]; then sudo dnf install -y git || sudo yum install -y git
    elif [ -f /etc/debian_version ]; then sudo apt-get update && sudo apt-get install -y git
    fi
fi

# 3. Docker 环境检查
if ! [ -x "$(command -v docker)" ]; then
    echo -e "${ERROR}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# 3. 同步最新代码 (使用强制重置模式)
echo -e "${INFO}>>> Syncing code...${NC}"
GITHUB_REPO="https://github.com/yangqingmang/AI.git"
PROXY_REPO="https://ghproxy.net/https://github.com/yangqingmang/AI.git"

sync_code() {
    local repo_url=$1
    if [ -d ".git" ]; then
        git remote set-url origin "$repo_url"
        git fetch --progress origin master
        git reset --hard origin/master
        git clean -fd
    else
        git init && git remote add origin "$repo_url"
        git fetch --progress origin master
        git reset --hard origin/master
    fi
}

sync_code "$GITHUB_REPO" || sync_code "$PROXY_REPO" || { echo -e "${ERROR}Sync failed${NC}"; exit 1; }

# 4. 配置与数据分离逻辑 (核心改进)
echo -e "${INFO}>>> Managing Config and Data separation...${NC}"

# 确保上一级目录有配置和数据文件夹
PARENT_DIR=".."
CONFIG_FILE="${PARENT_DIR}/.env"
DATA_DIR="${PARENT_DIR}/data"
DB_DIR="${PARENT_DIR}/chroma_db"

mkdir -p "$DATA_DIR" "$DB_DIR"
chmod 777 "$DB_DIR" "$DATA_DIR"

# 如果上一级没有 .env，则从模板复制
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${WARN}Initializing config in ${CONFIG_FILE}...${NC}"
    cp .env.example "$CONFIG_FILE"
    
    echo -e "${WARN}Please enter your DeepSeek API Key:${NC}"
    read -p "API Key: " USER_API_KEY
    if [ -n "$USER_API_KEY" ]; then
        sed -i "s|^DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=$USER_API_KEY|" "$CONFIG_FILE"
    fi
fi

# 5. 硬件智能探测
CPU_CORES=$(nproc)
if [ "$CPU_CORES" -gt 1 ]; then
    sed -i "/^OMP_NUM_THREADS=/d" "$CONFIG_FILE"
    echo "OMP_NUM_THREADS=$CPU_CORES" >> "$CONFIG_FILE"
fi

# 6. 启动服务 (强制关联上一级的 .env)
echo -e "${INFO}>>> Building and starting containers...${NC}"

# 自动处理 Docker 镜像加速
if [ ! -f /etc/docker/daemon.json ]; then
    mkdir -p /etc/docker
    echo '{"registry-mirrors": ["https://docker.m.daocloud.io"]}' > /etc/docker/daemon.json
    systemctl restart docker || true
fi

docker compose --env-file "$CONFIG_FILE" up -d --build

echo -e "${SUCCESS}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${INFO}Code:   $(pwd)${NC}"
echo -e "${INFO}Config: ${CONFIG_FILE}${NC}"
echo -e "${INFO}Data:   ${DATA_DIR}${NC}"
echo -e "URL: http://$(curl -s ifconfig.me || echo "localhost"):8501"