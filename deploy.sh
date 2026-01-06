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

# -1. 基础环境检查: Git
if ! [ -x "$(command -v git)" ]; then
    echo -e "${WARN}Git not found. Installing...${NC}"
    if [ -f /etc/redhat-release ]; then
        sudo dnf install -y git || sudo yum install -y git
    elif [ -f /etc/debian_version ]; then
        sudo apt-get update && sudo apt-get install -y git
    else
        # Fallback or other distros
        if [ -x "$(command -v apk)" ]; then
            sudo apk add git
        elif [ -x "$(command -v pacman)" ]; then
            sudo pacman -S --noconfirm git
        else
             echo -e "${ERROR}Unsupported OS for auto-installing Git. Please install git manually.${NC}"
             exit 1
        fi
    fi
fi

# -0.5. 优化网络配置 (解决 HTTP/2 stream 错误)
if [ -x "$(command -v git)" ]; then
    git config --global http.version HTTP/1.1
fi

# 0. 同步最新代码
echo -e "${INFO}>>> Checking for updates...${NC}"
GITHUB_REPO="https://github.com/yangqingmang/AI.git"
PROXY_REPO="https://ghproxy.net/https://github.com/yangqingmang/AI.git"

sync_code() {
    local repo_url=$1
    echo -e "${INFO}Attempting to sync from: ${repo_url}...${NC}"
    
    # 配置 Git 临时参数：15秒连接超时，开启进度
    if [ -d ".git" ]; then
        git remote set-url origin "$repo_url"
        git fetch --progress --connect-timeout 15 origin master
        git reset --hard origin/master
    else
        git init
        git remote add origin "$repo_url" || git remote set-url origin "$repo_url"
        git fetch --progress --connect-timeout 15 origin master
        git reset --hard origin/master
    fi
}

if ! sync_code "$GITHUB_REPO"; then
    echo -e "${WARN}Direct access to GitHub failed. Trying via Acceleration Proxy...${NC}"
    if ! sync_code "$PROXY_REPO"; then
        echo -e "${ERROR}All sync attempts failed. Please check your internet connection.${NC}"
        exit 1
    fi
fi
echo -e "${SUCCESS}Code synced successfully.${NC}"

echo -e "${INFO}>>> Starting Enterprise Brain Deployment...${NC}"

# 1. 环境检查: Docker
if ! [ -x "$(command -v docker)" ]; then
    echo -e "${WARN}Workflow: Docker not found. Installing...${NC}"
    # 原官方脚本安装方式 (因国内网络连接 get.docker.com 不稳定，已注释)
    # curl -fsSL https://get.docker.com | sh
    
    # 针对国内网络环境的优化安装方案
    if [ -f /etc/redhat-release ]; then
        # Rocky Linux / CentOS / RHEL (使用阿里云 yum 源)
        echo -e "${INFO}Detected RHEL-based system. Using Aliyun mirror for installation...${NC}"
        sudo dnf -y install dnf-plugins-core
        sudo dnf config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
        sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    # Ubuntu / Debian 等其他系统 (尝试使用阿里云镜像参数)
        # 如果 get.docker.com 完全无法访问，请手动替换为 apt/yum 源安装
        echo -e "${INFO}Installing Docker via official script with Aliyun mirror (this may take a few minutes)...${NC}"
        curl -fL https://get.docker.com | bash -s docker --mirror Aliyun
    fi
    
    systemctl enable --now docker
fi

# 2. 环境检查: Docker Compose
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 2.5. 配置 Docker 镜像加速 (针对国内网络)
if [ ! -f /etc/docker/daemon.json ]; then
    echo -e "${INFO}>>> Configuring Docker Registry Mirrors for China...${NC}"
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ]
}
EOF
    systemctl daemon-reload
    systemctl restart docker
    echo -e "${SUCCESS}Docker mirrors configured.${NC}"
else
    echo -e "${INFO}Docker daemon.json already exists. Skipping mirror config.${NC}"
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
echo -e "${INFO}>>> Preparing directories and checking resources...${NC}"

# 性能优化: 检查 Swap
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
TOTAL_SWAP=$(free -m | awk '/^Swap:/{print $2}')
if [ $((TOTAL_MEM + TOTAL_SWAP)) -lt 3500 ]; then
    echo -e "${WARN}Low memory detected (RAM+Swap < 3.5GB). Attempting to enable 2GB Swap for stability...${NC}"
    if [ ! -f /swapfile ]; then
        sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo "/swapfile swap swap defaults 0 0" | sudo tee -a /etc/fstab
        echo -e "${SUCCESS}Swap enabled.${NC}"
    fi
fi

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
