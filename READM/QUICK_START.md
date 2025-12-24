# 🚀 快速开始

## 当前状态

✅ Python 环境已就绪  
✅ 所有依赖包已安装  
✅ 项目目录已创建  
⚠️ FFmpeg 需要安装  
⚠️ API 密钥需要配置  

## 下一步（2 步完成）

### 步骤 1：安装 FFmpeg

**选项 A：自动安装（推荐）**

以**管理员身份**打开 PowerShell，运行：

```powershell
.\install_ffmpeg.ps1
```

**选项 B：使用 Chocolatey**

```powershell
choco install ffmpeg -y
```

**选项 C：手动安装**

查看详细说明：`install_ffmpeg.md`

### 步骤 2：配置 API 密钥

编辑 `.env` 文件，选择使用 OpenAI 或 Gemini：

**使用 OpenAI：**
```env
OPENAI_API_KEY=sk-your-actual-key-here
AI_PROVIDER=openai
ENABLE_AI_POLISH=true
```

**使用 Gemini：**
```env
GEMINI_API_KEY=your-gemini-key-here
AI_PROVIDER=gemini
ENABLE_AI_POLISH=true
```

**不使用 AI 润色（仅语音识别）：**
```env
ENABLE_AI_POLISH=false
```

获取 API Key：
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://makersuite.google.com/app/apikey

详细说明：查看 `AI_PROVIDERS.md`

## 启动应用

完成上述步骤后：

```powershell
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

## 测试环境

随时运行测试脚本检查配置：

```powershell
python test_env.py
```

## 使用示例

1. 在 Web 界面输入视频链接（抖音/B站/小红书）
2. 点击"开始处理"
3. 等待处理完成（下载→识别→AI处理→生成笔记）
4. 下载 Markdown 笔记或查看飞书同步结果

## 需要帮助？

- 详细配置：`SETUP_GUIDE.md`
- FFmpeg 安装：`install_ffmpeg.md`
- 项目说明：`README.md`
