# 本地开发一键启动脚本
Write-Host "🚀 Starting Local Development Environment..." -ForegroundColor Cyan

# 1. 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Error "Virtual environment not found! Please run 'python -m venv .venv' first."
    exit 1
}

# 2. 启动 ChromaDB (后台进程)
Write-Host "📦 Starting ChromaDB Server (Port 8000)..."
$chromaJob = Start-Job -ScriptBlock {
    param($cwd)
    Set-Location $cwd
    .\.venv\Scripts\activate
    chroma run --path ./chroma_db --port 8000
} -ArgumentList (Get-Location)

# 等待几秒让 Chroma 启动
Start-Sleep -Seconds 3

# 3. 启动 Streamlit
Write-Host "🌐 Starting Streamlit App..."
try {
    .\.venv\Scripts\streamlit run src/app.py
}
finally {
    # 4. 清理：当 Streamlit 关闭时，停止 Chroma
    Write-Host "🛑 Stopping ChromaDB Server..." -ForegroundColor Yellow
    Stop-Job $chromaJob
    Remove-Job $chromaJob
    Write-Host "✅ Cleanup complete." -ForegroundColor Green
}
