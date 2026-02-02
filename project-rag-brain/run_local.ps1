# 本地开发一键启动脚本 (无副作用版)
Write-Host "🚀 Starting Local Development Environment..." -ForegroundColor Cyan

# 保存当前目录
Push-Location

$root = Get-Location

# 1. 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Error "Virtual environment not found in root! Please run 'python -m venv .venv' first."
    Pop-Location
    exit 1
}

# 2. 启动 ChromaDB (后台进程)
Write-Host "📦 Starting ChromaDB Server (Port 8001)..."
$chromaJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    .\.venv\Scripts\activate
    Set-Location enterprise-brain
    chroma run --path ./chroma_db --port 8001
} -ArgumentList $root

# 3. 启动 FastAPI Backend (后台进程)
Write-Host "⚡ Starting FastAPI Backend (Port 8000)..."
$apiJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    .\.venv\Scripts\activate
    Set-Location enterprise-brain
    # 设置环境变量以连接到端口 8001 的 Chroma
    $env:CHROMA_SERVER_PORT = 8001
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
} -ArgumentList $root

# 等待启动
Start-Sleep -Seconds 5

# 4. 启动 Streamlit
Write-Host "🌐 Starting Streamlit App..."
try {
    Set-Location enterprise-brain
    # 设置 API 地址指向 FastAPI 所在的 8000 端口
    $env:API_BASE_URL = "http://localhost:8000/api/v1"
    ..\.venv\Scripts\python.exe -m streamlit run src/app.py
}
finally {
    # 5. 清理与恢复
    Write-Host "🛑 Stopping Servers..." -ForegroundColor Yellow
    Stop-Job $chromaJob
    Stop-Job $apiJob
    Remove-Job $chromaJob
    Remove-Job $apiJob
    
    # 恢复目录
    Pop-Location
    Write-Host "✅ Cleanup complete. Directory restored." -ForegroundColor Green
}
