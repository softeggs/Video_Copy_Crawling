# 项目结构说明

## 📁 目录结构

```
Video_Copy_Crawling/
├── 📄 核心文件
│   ├── app.py                          # Streamlit 主应用
│   ├── requirements.txt                # Python 依赖
│   ├── setup.ps1                       # Windows 安装脚本
│   ├── .env                           # 环境变量配置（需自行创建）
│   ├── .env.example                   # 环境变量示例
│   └── .gitignore                     # Git 忽略文件
│
├── 📦 核心模块
│   ├── core/                          # 核心功能模块
│   │   ├── downloader.py             # 视频下载器（支持 B站/小红书/抖音）
│   │   ├── audio_processor.py        # 音频处理
│   │   ├── transcriber.py            # 语音识别（Whisper）
│   │   ├── ai_processor.py           # AI 润色（OpenAI/Gemini）
│   │   ├── feishu_sync.py            # 飞书同步
│   │   └── pipeline.py               # 处理流水线
│   │
│   └── utils/                         # 工具模块
│       ├── config.py                 # 配置管理
│       ├── logger.py                 # 日志工具
│       ├── platform_detector.py      # 平台检测器
│       ├── url_cleaner.py            # URL 清理工具
│       └── douyin_helper.py          # 抖音下载辅助
│
├── 📚 文档
│   ├── README.md                      # 项目说明
│   ├── QUICK_START.md                 # 快速开始指南
│   ├── SETUP_GUIDE.md                 # 详细安装指南
│   ├── AI_PROVIDERS.md                # AI 提供商配置
│   ├── AI失败自动跳过功能说明.md      # AI 降级机制
│   ├── Cookies使用完整指南.md         # Cookies 完整指南
│   ├── Cookies导出指南.md             # Cookies 导出方法
│   ├── URL清理功能说明.md             # URL 清理功能
│   ├── 平台识别和分平台Cookies功能说明.md  # 平台识别说明
│   ├── 前端Cookies使用指南.md         # 前端 Cookies 使用
│   └── install_ffmpeg.md              # FFmpeg 安装指南
│
├── 🗂️ 数据目录
│   ├── downloads/                     # 下载的视频和音频
│   ├── outputs/                       # 生成的 Markdown 笔记
│   └── logs/                          # 日志文件
│
└── 🔐 配置文件
    ├── cookies_bilibili.txt           # B站 Cookies
    ├── cookies_xiaohongshu.txt        # 小红书 Cookies
    ├── cookies_douyin.txt             # 抖音 Cookies
    └── cookies.txt                    # 通用 Cookies（可选）
```

## 🎯 核心功能模块说明

### 1. app.py - 主应用
- Streamlit Web 界面
- 用户交互
- 配置管理
- 进度显示

### 2. core/ - 核心功能

#### downloader.py
- 视频下载
- 平台检测（B站/小红书/抖音）
- 自动选择下载方式
  - B站/小红书：yt-dlp
  - 抖音：SaveTik API
- 音频提取

#### audio_processor.py
- 音频格式转换
- 音频优化（降噪、标准化）
- 为 ASR 优化

#### transcriber.py
- Whisper 语音识别
- 多模型支持（tiny/base/small/medium/large）
- 参数优化

#### ai_processor.py
- AI 内容润色
- 多提供商支持（OpenAI/Gemini）
- 自动降级机制
- Markdown 生成

#### feishu_sync.py
- 飞书多维表格同步
- 自动创建记录
- 错误处理

#### pipeline.py
- 完整处理流程编排
- 进度管理
- 错误处理
- 文件清理

### 3. utils/ - 工具模块

#### platform_detector.py
- 平台自动识别
- 域名匹配
- Cookies 文件管理
- Referer 管理

#### url_cleaner.py
- URL 参数清理
- 敏感信息移除
- 保守/深度清理模式
- 视频 ID 提取

#### douyin_helper.py
- 抖音 SaveTik API 集成
- HTML 解析
- 下载链接提取
- 视频下载

#### config.py
- 环境变量加载
- 配置管理
- 路径管理

#### logger.py
- 日志配置
- 文件日志
- 控制台日志

## 🔧 配置文件

### .env
```env
# AI 配置
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
AI_PROVIDER=gemini
ENABLE_AI_POLISH=true

# Whisper 配置
WHISPER_MODEL=base

# 飞书配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_BITABLE_APP_TOKEN=your_token
FEISHU_BITABLE_TABLE_ID=your_table_id
```

### Cookies 文件
- `cookies_bilibili.txt` - B站登录 Cookies
- `cookies_xiaohongshu.txt` - 小红书登录 Cookies
- `cookies_douyin.txt` - 抖音登录 Cookies

格式：Netscape HTTP Cookie File

## 📊 数据流程

```
用户输入 URL
    ↓
平台检测 (platform_detector)
    ↓
URL 清理 (url_cleaner)
    ↓
视频下载 (downloader)
    ├─ B站/小红书 → yt-dlp
    └─ 抖音 → SaveTik API
    ↓
音频提取 (downloader)
    ↓
音频优化 (audio_processor)
    ↓
语音识别 (transcriber)
    ↓
AI 润色 (ai_processor)
    ├─ 成功 → AI 处理结果
    └─ 失败 → 原始文本
    ↓
生成 Markdown (ai_processor)
    ↓
飞书同步 (feishu_sync)
    ↓
完成
```

## 🚀 启动方式

### 开发环境
```bash
streamlit run app.py
```

### 生产环境
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📝 日志位置

- 应用日志：`logs/app.log`
- 控制台输出：实时显示

## 🔒 安全说明

### 敏感文件（不要提交到 Git）
- `.env` - 包含 API Keys
- `cookies_*.txt` - 包含登录信息
- `logs/` - 可能包含敏感信息

### 已配置 .gitignore
```
.env
cookies*.txt
logs/
downloads/
outputs/
__pycache__/
*.pyc
```

## 📦 依赖管理

### 主要依赖
- `streamlit` - Web 界面
- `yt-dlp` - 视频下载
- `openai-whisper` - 语音识别
- `openai` - OpenAI API
- `google-generativeai` - Gemini API
- `requests` - HTTP 请求
- `ffmpeg-python` - 音频处理

### 安装
```bash
pip install -r requirements.txt
```

## 🎨 界面结构

### 侧边栏
- AI 设置
- Whisper 模型选择
- 输出路径
- 飞书配置
- Cookies 配置

### 主界面
- 单个处理
- 批量处理
- 历史记录

## 🔄 更新日志

### v1.0 - 2024-12-24
- ✅ 基础功能实现
- ✅ B站/小红书/抖音支持
- ✅ 平台自动识别
- ✅ 分平台 Cookies 管理
- ✅ URL 自动清理
- ✅ AI 失败自动跳过
- ✅ 抖音 SaveTik API 集成

## 📞 支持

如有问题，请查看：
1. `README.md` - 项目概述
2. `QUICK_START.md` - 快速开始
3. `SETUP_GUIDE.md` - 详细安装
4. 各功能说明文档

---

**项目状态**：✅ 生产就绪  
**最后更新**：2024-12-24  
**版本**：v1.0
