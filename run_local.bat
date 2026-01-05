@echo off
setlocal

:: 设置窗口标题，方便后续查找
title EnterpriseBrain-Launcher

echo [INFO] Checking virtual environment...
if not exist ".venv" (
    echo [ERROR] .venv not found! Please run 'python -m venv .venv' first.
    pause
    exit /b 1
)

echo [INFO] Activating venv...
call .venv\Scripts\activate.bat

echo [INFO] Starting ChromaDB Server (Port 8000)...
:: 使用 start /min 在最小化窗口中启动 Chroma
start "ChromaDB-Server" /min cmd /c "chroma run --path ./chroma_db --port 8000"

echo [INFO] Waiting 3 seconds for Chroma to start...
timeout /t 3 /nobreak >nul

echo [INFO] Starting Streamlit App...
streamlit run src/app.py

:: 当 Streamlit 关闭后，清理 Chroma 进程
echo [INFO] Streamlit closed. Cleaning up...
taskkill /fi "WINDOWTITLE eq ChromaDB-Server*" /f >nul 2>&1

echo [SUCCESS] Cleanup done.
pause
