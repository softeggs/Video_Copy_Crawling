# 短视频内容情报提取系统 - 环境配置脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  短视频内容情报提取系统 - 环境配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 FFmpeg
Write-Host "[1/4] 检查 FFmpeg..." -ForegroundColor Yellow
try {
    $null = Get-Command ffmpeg -ErrorAction Stop
    Write-Host "  OK FFmpeg 已安装" -ForegroundColor Green
    ffmpeg -version 2>&1 | Select-String "ffmpeg version" | Write-Host
} catch {
    Write-Host "  X FFmpeg 未安装" -ForegroundColor Red
    Write-Host "  请手动安装 FFmpeg:" -ForegroundColor Yellow
    Write-Host "    方式1: choco install ffmpeg -y (需要管理员权限)" -ForegroundColor Cyan
    Write-Host "    方式2: 查看 install_ffmpeg.md 文件" -ForegroundColor Cyan
}

Write-Host ""

# 2. 安装 Python 依赖
Write-Host "[2/4] 安装 Python 依赖包..." -ForegroundColor Yellow
Write-Host "  这可能需要几分钟，请耐心等待..." -ForegroundColor Yellow

pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Python 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "  X 依赖安装失败" -ForegroundColor Red
}

Write-Host ""

# 3. 创建 .env 文件
Write-Host "[3/4] 配置环境变量..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "  .env 文件已存在" -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "  OK 已创建 .env 文件" -ForegroundColor Green
    Write-Host "  请编辑 .env 文件，填入你的 API 密钥" -ForegroundColor Yellow
}

Write-Host ""

# 4. 创建必要的目录
Write-Host "[4/4] 创建工作目录..." -ForegroundColor Yellow

$dirs = @("downloads", "outputs", "logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  OK 创建目录: $dir" -ForegroundColor Green
    } else {
        Write-Host "  OK 目录已存在: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 编辑 .env 文件，填入你的 API 密钥" -ForegroundColor White
Write-Host "2. 如果 FFmpeg 未安装，请先安装" -ForegroundColor White
Write-Host "3. 运行命令启动应用: streamlit run app.py" -ForegroundColor White
Write-Host ""
