#!/bin/bash

# Enterprise Brain 打包脚本 (Linux/WSL/Git Bash)
VERSION="v1.0"
DIST_DIR="dist/enterprise-brain-$VERSION"
TARGET_FILE="dist/enterprise-brain-$VERSION.tar.gz"

echo -e "\033[0;36m📦 Packaging Enterprise Brain $VERSION...\033[0m"

# 1. 清理旧构建
rm -rf dist
mkdir -p "$DIST_DIR"

# 2. 定义排除模式
# 使用 tar 的 --exclude 功能直接打包
echo "   Creating archive and excluding junk files..."

tar -czf "$TARGET_FILE" \
    --exclude=".venv" \
    --exclude=".git" \
    --exclude=".idea" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="chroma_db" \
    --exclude=".env" \
    --exclude="dist" \
    --exclude="enterprise-brain/data/*" \
    enterprise-brain Dockerfile docker-compose.yml .env.example deploy.sh

# 3. 整理 dist 目录内容 (方便直接解压查看)
mkdir -p "$DIST_DIR"
tar -xzf "$TARGET_FILE" -C "$DIST_DIR"

echo -e "\033[0;32m✅ Package created successfully!\033[0m"
echo -e "📂 Location: $TARGET_FILE"
echo -e "💡 You can now send this .tar.gz file to your client."
