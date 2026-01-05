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
Write-Host "📦 Starting ChromaDB Server (Port 8000)..."
$chromaJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    .\.venv\Scripts\activate
    Set-Location enterprise-brain
    chroma run --path ./chroma_db --port 8000
} -ArgumentList $root

# 等待启动
Start-Sleep -Seconds 3

# 3. 启动 Streamlit
Write-Host "🌐 Starting Streamlit App..."
try {
    Set-Location enterprise-brain
    ..\.venv\Scripts\python.exe -m streamlit run src/app.py
}
finally {
    # 4. 清理与恢复
    Write-Host "🛑 Stopping ChromaDB Server..." -ForegroundColor Yellow
    Stop-Job $chromaJob
    Remove-Job $chromaJob
    
    # 恢复目录
    Pop-Location
    Write-Host "✅ Cleanup complete. Directory restored." -ForegroundColor Green
}
