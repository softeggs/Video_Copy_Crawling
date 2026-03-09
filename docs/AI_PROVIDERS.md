# AI 提供商配置指南

本系统支持多个 AI 提供商，你可以根据需求选择使用。

## 🤖 支持的 AI 提供商

### 1. OpenAI（推荐）

**优势**：
- 高质量的文本处理能力
- 稳定的 API 服务
- 丰富的模型选择

**配置**：
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
AI_PROVIDER=openai
ENABLE_AI_POLISH=true
```

**获取 API Key**：
1. 访问：https://platform.openai.com/api-keys
2. 登录或注册账号
3. 点击 "Create new secret key"
4. 复制密钥到 `.env` 文件

**推荐模型**：
- `gpt-4-turbo-preview` - 最强性能
- `gpt-4` - 高质量
- `gpt-3.5-turbo` - 经济实惠

### 2. Google Gemini

**优势**：
- Google 最新的 AI 模型
- 免费额度较高
- 多语言支持良好

**配置**：
```env
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro
AI_PROVIDER=gemini
ENABLE_AI_POLISH=true
```

**获取 API Key**：
1. 访问：https://makersuite.google.com/app/apikey
2. 使用 Google 账号登录
3. 点击 "Create API Key"
4. 复制密钥到 `.env` 文件

**可用模型**：
- `gemini-pro` - 标准模型
- `gemini-pro-vision` - 支持图像（未来功能）

## 🔧 不使用 AI 润色模式

如果你只需要语音识别功能，不需要 AI 处理，可以禁用 AI 润色：

```env
ENABLE_AI_POLISH=false
```

**此模式下**：
- ✅ 仍然进行语音识别
- ✅ 生成基础的 Markdown 笔记
- ❌ 不进行文本润色
- ❌ 不提取核心观点和金句
- ❌ 不需要 AI API Key

## 📊 功能对比

| 功能 | AI 润色模式 | 仅识别模式 |
|------|------------|-----------|
| 视频下载 | ✅ | ✅ |
| 语音识别 | ✅ | ✅ |
| 去除口癖 | ✅ | ❌ |
| 纠正错别字 | ✅ | ❌ |
| 提取核心观点 | ✅ | 简单提取 |
| 提取金句 | ✅ | 简单提取 |
| 生成标签 | ✅ | 基础标签 |
| 书面化处理 | ✅ | ❌ |
| 需要 API Key | ✅ | ❌ |
| 处理速度 | 较慢 | 快 |
| 成本 | 有 API 费用 | 无 |

## 💰 成本估算

### OpenAI

**GPT-4 Turbo**：
- 输入：$0.01 / 1K tokens
- 输出：$0.03 / 1K tokens
- 单个视频（5分钟）：约 $0.05-0.10

**GPT-3.5 Turbo**：
- 输入：$0.0005 / 1K tokens
- 输出：$0.0015 / 1K tokens
- 单个视频（5分钟）：约 $0.003-0.005

### Google Gemini

**Gemini Pro**：
- 免费额度：60 请求/分钟
- 单个视频：免费（在额度内）

## 🎯 推荐配置

### 场景 1：追求最高质量

```env
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4-turbo-preview
ENABLE_AI_POLISH=true
```

### 场景 2：经济实惠

```env
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-pro
ENABLE_AI_POLISH=true
```

### 场景 3：快速处理

```env
ENABLE_AI_POLISH=false
```

### 场景 4：批量处理

```env
AI_PROVIDER=openai
OPENAI_MODEL=gpt-3.5-turbo
ENABLE_AI_POLISH=true
```

## 🔄 在界面中切换

启动应用后，可以在侧边栏实时切换：

1. **AI 润色开关**：启用/禁用 AI 处理
2. **AI 提供商**：选择 OpenAI 或 Gemini
3. 无需重启应用，立即生效

## ⚠️ 注意事项

1. **API Key 安全**：不要将 `.env` 文件提交到 Git
2. **额度限制**：注意 API 的请求频率限制
3. **网络要求**：需要能访问对应的 API 服务
4. **成本控制**：批量处理时注意 API 费用

## 🆘 常见问题

**Q: 可以同时配置两个提供商吗？**
A: 可以，在 `.env` 中配置两个 API Key，通过 `AI_PROVIDER` 切换使用

**Q: Gemini 在中国能用吗？**
A: 需要网络代理访问

**Q: 不使用 AI 润色效果如何？**
A: 可以获得准确的语音转文字，但文本质量取决于原始语音质量

**Q: 如何降低成本？**
A: 使用 Gemini（免费额度）或 GPT-3.5-turbo（便宜）
