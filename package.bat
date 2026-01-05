@echo off
setlocal enabledelayedexpansion

set VERSION=v1.2
set DIST_DIR=dist\enterprise-brain-%VERSION%
set ZIP_FILE=dist\enterprise-brain-%VERSION%.zip

echo [INFO] Packaging Enterprise Brain %VERSION%...

:: 1. 清理旧构建
if exist dist rmdir /s /q dist
mkdir %DIST_DIR%

:: 2. 复制文件
echo [INFO] Copying files...
xcopy enterprise-brain %DIST_DIR%\enterprise-brain\ /E /I /Y /Q >nul
copy Dockerfile %DIST_DIR%\ >nul
copy docker-compose.yml %DIST_DIR%\ >nul
copy .env.example %DIST_DIR%\ >nul
copy deploy.sh %DIST_DIR%\ >nul

:: 3. 清理垃圾文件 (递归删除 .venv, __pycache__)
echo [INFO] Cleaning junk files...
cd %DIST_DIR%
for /d /r %%d in (__pycache__ .venv .git .idea chroma_db) do (
    if exist "%%d" rmdir /s /q "%%d"
)
cd ..\..

:: 4. 压缩 (使用 Windows 10/11 自带的 tar)
echo [INFO] Zipping...
cd dist
tar -a -c -f enterprise-brain-%VERSION%.zip enterprise-brain-%VERSION%
cd ..

echo [SUCCESS] Package created at %ZIP_FILE%
pause
