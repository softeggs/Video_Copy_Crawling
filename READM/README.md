# 短视频内容情报提取系统

全自动化的视频内容分析与飞书同步工具

## 功能特性

- 🎬 **多平台支持**：抖音、B站、小红书视频自动下载
- 🎙️ **语音识别**：基于 OpenAI Whisper 的高精度转写
- 🤖 **多 AI 引擎**：支持 OpenAI GPT 和 Google Gemini
- 📝 **智能纠错**：AI 纠错模式，保持原文风格只做文字修正
- 🔄 **灵活模式**：可选 AI 纠错或纯语音识别
- ⏱️ **超时重试**：AI 处理超时自动重试（60s × 3 次）
- ✨ **智能分析**：自动提取核心观点、金句、标签
- 📊 **飞书同步**：自动同步到飞书多维表格
- ⚡ **高效处理**：异步并发，支持批量处理
- 🍪 **分平台 Cookies**：独立管理各平台登录状态

## 技术栈

- Python 3.9+
- yt-dlp (视频抓取)
- FFmpeg (音频处理)
- OpenAI Whisper (语音识别)
- LangChain + OpenAI (AI 处理)
- Feishu SDK (飞书集成)
- Streamlit (Web 界面)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 AI（二选一）

复制 `.env.example` 为 `.env`，配置 AI 提供商：

**选项 A：使用 OpenAI**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_BASE_URL=  # 可选：中转 API
```

**选项 B：使用 Google Gemini**
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash
```

**AI 处理模式**
```env
ENABLE_AI_POLISH=true  # true=启用AI处理，false=仅语音识别
```

**AI 纠错模式说明**：
- ✅ 保持原文结构和语序不变
- ✅ 修正同音字错误（如：视屏→视频）
- ✅ 校准专有名词和术语
- ✅ 优化断句和标点符号
- ✅ 去除无意义语气词（呃、啊、这个、那个）
- ✅ 忠于原意，不改变核心观点

📖 详细配置：[AI_PROVIDERS.md](AI_PROVIDERS.md)  
📖 纠错模式指南：[../AI纠错模式快速指南.md](../AI纠错模式快速指南.md)

### 3. 配置飞书同步（可选）

```env
FEISHU_APP_ID=cli_xxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxx
FEISHU_BITABLE_APP_TOKEN=xxxxxxxxxx
FEISHU_BITABLE_TABLE_ID=tblxxxxxxxxx
```

📖 飞书配置指南：
- 快速开始：[FEISHU_QUICKSTART.md](FEISHU_QUICKSTART.md)
- 详细文档：[FEISHU_SETUP.md](FEISHU_SETUP.md)

### 4. 启动应用

```bash
streamlit run app.py
```

访问 http://localhost:8501

### 5. 测试配置

```bash
# 测试 AI 配置
python test_gemini.py  # 或 test_openai.py

# 测试飞书配置
python test_feishu.py
```

## 项目结构

```
├── app.py                      # Streamlit Web 界面
├── core/                       # 核心处理模块
│   ├── downloader.py          # 视频下载（yt-dlp）
│   ├── audio_processor.py     # 音频优化（FFmpeg）
│   ├── transcriber.py         # 语音识别（Whisper）
│   ├── ai_processor.py        # AI 分析润色
│   ├── feishu_sync.py         # 飞书同步
│   └── pipeline.py            # 处理流水线
├── utils/                      # 工具模块
│   ├── config.py              # 配置管理
│   ├── logger.py              # 日志工具
│   ├── platform_detector.py   # 平台识别
│   └── url_cleaner.py         # URL 清理
├── READM/                      # 文档目录
│   ├── README.md              # 主文档
│   ├── AI_PROVIDERS.md        # AI 配置指南
│   ├── FEISHU_QUICKSTART.md   # 飞书快速开始
│   ├── FEISHU_SETUP.md        # 飞书详细配置
│   └── Cookies使用完整指南.md  # Cookies 配置
├── requirements.txt            # Python 依赖
├── .env.example               # 环境变量模板
└── test_feishu.py             # 飞书测试脚本
```


## 飞书同步功能

### 功能说明

处理完成的视频内容会自动同步到飞书多维表格，包括：

- ✅ 视频元数据（标题、作者、链接、日期）
- ✅ AI 分析结果（摘要、核心观点、详细内容）
- ✅ 提取的金句和标签
- ✅ 处理状态和时间戳
- ✅ Markdown 笔记路径

### 快速配置

1. **创建飞书应用**（2 分钟）
   - 访问 https://open.feishu.cn/
   - 创建企业自建应用
   - 复制 App ID 和 App Secret

