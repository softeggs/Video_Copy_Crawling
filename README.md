# 短视频内容情报提取系统

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**全自动化的视频内容分析与飞书多维表格同步工具**。集成了多平台视频抓取、Whisper 语音识别、多模型 AI 润色以及飞书自动化同步功能。

---

## 📖 核心文档导航
- [快速开始指南](docs/QUICK_START.md) | [详细配置手册](docs/SETUP_GUIDE.md)
- [iOS 快捷指令详细步骤](docs/IOS_详细配置步骤.md) | [定时任务高级指南](docs/定时任务使用指南.md)
- [完整文件列表及说明](docs/PROJECT_STRUCTURE.md)

---

## 1. 环境部署 (Environment Deployment)

本项目基于 Python 开发，核心依赖包括视频抓取 (yt-dlp)、音频处理 (FFmpeg) 及 AI 推理。

### 基础环境
- **Python**: 推荐使用 3.9 或更高版本。
- **FFmpeg**: 必须安装以支持音频提取与转换。
    - **Windows**: 下载后添加至系统变量，详见 [FFmpeg 安装指南](docs/install_ffmpeg.md)。
    - **Linux/Mac**: `sudo apt install ffmpeg` 或 `brew install ffmpeg`。

### 安装步骤
1. 克隆项目并进入目录：
   ```bash
   git clone <repository_url>
   cd Video_Copy_Crawling
   ```
2. 安装 Python 依赖：
   ```bash
   pip install -r docs/requirements.txt
   ```

---

## 2. 配置制定 (Configuration Specification)

项目所有敏感配置均通过 `.env` 文件管理。请从模板复制并填写：
```bash
cp .env.example .env
```

### 核心参数核心参数
| 类别         | 变量名                     | 说明                                         |
| :----------- | :------------------------- | :------------------------------------------- |
| **AI 引擎**  | `AI_PROVIDER`              | `openai` 或 `gemini`                         |
|              | `OPENAI_API_KEY`           | OpenAI API 密钥 (或中转 Key)                 |
|              | `GEMINI_API_KEY`           | Google AI Studio 密钥                        |
| **功能开关** | `ENABLE_AI_POLISH`         | `true` (启用 AI 润色) / `false` (仅转录文本) |
| **飞书集成** | `FEISHU_APP_ID`            | 飞书自建应用 App ID                          |
|              | `FEISHU_APP_SECRET`        | 飞书自建应用 App Secret                      |
|              | `FEISHU_BITABLE_APP_TOKEN` | 多维表格 App Token                           |
|              | `FEISHU_BITABLE_TABLE_ID`  | 具体数据表的 ID                              |

> [!TIP]
> 详细的飞书权限申请流程请参考 [飞书快速开始](docs/FEISHU_QUICKSTART.md)。

---

## 3. 项目运行 (Project Operation)

您可以根据使用场景选择不同的运行方式：

### A. Web 交互模式 (推荐)
启动基于 Streamlit 的可视化界面，支持单任务处理、日志查看及定时任务控制。

- **Windows 用户**: 直接双击运行根目录下的 `快速启动.bat`。
- **命令行**: `streamlit run app.py`

### B. 独立调度模式
如果您希望系统在后台静默运行，自动处理飞书表格中的新链接：
```bash
python scheduler_app.py
```

### C. 命令行手动核查
一次性检查并处理所有飞书表中的空白链接：
```bash
python check_blank_links.py
```

---

## 4. 自动化后台处理 (Automated Background Processing)

系统支持高效的自动化工作流，主要由 `BackgroundScheduler` (单例模式) 驱动。

### 工作原理
1. **监听**: 定时扫描飞书多维表格中「处理状态」为「待处理」或「处理中」且内容为空的记录。
2. **下载与识别**: 自动调用 `yt-dlp` 下载视频并利用 Whisper 进行语音转录。
3. **AI 分析**: 提取核心观点、金句及标签（若开启 AI 润色）。
4. **回传**: 将处理结果即时同步回飞书表格，并更新「处理状态」。

### 管理方式
- **Web 端**: 在 Streamlit 界面的「⏰ 定时任务」标签页中实时启动/停止任务。
- **Windows 自动化**: 
    - 已集成 **Windows 计划任务** (`VideoCopyCrawlingMonitor`)。
    - 每 **4 小时** 自动执行一次 `monitor_app.ps1`，检测进程若不在运行则自动拉起。
    - 日志记录于 `logs/monitor.log`。
- **Linux 系统服务**: 可配置为 `systemd` 服务以实现开机自启，见 `feishu-scheduler.service`。

---

## 5. iOS 快捷指令配置 (iOS Shortcut Configuration)

为了实现「在手机上一键收藏并自动分析」，您可以配置 iOS 快捷指令：

### 核心流程
1. **分享/复制链接**: 在抖音、B站或小红书复制视频链接。
2. **触发指令**: 运行快捷指令，它将直接通过飞书 API 将链接写入您的多维表格。
3. **自动处理**: 后台程序（见第 4 节）自动检测到新链接并开始分析。

### 配置要点
- 您需要在快捷指令中填入您的 `App ID`, `App Secret`, `Table ID`。
- **详细图文教程**: 请参考 [iOS 快捷指令最终指南](docs/IOS_SHORTCUT_FINAL_GUIDE.md)。

---

## 🛠️ 项目结构简述
```text
├── app.py                # 主 Web 界面
├── scheduler_app.py      # 独立调度程序
├── core/                 # 核心逻辑 (下载、转录、AI、飞书)
├── docs/                 # 项目详细文档、配置指南及依赖列表
├── utils/                # 通用工具
└── .env                  # 环境配置文件
```

---

## 许可证
本项目遵循 MIT 开源协议。
