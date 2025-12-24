# 短视频内容情报提取系统

全自动化的视频内容分析与飞书同步工具

## 功能特性

- 🎬 多平台视频抓取（抖音/B站/小红书）
- 🎙️ 高精度语音识别（Whisper）
- 🤖 多 AI 提供商支持（OpenAI / Gemini）
- 🔄 可选 AI 润色模式（支持纯语音识别）
- ✨ AI 智能润色与结构化
- 📊 飞书多维表格自动同步
- ⚡ 异步并发处理

## 技术栈

- Python 3.9+
- yt-dlp (视频抓取)
- FFmpeg (音频处理)
- OpenAI Whisper (语音识别)
- LangChain + OpenAI (AI 处理)
- Feishu SDK (飞书集成)
- Streamlit (Web 界面)

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量（复制 .env.example 为 .env）：
```bash
# 选择 AI 提供商（二选一）
OPENAI_API_KEY=your_openai_key
# 或
GEMINI_API_KEY=your_gemini_key

AI_PROVIDER=openai  # 或 gemini
ENABLE_AI_POLISH=true  # 或 false（仅语音识别）

# 可选：飞书配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_BITABLE_APP_TOKEN=your_bitable_token
FEISHU_BITABLE_TABLE_ID=your_table_id
```

详细配置说明：查看 `AI_PROVIDERS.md`

3. 启动应用：
```bash
streamlit run app.py
```

## 项目结构

```
├── app.py                 # Streamlit 主界面
├── core/
│   ├── downloader.py     # 视频下载模块
│   ├── audio_processor.py # 音频处理模块
│   ├── transcriber.py    # 语音识别模块
│   ├── ai_processor.py   # AI 润色模块
│   └── feishu_sync.py    # 飞书同步模块
├── utils/
│   ├── config.py         # 配置管理
│   └── logger.py         # 日志工具
├── requirements.txt
└── .env.example
```
