#!/bin/bash

# Enterprise Brain 自动化部署脚本
# 适用系统: Ubuntu, CentOS, Debian

set -e # 遇错即停

# 颜色定义
INFO='\033[0;36m'
SUCCESS='\033[0;32m'
WARN='\033[1;33m'
ERROR='\033[0;31m'
NC='\033[0m'

echo -e "${INFO}>>> Starting Enterprise Brain Deployment...${NC}"

# 1. 环境检查: Docker
if ! [ -x "$(command -v docker)" ]; then
    echo -e "${WARN}Workflow: Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

# 2. 环境检查: Docker Compose
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 3. 配置密钥 (交互式)
if [ ! -f .env ]; then
    echo -e "${INFO}>>> Initializing .env from template...${NC}"
    cp .env.example .env
    
    echo -e "${WARN}Please enter your DeepSeek API Key (starts with sk-):${NC}"
    read -p "API Key: " USER_API_KEY
    
    if [ -n "$USER_API_KEY" ]; then
        # 兼容 Linux 不同发行版的 sed 行为
        sed -i "s|^DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=$USER_API_KEY|" .env
        echo -e "${SUCCESS}API Key configured.${NC}"
    else
        echo -e "${WARN}No API Key entered.${NC}"
        read -p "Do you want to continue anyway? The app might not work without an API Key. (y/n) " CONT
        if [[ "$CONT" != "y" && "$CONT" != "Y" ]]; then
            echo "Aborting deployment."
            exit 1
        fi
    fi
    
    echo -e "${WARN}Set Admin Password for the Knowledge Base UI (default: admin):${NC}"
    read -p "Password: " USER_PWD
    if [ -n "$USER_PWD" ]; then
        # 如果 .env.example 里没有这个变量，就追加；如果有就替换
        if grep -q "ADMIN_PASSWORD" .env; then
            sed -i "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=$USER_PWD|" .env
        else
            echo "" >> .env
            echo "ADMIN_PASSWORD=$USER_PWD" >> .env
        fi
        echo -e "${SUCCESS}Admin password set.${NC}"
    fi
fi

# 4. 目录与权限准备
echo -e "${INFO}>>> Preparing directories...${NC}"
mkdir -p data chroma_db
chmod 777 chroma_db # 确保容器有权写入持久化数据库

# 5. 启动服务
echo -e "${INFO}>>> Building and starting containers...${NC}"
$DOCKER_COMPOSE up -d --build

# 6. 状态验证
echo -e "${INFO}>>> Waiting for service to stabilize...${NC}"
sleep 5
if [ "$(docker ps -q -f name=enterprise_brain_v1)" ]; then
    echo -e "${SUCCESS}==============================================${NC}"
    echo -e "${SUCCESS}✅ DEPLOYMENT COMPLETE!${NC}"
    echo -e "${SUCCESS}==============================================${NC}"
    # 尝试获取公网IP，如果失败则显示内网IP或 localhost
    PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")
    echo -e "URL: http://$PUBLIC_IP:8501"
    echo -e "Logs: $DOCKER_COMPOSE logs -f"
else
    echo -e "${ERROR}❌ Deployment failed. Check logs with 'docker logs enterprise_brain_v1'${NC}"
    exit 1
fi
