# 🍪 Cookies 使用完整指南

## ✅ 功能已添加

系统现在支持使用 Cookies 文件来下载需要登录的视频平台内容。

### 更新内容

1. ✅ 配置文件支持 Cookies 路径
2. ✅ 下载器自动使用 Cookies
3. ✅ Streamlit 界面添加 Cookies 上传
4. ✅ Cookies 管理功能（上传/删除）
5. ✅ 测试脚本验证 Cookies

## 🚀 快速开始（3 步完成）

### 步骤 1：导出 Cookies

**使用 Chrome 浏览器**：

1. 安装扩展 "Get cookies.txt LOCALLY"
   - 打开：https://chrome.google.com/webstore
   - 搜索：Get cookies.txt LOCALLY
   - 点击"添加至 Chrome"

2. 访问目标网站并登录
   - 例如：https://www.bilibili.com
   - 使用你的账号登录

3. 导出 Cookies
   - 点击浏览器工具栏的扩展图标
   - 点击 "Export"
   - 保存为 `cookies.txt`

### 步骤 2：上传到应用

1. 启动应用
   ```bash
   streamlit run app.py
   ```

2. 在侧边栏找到 "Cookies 配置"

3. 点击 "上传 cookies.txt"

4. 选择刚才导出的文件

5. 看到 "✓ Cookies 已配置" 提示

### 步骤 3：测试下载

1. 在主界面输入视频链接
   ```
   https://www.bilibili.com/video/BV1xx411c7mD
   ```

2. 点击 "🚀 开始处理"

3. 观察处理进度

4. 如果成功，说明 Cookies 有效！

## 📋 详细说明

### 配置文件

`.env` 文件中添加了 Cookies 配置：

```env
# Cookies 文件路径
COOKIES_FILE=./cookies.txt
```

### 应用界面

侧边栏新增 "Cookies 配置" 部分：

- **状态显示**：显示是否已配置 Cookies
- **上传功能**：直接上传 cookies.txt 文件
- **删除功能**：一键删除 Cookies
- **使用指南**：展开查看详细说明

### 自动使用

下载器会自动检测并使用 Cookies：

```python
# 如果 cookies.txt 存在，自动使用
if Path('cookies.txt').exists():
    # 下载时自动带上 cookies
    ydl_opts['cookiefile'] = 'cookies.txt'
```

## 🧪 测试 Cookies

### 使用测试脚本

```bash
# 测试默认的 cookies.txt
python test_cookies.py

# 测试指定的文件
python test_cookies.py my_cookies.txt
```

### 测试输出

**成功示例**：
```
🍪 Cookies 测试
======================================================================

✓ 找到 Cookies 文件: cookies.txt

Cookies 信息：
  总行数: 25
  Cookie 数量: 20

检测到平台: B站

----------------------------------------------------------------------
测试视频下载
----------------------------------------------------------------------

测试平台: B站
测试链接: https://www.bilibili.com/video/BV1xx411c7mD

正在获取视频信息...
✓ 获取信息成功

视频信息：
  标题: 测试视频
  作者: UP主名称
  时长: 120 秒

======================================================================
✅ Cookies 测试成功
======================================================================
```

**失败示例**：
```
❌ Cookies 测试失败

可能的原因：
1. Cookies 已过期
2. Cookies 格式不正确
3. 账号被限制
4. 网络连接问题

解决方案：
1. 重新登录并导出新的 cookies
2. 检查 cookies 文件格式
3. 查看详细指南：Cookies导出指南.md
```

## 📝 支持的平台

| 平台 | 状态 | 说明 |
|------|------|------|
| B站 | ✅ 支持 | 需要登录 cookies |
| 小红书 | ✅ 支持 | 需要登录 cookies |
| 抖音 | ✅ 支持 | 需要登录 cookies |
| YouTube | ✅ 支持 | 某些视频需要 cookies |
| Twitter | ✅ 支持 | 需要登录 cookies |
| Instagram | ✅ 支持 | 需要登录 cookies |

## 🔒 安全建议

### ⚠️ 重要提醒

