# Enterprise Brain 打包脚本 (Windows)

$Version = "v1.0"
$DistDir = "dist\enterprise-brain-$Version"
$ZipFile = "dist\enterprise-brain-$Version.zip"

Write-Host "📦 Packaging Enterprise Brain $Version..." -ForegroundColor Cyan

# 1. 清理旧构建
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
New-Item -ItemType Directory -Path $DistDir -Force | Out-Null

# 2. 复制核心文件
# 排除 .venv, .git, chroma_db (本地测试数据不发给客户), __pycache__
$ExcludeList = @(".venv", ".git", ".idea", "__pycache__", "chroma_db", ".env", "dist")

Write-Host "   Copying files..."
Copy-Item "enterprise-brain" -Destination $DistDir -Recurse
Copy-Item "Dockerfile" -Destination $DistDir
Copy-Item "docker-compose.yml" -Destination $DistDir
Copy-Item ".env.example" -Destination $DistDir
Copy-Item "deploy.sh" -Destination $DistDir

# 3. 清理目标目录中的垃圾文件 (递归删除 pycache 等)
Get-ChildItem -Path $DistDir -Include "__pycache__", "*.pyc", ".venv", ".git" -Recurse | Remove-Item -Recurse -Force

# 4. 压缩
Write-Host "   Zipping..."
Compress-Archive -Path "$DistDir\*" -DestinationPath $ZipFile

Write-Host "✅ Package created successfully!" -ForegroundColor Green
Write-Host "📂 Location: $ZipFile"
