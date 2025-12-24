# 平台识别和分平台 Cookies 功能说明

## 功能概述

系统现在支持：
1. **自动平台识别** - 根据 URL 自动识别视频平台
2. **分平台 Cookies 管理** - 每个平台独立的 cookies 文件
3. **平台支持检测** - 不支持的平台会提示用户
4. **自动 Cookies 调用** - 处理时自动使用对应平台的 cookies

## 支持的平台

### ✅ 已支持
- **B站** (bilibili.com, b23.tv, acg.tv)
- **小红书** (xiaohongshu.com, xhslink.com, xhs.cn)
- **抖音** (douyin.com, iesdouyin.com, v.douyin.com)

### ❌ 暂不支持
- 其他平台会显示"该平台暂不支持"提示

## Cookies 文件结构

每个平台使用独立的 cookies 文件：

```
项目根目录/
├── cookies_bilibili.txt      # B站 cookies
├── cookies_xiaohongshu.txt   # 小红书 cookies
├── cookies_douyin.txt         # 抖音 cookies
└── cookies.txt                # 通用 cookies（向后兼容）
```

## 使用方法

### 1. 配置 Cookies

在应用侧边栏：

1. **选择平台**
   - 从下拉菜单选择：B站 / 小红书 / 抖音

2. **查看状态**
   - 绿色 ✓ = 已配置
   - 灰色 ℹ️ = 未配置
   - 展开"所有平台状态"查看全部

3. **输入 Cookies**
   - 方式 1：文本输入（推荐）
   - 方式 2：文件上传

4. **保存**
   - 点击"💾 保存 XX Cookies"
   - 自动保存到对应平台文件

### 2. 处理视频

1. **输入链接**
   - 粘贴视频 URL

2. **自动识别**
   - 系统自动检测平台
   - 显示"🎯 检测到平台: XX"

3. **Cookies 检查**
   - 如果未配置对应平台 cookies
   - 显示警告："⚠️ 未配置 XX Cookies"

4. **开始处理**
   - 点击"🚀 开始处理"
   - 自动使用对应平台的 cookies

### 3. 不支持的平台

如果输入不支持的平台链接：
- 显示："⚠️ 该平台暂不支持"
- 提示："当前支持的平台：B站、小红书、抖音"
- 无法点击"开始处理"按钮

## 技术实现

### 平台检测器 (PlatformDetector)

```python
from utils.platform_detector import PlatformDetector, Platform

# 检测平台
platform = PlatformDetector.detect_platform(url)

# 获取平台名称
name = PlatformDetector.get_platform_name(platform)

# 获取 cookies 文件
cookies_file = PlatformDetector.get_cookies_file(platform)

# 检查是否支持
is_supported = PlatformDetector.is_supported(platform)
```

### 下载器自动调用

下载器会自动：
1. 检测 URL 平台
2. 查找对应平台的 cookies 文件
3. 如果不存在，回退到通用 cookies
4. 设置对应平台的 Referer

```python
# 自动流程
platform = detect_platform(url)
cookies = get_platform_cookies(platform)  # cookies_bilibili.txt
referer = get_platform_referer(platform)  # https://www.bilibili.com/
```

## 优势

### 1. 更好的隔离性
- 每个平台独立 cookies
- 避免 cookies 冲突
- 更新一个平台不影响其他

### 2. 更清晰的管理
- 一目了然哪些平台已配置
- 针对性更新过期的 cookies
- 便于问题排查

### 3. 更好的用户体验
- 自动识别平台
- 自动选择 cookies
- 明确的错误提示

### 4. 向后兼容
- 保留通用 cookies.txt
- 如果没有平台专用 cookies，自动回退
- 不影响现有配置

## 配置示例

### B站 Cookies

文件：`cookies_bilibili.txt`

```
# Netscape HTTP Cookie File
.bilibili.com	TRUE	/	FALSE	1735689600	SESSDATA	xxx
.bilibili.com	TRUE	/	FALSE	1735689600	bili_jct	xxx
.bilibili.com	TRUE	/	FALSE	1735689600	DedeUserID	xxx
```

### 小红书 Cookies

文件：`cookies_xiaohongshu.txt`

```
# Netscape HTTP Cookie File
.xiaohongshu.com	TRUE	/	FALSE	1798022982	a1	xxx
.xiaohongshu.com	TRUE	/	TRUE	1798022997	web_session	xxx
```

### 抖音 Cookies

文件：`cookies_douyin.txt`

```
# Netscape HTTP Cookie File
.douyin.com	TRUE	/	FALSE	1735689600	sessionid	xxx
```

## 常见问题

### Q1: 如何知道需要配置哪个平台的 cookies？
A: 输入视频链接后，系统会自动检测并提示。如果显示"未配置 XX Cookies"，就需要配置该平台。

### Q2: 可以同时配置多个平台吗？
A: 可以。每个平台独立配置，互不影响。

### Q3: 如果没有配置对应平台 cookies 会怎样？
A: 系统会尝试使用通用 cookies.txt，如果也没有，下载可能失败。

### Q4: 如何添加新平台支持？
A: 需要在 `utils/platform_detector.py` 中添加平台域名映射。

### Q5: 旧的 cookies.txt 还能用吗？
A: 可以。如果没有平台专用 cookies，系统会自动使用 cookies.txt。

## 测试步骤

### 1. 配置 B站 Cookies
```
1. 侧边栏选择"B站"
2. 粘贴 B站 cookies
3. 点击"保存 B站 Cookies"
4. 确认显示"✓ B站 Cookies 已配置"
```

### 2. 测试 B站视频
```
1. 输入 B站视频链接
2. 确认显示"🎯 检测到平台: B站"
3. 点击"开始处理"
4. 验证下载成功
```

### 3. 测试不支持的平台
```
1. 输入 YouTube 链接
2. 确认显示"⚠️ 该平台暂不支持"
3. 确认无法点击"开始处理"
```

## 文件清单

### 新增文件
- `utils/platform_detector.py` - 平台检测器

### 修改文件
- `core/downloader.py` - 集成平台检测
- `app.py` - 分平台 Cookies UI

### Cookies 文件
- `cookies_bilibili.txt` - B站
- `cookies_xiaohongshu.txt` - 小红书
- `cookies_douyin.txt` - 抖音
- `cookies.txt` - 通用（向后兼容）

## 下一步

1. 配置各平台 cookies
2. 测试各平台下载
3. 验证平台识别准确性
4. 根据需要添加更多平台支持