2. **配置权限**（1 分钟）
   - 开通多维表格权限（bitable）
   - 发布应用版本

3. **创建多维表格**（1 分钟）
   - 新建多维表格
   - 添加必需字段（见文档）
   - 复制 APP_TOKEN 和 TABLE_ID

4. **配置环境变量**（30 秒）
   ```env
   FEISHU_APP_ID=cli_xxxxxxxxxx
   FEISHU_APP_SECRET=xxxxxxxxxxxxx
   FEISHU_BITABLE_APP_TOKEN=xxxxxxxxxx
   FEISHU_BITABLE_TABLE_ID=tblxxxxxxxxx
   ```

5. **测试配置**（30 秒）
   ```bash
   python test_feishu.py
   ```

### 详细文档

- 📖 [5 分钟快速开始](FEISHU_QUICKSTART.md)
- 📖 [完整配置指南](FEISHU_SETUP.md)

### 使用方式

**Web 界面**：在侧边栏勾选「启用飞书同步」

**代码调用**：
```python
from core.pipeline import ProcessingPipeline
import asyncio

pipeline = ProcessingPipeline()
result = asyncio.run(pipeline.process("https://..."))

if result['feishu_synced']:
    print("✅ 已同步到飞书")
```

### 数据结构

同步到飞书的数据包括：

| 字段 | 类型 | 说明 |
|------|------|------|
| 标题 | 文本 | 视频标题 |
| 原始链接 | URL | 视频链接 |
| 作者 | 文本 | 作者名称 |
| 发布日期 | 日期 | 发布时间 |
| 一句话总结 | 文本 | AI 生成摘要 |
| 核心观点 | 多行文本 | 提取的要点 |
| 详细内容 | 多行文本 | 完整文案 |
| 金句 | 多行文本 | 精彩语句 |
| 标签 | 多选 | 内容标签 |
| 笔记路径 | 文本 | MD 文件路径 |
| 处理状态 | 单选 | 已完成/处理中/失败 |
| 处理时间 | 日期 | 完成时间 |

## 常见问题

### AI 相关

**Q: 如何选择 AI 提供商？**
A: OpenAI 精度更高但需付费，Gemini 免费但有配额限制。详见 [AI_PROVIDERS.md](AI_PROVIDERS.md)

**Q: 可以不使用 AI 吗？**
A: 可以，设置 `ENABLE_AI_POLISH=false` 即可只进行语音识别。

**Q: AI 处理超时怎么办？**
A: 系统会自动重试 3 次（每次 60 秒超时），全部失败后自动跳过 AI 处理，使用原始转写文本。详见 [AI_TIMEOUT_RETRY.md](AI_TIMEOUT_RETRY.md)

**Q: AI 处理失败怎么办？**
A: 系统会自动重试，最终失败后跳过 AI 处理，使用原始转写文本。不影响整体流程。

### 飞书相关

**Q: 飞书同步失败？**
A: 检查以下几点：
1. 应用是否已添加为表格协作者
2. 权限是否正确配置
3. APP_TOKEN 和 TABLE_ID 是否正确
4. 字段名称是否匹配

详细排查：[FEISHU_SETUP.md](FEISHU_SETUP.md)

**Q: 可以自定义字段吗？**
A: 可以，修改 `core/feishu_sync.py` 中的字段映射。

### 平台相关

**Q: 支持哪些平台？**
A: 目前支持 B站、小红书、抖音。

**Q: 需要配置 Cookies 吗？**
A: 建议配置，可以下载会员专享和登录可见的视频。详见 [Cookies使用完整指南.md](Cookies使用完整指南.md)

**Q: 抖音下载失败？**
A: 抖音反爬虫严格，建议使用浏览器扩展下载。

## 更新日志

### v2.1.0 (2024-01)
- ✨ 新增 AI 处理超时重试机制（60s × 3 次）
- ✨ 超时后自动跳过 AI 润色，使用原始文本
- 🔧 优化错误处理和用户提示
- 📚 新增超时重试机制文档

### v2.0.0 (2024-01)
- ✨ 新增飞书多维表格同步
- ✨ 支持 Google Gemini AI
- ✨ 新增分平台 Cookies 管理
- ✨ 新增 URL 自动清理
- ✨ 新增 AI 失败自动跳过
- 🐛 修复多个已知问题

### v1.0.0 (2023-12)
- 🎉 首次发布
- ✨ 支持 B站、小红书、抖音
- ✨ Whisper 语音识别
- ✨ OpenAI AI 润色

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎通过 Issue 反馈。
