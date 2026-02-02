#!/bin/bash

# Enterprise Brain Pro Deployment Script
# Integrates Enterprise Brain with RAGFlow

echo "🚀 Starting Enterprise Brain Pro (RAGFlow Edition) Deployment..."

# 1. Check Prerequisites
if [ -z "$(command -v docker)" ]; then
    echo "❌ Error: Docker is not installed."
    exit 1
fi

# 2. Setup RAGFlow Configuration
RAGFLOW_VERSION="v0.16.0" # Lock version for stability
echo "📦 Downloading RAGFlow configuration ($RAGFLOW_VERSION)..."

# Create a clean directory for RAGFlow
mkdir -p ragflow_core
cd ragflow_core

# Download official docker-compose from RAGFlow repo
curl -sSL https://raw.githubusercontent.com/infiniflow/ragflow/${RAGFLOW_VERSION}/docker/docker-compose.yml -o docker-compose.base.yml
curl -sSL https://raw.githubusercontent.com/infiniflow/ragflow/${RAGFLOW_VERSION}/docker/.env -o .env

# Adjust .env for RAGFlow (e.g., set ports if needed)
# sed -i 's/RAGFLOW_PORT=80/RAGFLOW_PORT=9380/g' .env

cd ..

# 3. Merge Environments
echo "🔗 Configuring network..."
# Ensure the network exists
docker network create ragflow-network 2>/dev/null || true

# 4. Start RAGFlow Core
echo "🔥 Starting RAGFlow Core Engine..."
cd ragflow_core
docker-compose -f docker-compose.base.yml up -d
cd ..

echo "⏳ Waiting for RAGFlow to initialize (30s)..."
sleep 30

# 5. Start Enterprise Brain
echo "🧠 Starting Enterprise Brain Application..."
# We use the override file to link to the network created by RAGFlow
docker-compose -f docker-compose.ragflow.yml up -d --build

echo "✅ Deployment Complete!"
echo "   - Frontend: http://localhost:8501"
echo "   - RAGFlow Console: http://localhost:80 (Default)"
echo "⚠️  Important: Please generate an API Key in RAGFlow Console and update your .env file."