1. **Cookies 包含敏感信息**
   - 相当于你的登录凭证
   - 不要分享给他人
   - 不要上传到公共位置

2. **Cookies 会过期**
   - 通常 1-30 天
   - 过期后需要重新导出
   - 应用会提示失效

3. **账号安全**
   - 建议使用测试账号
   - 使用后可以修改密码
   - 或重新登录使 cookies 失效

### ✅ 最佳实践

1. **使用专用账号**
   ```
   为测试创建新账号
   不要使用主账号
   ```

2. **定期更新**
   ```
   每周检查 cookies 是否过期
   过期后重新导出
   ```

3. **使用后清理**
   ```
   测试完成后删除 cookies
   在应用中点击 "删除 Cookies"
   ```

## 💡 使用技巧

### 技巧 1：多平台 Cookies

一个 cookies.txt 可以包含多个网站的 cookies：

```
# Netscape HTTP Cookie File
.bilibili.com	TRUE	/	FALSE	1735689600	SESSDATA	xxx
.xiaohongshu.com	TRUE	/	FALSE	1735689600	web_session	xxx
.youtube.com	TRUE	/	FALSE	1735689600	CONSENT	xxx
```

### 技巧 2：快速切换

如果需要切换账号：

1. 导出新账号的 cookies
2. 重命名为 `cookies_account2.txt`
3. 在 `.env` 中修改：
   ```env
   COOKIES_FILE=./cookies_account2.txt
   ```

### 技巧 3：自动化更新

创建脚本定期检查 cookies：

```python
# check_cookies.py
import subprocess
from datetime import datetime

result = subprocess.run(['python', 'test_cookies.py'], capture_output=True)

if result.returncode != 0:
    print(f"{datetime.now()}: Cookies 已失效，请更新")
else:
    print(f"{datetime.now()}: Cookies 有效")
```

## 🔧 故障排查

### 问题 1：上传后仍然下载失败

**症状**：
```
ERROR: Unable to download webpage: HTTP Error 412
```

**解决方案**：
1. 检查 cookies 文件格式
2. 确认已登录目标网站
3. 尝试重新导出
4. 使用测试脚本验证

### 问题 2：Cookies 很快过期

**症状**：
```
昨天还能用，今天就失效了
```

**解决方案**：
1. 在浏览器中勾选 "保持登录"
2. 不要在浏览器中退出登录
3. 使用更稳定的账号

### 问题 3：某些视频仍然无法下载

**症状**：
```
有些视频能下载，有些不能
```

**解决方案**：
1. 检查视频是否需要会员
2. 确认视频未被删除或限制
3. 尝试其他视频测试

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| `Cookies导出指南.md` | 详细的导出步骤 |
| `test_cookies.py` | Cookies 测试脚本 |
| `下载问题解决方案.md` | 下载问题汇总 |

## 🎯 Demo 演示流程

### 演示脚本（5分钟）

**1. 介绍功能**（1分钟）
- 系统支持使用 Cookies 下载视频
- 解决平台反爬虫问题
- 简单易用

**2. 导出 Cookies**（2分钟）
- 打开浏览器
- 访问 B站并登录
- 使用扩展导出 cookies.txt
- 展示文件内容

**3. 上传使用**（1分钟）
- 在应用侧边栏上传
- 显示配置成功
- 输入视频链接测试

**4. 验证效果**（1分钟）
- 观察下载进度
- 展示处理结果
- 说明 cookies 的作用

## ✅ 总结

### 已实现功能

- ✅ Cookies 文件支持
- ✅ 自动检测和使用
- ✅ Web 界面上传
- ✅ Cookies 管理
- ✅ 测试验证工具

### 使用流程

```
1. 导出 Cookies
   ↓
2. 上传到应用
   ↓
3. 输入视频链接
   ↓
4. 开始处理
   ↓
5. 获得结果
```

### 优势

- 🎯 简单易用：3 步完成配置
- 🔒 安全可靠：本地存储
- 🚀 即时生效：上传后立即可用
- 🔄 灵活管理：随时上传/删除

---

**更新时间**：2024-12-23  
**状态**：✅ 功能已完成并测试
