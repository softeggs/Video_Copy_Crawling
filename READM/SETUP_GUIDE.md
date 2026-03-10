# 环境配置指南

## ✅ 已完成

- ✅ Python 3.12.7 已安装
- ✅ Python 依赖包已安装
- ✅ 工作目录已创建（downloads, outputs, logs）
- ✅ .env 配置文件已创建

## ⚠️ 待完成

### 1. 安装 FFmpeg（必需）

**方式 1：使用 Chocolatey（推荐）**

以**管理员身份**打开 PowerShell，运行：

```powershell
choco install ffmpeg -y
```

安装完成后，重启终端并验证：

```powershell
ffmpeg -version
```

**方式 2：手动安装**

1. 访问：https://www.gyan.dev/ffmpeg/builds/
2. 下载：ffmpeg-release-essentials.zip
3. 解压到：`C:\ffmpeg`
4. 添加环境变量：
   - 按 Win + X，选择"系统"
   - 点击"高级系统设置"
   - 点击"环境变量"
   - 在"系统变量"中找到 `Path`，点击"编辑"
   - 点击"新建"，添加：`C:\ffmpeg\bin`
   - 点击"确定"保存
5. 重启终端验证：`ffmpeg -version`

### 2. 配置 API 密钥

编辑项目根目录的 `.env` 文件：

```env
# AI 提供商选择（二选一）

# 选项 1: OpenAI
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# 选项 2: Google Gemini
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro

# 选择使用哪个 AI 提供商: openai 或 gemini
AI_PROVIDER=openai

# 是否启用 AI 润色: true 或 false
# 设为 false 则只进行语音识别，不进行 AI 处理
ENABLE_AI_POLISH=true

# Whisper 模型（可选，默认 base）
WHISPER_MODEL=base

# 飞书配置（可选，不配置则不同步到飞书）
FEISHU_APP_ID=cli_your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_BITABLE_APP_TOKEN=your_bitable_app_token
FEISHU_BITABLE_TABLE_ID=your_table_id
```

#### 获取 API Key

**OpenAI**：
1. 访问：https://platform.openai.com/api-keys
2. 登录账号
3. 点击"Create new secret key"
4. 复制密钥到 `.env` 文件

**Google Gemini**：
1. 访问：https://makersuite.google.com/app/apikey
2. 使用 Google 账号登录
3. 点击"Create API Key"
4. 复制密钥到 `.env` 文件

详细的 AI 提供商配置说明，请查看 `AI_PROVIDERS.md`

#### 获取飞书配置（可选）

1. 访问飞书开放平台：https://open.feishu.cn/
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 创建多维表格，获取 App Token 和 Table ID

### 3. 启动应用

完成上述配置后，在项目目录运行：

```powershell
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

## 🎯 快速测试

安装 FFmpeg 后，可以先测试基本功能：

```powershell
# 测试 FFmpeg
ffmpeg -version

# 测试 Python 环境
python -c "import whisper; print('Whisper OK')"

# 启动应用
streamlit run app.py
```

## 📝 注意事项

1. **首次运行 Whisper** 会自动下载模型文件（约 150MB），需要等待
2. **网络问题**：如果下载模型失败，可以手动下载后放到 `~/.cache/whisper/`
3. **飞书同步**：如果不需要飞书功能，可以不配置相关密钥
4. **依赖冲突**：如果遇到 h11 版本冲突警告，可以忽略，不影响使用

## 🆘 常见问题

**Q: FFmpeg 安装后仍提示找不到？**
A: 重启终端或重启电脑，确保环境变量生效

**Q: Whisper 模型下载失败？**
A: 检查网络连接，或使用代理

**Q: OpenAI API 调用失败？**
A: 检查 API Key 是否正确，账户是否有余额

**Q: 视频下载失败？**
A: 某些平台可能需要登录或有地区限制
