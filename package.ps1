# Enterprise Brain 打包脚本 (Windows)

$Version = "v1.0"
$DistDir = "dist\enterprise-brain-$Version"
$ZipFile = "dist\enterprise-brain-$Version.zip"

Write-Host "📦 Packaging Enterprise Brain $Version..." -ForegroundColor Cyan

# 1. 清理旧构建
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
New-Item -ItemType Directory -Path $DistDir -Force | Out-Null

# 2. 复制核心文件
# 使用 Robocopy 高效复制并排除不需要的大文件夹 (.venv, .git, chroma_db 等)
Write-Host "   Copying files..."
$RoboDest = Join-Path $DistDir "enterprise-brain"
robocopy "enterprise-brain" $RoboDest /E /XD .venv .git .idea __pycache__ chroma_db /XF .env *.pyc *.log chat_history.db /NFL /NDL /NJH /NJS
if ($LASTEXITCODE -le 7) { $global:LastExitCode = 0 } # Robocopy success codes are 0-7

Copy-Item "Dockerfile" -Destination $DistDir
Copy-Item "docker-compose.yml" -Destination $DistDir
Copy-Item ".env.example" -Destination $DistDir
Copy-Item "deploy.sh" -Destination $DistDir

# 3. 清理目标目录中的垃圾文件 (辅助清理)
Get-ChildItem -Path $DistDir -Include "__pycache__", "*.pyc" -Recurse | Remove-Item -Recurse -Force

# 4. 压缩
Write-Host "   Zipping..."
Compress-Archive -Path "$DistDir\*" -DestinationPath $ZipFile

Write-Host "✅ Package created successfully!" -ForegroundColor Green
Write-Host "📂 Location: $ZipFile"
