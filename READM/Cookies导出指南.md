# 🍪 Cookies 导出指南

## 📋 为什么需要 Cookies？

视频平台（B站、小红书、抖音、YouTube等）为了防止滥用，需要验证用户身份。Cookies 包含了你的登录信息，让程序可以像浏览器一样访问这些网站。

## 🎯 快速开始

### 方法 1：使用浏览器扩展（推荐）

#### Chrome 浏览器

1. **安装扩展**
   - 打开 Chrome 网上应用店
   - 搜索 "Get cookies.txt LOCALLY"
   - 点击"添加至 Chrome"
   - 链接：https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

2. **导出 Cookies**
   - 访问目标网站（如 https://www.bilibili.com）
   - 登录你的账号
   - 点击浏览器工具栏的扩展图标
   - 点击 "Export" 或 "导出"
   - 保存为 `cookies.txt`

3. **上传到应用**
   - 在应用侧边栏找到 "Cookies 配置"
   - 点击 "上传 cookies.txt"
   - 选择刚才导出的文件

#### Firefox 浏览器

1. **安装扩展**
   - 打开 Firefox 附加组件
   - 搜索 "cookies.txt"
   - 安装扩展
   - 链接：https://addons.mozilla.org/firefox/addon/cookies-txt/

2. **导出 Cookies**
   - 访问目标网站并登录
   - 点击扩展图标
   - 选择 "Export cookies.txt"
   - 保存文件

3. **上传到应用**
   - 同 Chrome 步骤

#### Edge 浏览器

Edge 可以使用 Chrome 扩展：
1. 启用 "允许来自其他应用商店的扩展"
2. 按照 Chrome 的步骤操作

### 方法 2：手动导出（高级）

如果不想安装扩展，可以手动导出：

#### 步骤 1：获取 Cookies

1. 打开浏览器开发者工具（按 F12）
2. 访问目标网站并登录
3. 切换到 "Application" 或 "应用程序" 标签
4. 左侧选择 "Cookies"
5. 选择网站域名
6. 复制所有 cookies

#### 步骤 2：转换格式

Cookies 需要是 Netscape 格式。使用在线工具或脚本转换：

```python
# convert_cookies.py
import json

# 从浏览器复制的 cookies（JSON 格式）
cookies_json = [
    {
        "name": "cookie_name",
        "value": "cookie_value",
        "domain": ".bilibili.com",
        "path": "/",
        "expires": 1234567890,
        "httpOnly": False,
        "secure": True
    }
]

# 转换为 Netscape 格式
with open('cookies.txt', 'w') as f:
    f.write("# Netscape HTTP Cookie File\n")
    for cookie in cookies_json:
        line = f"{cookie['domain']}\tTRUE\t{cookie['path']}\t"
        line += f"{'TRUE' if cookie.get('secure') else 'FALSE'}\t"
        line += f"{cookie.get('expires', 0)}\t"
        line += f"{cookie['name']}\t{cookie['value']}\n"
        f.write(line)

print("✓ cookies.txt 已生成")
```

## 📝 Cookies 文件格式

正确的 cookies.txt 格式示例：

```
# Netscape HTTP Cookie File
.bilibili.com	TRUE	/	FALSE	1735689600	SESSDATA	your_session_data_here
.bilibili.com	TRUE	/	FALSE	1735689600	bili_jct	your_csrf_token_here
.bilibili.com	TRUE	/	FALSE	1735689600	DedeUserID	12345678
```

格式说明：
- 第一行必须是：`# Netscape HTTP Cookie File`
- 每行一个 cookie，字段用 Tab 分隔
- 字段顺序：域名、包含子域、路径、安全标志、过期时间、名称、值

## 🎯 各平台 Cookies 导出

### B站（bilibili.com）

**需要的关键 Cookies**：
- `SESSDATA` - 会话数据
- `bili_jct` - CSRF token
- `DedeUserID` - 用户ID

**导出步骤**：
1. 登录 https://www.bilibili.com
2. 使用扩展导出 cookies.txt
3. 上传到应用

### 小红书（xiaohongshu.com）

**需要的关键 Cookies**：
- `web_session` - 会话标识
- `xsecappid` - 应用ID

**导出步骤**：
1. 登录 https://www.xiaohongshu.com
2. 导出 cookies
3. 上传到应用

### 抖音（douyin.com）

