# FFmpeg 安装脚本（需要管理员权限）

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FFmpeg 安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-NOT $isAdmin) {
    Write-Host "✗ 需要管理员权限" -ForegroundColor Red
    Write-Host ""
    Write-Host "请以管理员身份运行此脚本：" -ForegroundColor Yellow
    Write-Host "1. 右键点击 PowerShell" -ForegroundColor White
    Write-Host "2. 选择'以管理员身份运行'" -ForegroundColor White
    Write-Host "3. 运行: .\install_ffmpeg.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "或者手动安装：" -ForegroundColor Yellow
    Write-Host "choco install ffmpeg -y" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# 检查 Chocolatey
Write-Host "检查 Chocolatey..." -ForegroundColor Yellow
try {
    $null = Get-Command choco -ErrorAction Stop
    Write-Host "✓ Chocolatey 已安装" -ForegroundColor Green
} catch {
    Write-Host "✗ Chocolatey 未安装" -ForegroundColor Red
    Write-Host "正在安装 Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "✓ Chocolatey 安装完成" -ForegroundColor Green
}

Write-Host ""

# 安装 FFmpeg
Write-Host "安装 FFmpeg..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟，请耐心等待..." -ForegroundColor Yellow
Write-Host ""

choco install ffmpeg -y

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ FFmpeg 安装成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "验证安装：" -ForegroundColor Yellow
    ffmpeg -version | Select-String "ffmpeg version"
    Write-Host ""
    Write-Host "请重启终端后继续使用" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✗ FFmpeg 安装失败" -ForegroundColor Red
    Write-Host "请手动安装：https://ffmpeg.org/download.html" -ForegroundColor Yellow
}

Write-Host ""
