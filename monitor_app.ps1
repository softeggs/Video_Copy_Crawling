# 视频抓取系统监控脚本 (Windows PowerShell)
# 功能：检测 Streamlit 进程，若未运行则自动后台启动，并记录日志。

$WorkDir = "d:\code\Video_Copy_Crawling"
$LogFile = "$WorkDir\logs\monitor.log"

# 切换到工作目录
Set-Location -Path $WorkDir

# 检测运行中的 Streamlit 进程 (包含 app.py 参数)
$Process = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*streamlit run*app.py*" }

$now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if ($null -eq $Process) {
    # 如果没在运行，则静默启动
    Add-Content -Path $LogFile -Value "[$now] [Monitor] 检测到应用未在后台运行，正在尝试自动拉起..."
    
    # 使用 Start-Process 并在后台运行 (Hidden)
    # 若环境中有特定虚拟环境，请在此处修改命令，例如: .\venv\Scripts\streamlit run app.py
    Start-Process -FilePath "streamlit" -ArgumentList "run", "app.py" -WindowStyle Hidden -WorkingDirectory $WorkDir
    
    Add-Content -Path $LogFile -Value "[$now] [Monitor] 启动命令已下发."
}
else {
    # 如果在运行，可以记录一次心跳（可选，注释掉以减少日志量）
    # Add-Content -Path $LogFile -Value "[$now] [Monitor] 应用状态：运行中."
}