**需要的关键 Cookies**：
- `sessionid` - 会话ID
- `ttwid` - 设备ID

**导出步骤**：
1. 登录 https://www.douyin.com
2. 导出 cookies
3. 上传到应用

### YouTube

**需要的关键 Cookies**：
- `CONSENT` - 同意标识
- `VISITOR_INFO1_LIVE` - 访客信息

**导出步骤**：
1. 登录 https://www.youtube.com
2. 导出 cookies
3. 上传到应用

## 🔒 安全注意事项

### ⚠️ 重要提醒

1. **Cookies 包含敏感信息**
   - 不要分享给他人
   - 不要上传到公共位置
   - 定期更新

2. **Cookies 会过期**
   - 通常 1-30 天过期
   - 过期后需要重新导出
   - 应用会提示 cookies 失效

3. **账号安全**
   - 使用后建议修改密码
   - 或者重新登录使 cookies 失效
   - 不要在不信任的设备上导出

### ✅ 安全建议

1. **使用专用账号**
   - 为测试创建新账号
   - 不要使用主账号

2. **定期清理**
   - 测试完成后删除 cookies 文件
   - 在应用中点击 "删除 Cookies"

3. **本地存储**
   - Cookies 只存储在本地
   - 不会上传到服务器
   - 应用重启后仍然有效

## 🧪 测试 Cookies

### 验证 Cookies 是否有效

创建测试脚本 `test_cookies.py`：

```python
import yt_dlp

TEST_URL = "https://www.bilibili.com/video/BV1xx411c7mD"

ydl_opts = {
    'cookiefile': 'cookies.txt',
    'quiet': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(TEST_URL, download=False)
        print("✓ Cookies 有效")
        print(f"视频标题: {info.get('title')}")
except Exception as e:
    print("✗ Cookies 无效或已过期")
    print(f"错误: {str(e)}")
```

运行测试：
```bash
python test_cookies.py
```

## 📚 常见问题

### Q: Cookies 多久过期？

A: 通常 1-30 天，取决于平台设置。过期后需要重新导出。

### Q: 可以同时使用多个平台的 Cookies 吗？

A: 可以。一个 cookies.txt 文件可以包含多个网站的 cookies。

### Q: Cookies 导出后还能正常使用浏览器吗？

A: 可以。导出不会影响浏览器中的 cookies。

### Q: 忘记删除 Cookies 怎么办？

A: 在浏览器中退出登录，或修改密码，会使 cookies 失效。

### Q: 应用提示 "Cookies 无效" 怎么办？

A: 
1. 检查文件格式是否正确
2. 重新登录并导出新的 cookies
3. 确认 cookies 未过期

## 🎬 在应用中使用

### 步骤 1：上传 Cookies

1. 打开应用侧边栏
2. 找到 "Cookies 配置" 部分
3. 点击 "上传 cookies.txt"
4. 选择导出的文件
5. 看到 "✓ Cookies 已配置" 提示

### 步骤 2：测试下载

1. 在主界面输入视频链接
2. 点击 "开始处理"
3. 观察是否能成功下载

### 步骤 3：管理 Cookies

- **查看状态**：侧边栏显示是否已配置
- **删除 Cookies**：点击 "删除 Cookies" 按钮
- **更新 Cookies**：重新上传新文件会覆盖旧文件

## 💡 最佳实践

### 推荐流程

1. **首次使用**
   - 创建测试账号
   - 导出 cookies
   - 上传到应用
   - 测试一个视频

2. **日常使用**
   - 定期检查 cookies 是否过期
   - 过期后重新导出
   - 使用完毕删除 cookies

3. **安全维护**
   - 不要分享 cookies 文件
   - 定期更换密码
   - 使用专用测试账号

## 🔧 故障排查

### 问题：上传后仍然下载失败

**解决方案**：
1. 检查 cookies 文件格式
2. 确认已登录目标网站
3. 尝试重新导出
4. 检查账号是否被限制

### 问题：Cookies 很快过期

**解决方案**：
1. 在浏览器中勾选 "保持登录"
2. 使用更稳定的账号
3. 考虑使用 API 方式（需要申请）

### 问题：某些视频仍然无法下载

**解决方案**：
1. 检查视频是否需要会员
2. 确认视频未被删除
3. 尝试其他视频测试

---

**更新时间**：2024-12-23  
**状态**：已在应用中集成 Cookies 上传功能
