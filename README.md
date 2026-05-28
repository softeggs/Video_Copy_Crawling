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
- 📱 iOS 快捷指令支持（一键添加视频链接）
- ⏰ 定时任务自动处理

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
# 或
DEEPSEEK_API_KEY=your_deepseek_key

AI_PROVIDER=openai  # 或 gemini / deepseek
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

## P7 本地部署演练

统一后端的第一阶段部署资产已经补齐，适用于本地 Docker 化演练，不涉及真实云主机发布。

- 部署说明：`docs/P7_LOCAL_DEPLOYMENT.md`
- 编排入口：`docker-compose.yml`
- 运行配置模板：`.env.deploy.example`

本阶段默认包含：

- `backend-api`
- `db-scheduler`
- `web_main.py` 正式用户入口
- `app.py` 内部调试台
- `nginx` 本地反向代理

## iOS 快捷指令 ⭐ 新功能

通过 iOS 快捷指令，可以快速将视频链接添加到飞书表格，等待定时任务自动处理。

### ✅ 已测试通过

- API 连接测试：✅ 成功
- 添加记录测试：✅ 成功
- 字段验证：✅ 完成

### 🚀 快速开始（5-10 分钟）

**新手推荐**: [超详细配置步骤](READM/IOS_详细配置步骤.md)（包含每一步的搜索关键词、参数配置、变量引用）

**快速配置**: [最终配置指南](READM/IOS_SHORTCUT_FINAL_GUIDE.md)（包含实际配置和测试结果）

**文档导航**: [START_HERE](READM/START_HERE.md) | [文档选择指南](READM/文档选择指南.md)

### 🧪 测试工具

在配置快捷指令之前，先测试 API：

```bash
# Windows 用户
test-ios-shortcut.bat

# 或直接运行
python quick_test_ios_api.py

# 检查表格字段
python check_feishu_fields.py
```

### 📱 使用方式

配置完成后，可以通过以下方式使用：

- **Siri**: "嘿 Siri，添加视频到飞书"
- **主屏幕**: 添加图标，一键启动
- **分享菜单**: 在浏览器中直接分享链接

### 📚 完整文档列表

- [IOS_详细配置步骤.md](READM/IOS_详细配置步骤.md) - 超详细逐步指南 ⭐ 推荐
- [IOS_SHORTCUT_FINAL_GUIDE.md](READM/IOS_SHORTCUT_FINAL_GUIDE.md) - 最终配置指南
- [IOS_SHORTCUT_README.md](READM/IOS_SHORTCUT_README.md) - 功能总览
- [IOS_SHORTCUT_QUICK_REFERENCE.md](READM/IOS_SHORTCUT_QUICK_REFERENCE.md) - 快速参考
- [文档选择指南.md](READM/文档选择指南.md) - 帮助选择合适的文档

## 项目结构

```
├── app.py                 # Streamlit 主界面
├── scheduler_app.py       # 定时任务界面
├── core/
│   ├── downloader.py     # 视频下载模块
│   ├── audio_processor.py # 音频处理模块
│   ├── transcriber.py    # 语音识别模块
│   ├── ai_processor.py   # AI 润色模块
│   ├── feishu_sync.py    # 飞书同步模块
│   └── scheduler.py      # 定时任务模块
├── utils/
│   ├── config.py         # 配置管理
│   └── logger.py         # 日志工具
├── test_add_url_to_feishu.py  # iOS 快捷指令测试工具
├── requirements.txt
└── .env.example
```
