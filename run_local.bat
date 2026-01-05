@echo off
setlocal

:: 保存当前目录
pushd .

echo [INFO] Checking virtual environment...
if not exist ".venv" (
    echo [ERROR] .venv not found in root!
    popd
    pause
    exit /b 1
)

echo [INFO] Starting ChromaDB Server (Port 8000)...
start "ChromaDB-Server" /min cmd /c "call .venv\Scripts\activate.bat && cd enterprise-brain && chroma run --path ./chroma_db --port 8000"

echo [INFO] Waiting 3 seconds for Chroma to start...
timeout /t 3 /nobreak >nul

echo [INFO] Starting Streamlit App...
cd enterprise-brain
..\.venv\Scripts\python.exe -m streamlit run src/app.py

echo [INFO] Streamlit closed. Cleaning up...
taskkill /fi "WINDOWTITLE eq ChromaDB-Server*" /f >nul 2>&1

:: 恢复目录
popd
echo [SUCCESS] Cleanup done. Directory restored.
pause
