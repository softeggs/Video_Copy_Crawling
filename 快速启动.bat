@echo off
chcp 65001
title 视频抓取系统 - 快速启动
cd /d "%~dp0"

echo ==========================================
echo    视频抓取与分析系统 (Video Copy Crawling)
echo ==========================================
echo.
echo [INFO] 正在启动 Streamlit Web 界面...
echo [HINT] 启动后请访问 http://localhost:8501
echo.

streamlit run app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] 程序异常启动失败，请检查依赖环境。
    pause
)
