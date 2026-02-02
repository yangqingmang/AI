Write-Host "🚀 Starting Enterprise Brain Pro (RAGFlow Edition) Deployment..." -ForegroundColor Green

# 1. Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Docker is not installed." -ForegroundColor Red
    exit 1
}

# 2. Setup RAGFlow
$RAGFLOW_VERSION = "v0.16.0"
Write-Host "📦 Downloading RAGFlow configuration ($RAGFLOW_VERSION)..."

New-Item -ItemType Directory -Force -Path ragflow_core | Out-Null
Set-Location ragflow_core

try {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/infiniflow/ragflow/${RAGFLOW_VERSION}/docker/docker-compose.yml" -OutFile "docker-compose.base.yml"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/infiniflow/ragflow/${RAGFLOW_VERSION}/docker/.env" -OutFile ".env"
}
catch {
    Write-Host "⚠️ Failed to download RAGFlow config. Check your internet connection." -ForegroundColor Yellow
    Set-Location ..
    exit 1
}

Set-Location ..

# 3. Start RAGFlow
Write-Host "🔥 Starting RAGFlow Core Engine..." -ForegroundColor Cyan
Set-Location ragflow_core
docker-compose -f docker-compose.base.yml up -d
Set-Location ..

Write-Host "⏳ Waiting for RAGFlow to initialize (10s)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# 4. Start Enterprise Brain
Write-Host "🧠 Starting Enterprise Brain Application..." -ForegroundColor Cyan
docker-compose -f docker-compose.ragflow.yml up -d --build

Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "   - Frontend: http://localhost:8501"
