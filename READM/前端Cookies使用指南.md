# 🍪 前端 Cookies 使用指南

## ✨ 新功能特性

### 前端输入 Cookies

现在支持直接在 Web 界面输入 Cookies，无需手动管理文件！

**优势**：
- ✅ 直接粘贴，即时生效
- ✅ 自动保存，下次自动加载
- ✅ 方便更新，cookies 过期后直接替换
- ✅ 可视化管理，清晰显示状态

## 🚀 快速开始

### 方式 1：文本输入（推荐）

**步骤 1：获取 Cookies**

使用浏览器扩展：

1. **Chrome 浏览器**
   - 安装扩展：[Get cookies.txt LOCALLY](https://chrome.google.com/webstore)
   - 访问网站（如 bilibili.com）并登录
   - 点击扩展图标
   - 点击 "Export" 导出
   - 复制全部内容

2. **Firefox 浏览器**
   - 安装扩展：cookies.txt
   - 访问网站并登录
   - 点击扩展图标
   - 导出并复制内容

**步骤 2：粘贴到应用**

1. 打开应用侧边栏
2. 找到 "Cookies 配置"
3. 选择 "文本输入"
4. 粘贴 cookies 内容到文本框
5. 点击 "💾 保存 Cookies"
6. 看到 "✓ Cookies 已保存" 提示

**步骤 3：开始使用**

1. 输入视频链接
2. 点击 "开始处理"
3. 系统自动使用 cookies 下载

### 方式 2：文件上传

**步骤 1：导出文件**

1. 使用浏览器扩展导出 cookies.txt 文件
2. 保存到本地

**步骤 2：上传到应用**

1. 在侧边栏选择 "文件上传"
2. 点击 "上传 cookies.txt"
3. 选择文件
4. 自动保存并生效

## 💡 使用场景

### 场景 1：首次配置

```
1. 登录 B站
2. 导出 cookies
3. 粘贴到应用
4. 保存
5. 开始使用
```

### 场景 2：Cookies 过期

```
1. 应用提示下载失败
2. 重新登录网站
3. 导出新的 cookies
4. 粘贴到应用（覆盖旧的）
5. 保存
6. 继续使用
```

### 场景 3：切换账号

```
1. 使用账号 A 的 cookies
2. 需要切换到账号 B
3. 登录账号 B
4. 导出新 cookies
5. 粘贴并保存
6. 立即生效
```

### 场景 4：多平台使用

```
1. 导出 B站 cookies
2. 导出小红书 cookies
3. 合并到一个文本框
4. 保存
5. 同时支持多个平台
```

## 📋 Cookies 格式

### 标准格式（Netscape）

```
# Netscape HTTP Cookie File
.bilibili.com	TRUE	/	FALSE	1735689600	SESSDATA	your_session_data_here
.bilibili.com	TRUE	/	FALSE	1735689600	bili_jct	your_csrf_token_here
.bilibili.com	TRUE	/	FALSE	1735689600	DedeUserID	12345678
```

### 格式说明

- 第一行：`# Netscape HTTP Cookie File`
- 每行一个 cookie
- 字段用 Tab 分隔
- 字段：域名、子域、路径、安全、过期时间、名称、值

### 多平台合并

```
# Netscape HTTP Cookie File

# B站 Cookies
.bilibili.com	TRUE	/	FALSE	1735689600	SESSDATA	xxx
.bilibili.com	TRUE	/	FALSE	1735689600	bili_jct	xxx

# 小红书 Cookies
.xiaohongshu.com	TRUE	/	FALSE	1735689600	web_session	xxx

# YouTube Cookies
.youtube.com	TRUE	/	FALSE	1735689600	CONSENT	xxx
```

## 🔄 自动保存机制

### 保存位置

Cookies 自动保存到：`./cookies.txt`

### 自动加载

- 应用启动时自动加载历史 cookies
- 无需每次重新输入
- 除非 cookies 过期

### 持久化

```
输入 Cookies
    ↓
保存到 session state（内存）
    ↓
保存到 cookies.txt（磁盘）
    ↓
下次启动自动加载
```

## 📊 状态显示

### 未配置状态

```
ℹ️ 未配置 Cookies
```

### 已配置状态

```
✓ Cookies 已配置（20 条）
```

显示 cookies 数量，方便确认

### 操作反馈

- 保存成功：`✓ Cookies 已保存`
- 清除成功：`✓ Cookies 已清除`
- 上传成功：`✓ Cookies 文件已上传`

## 🛠️ 管理功能

### 查看状态

侧边栏实时显示：
- 是否已配置
- Cookies 数量
- 配置时间（如果有）

### 更新 Cookies

1. 直接在文本框修改
2. 点击 "保存 Cookies"
3. 立即生效

### 清除 Cookies

1. 点击 "🗑️ 清除 Cookies"
2. 确认清除
3. 内存和文件都会清除

### 重新加载

1. 点击 "🔄 重新加载配置"
2. 重新读取配置文件
3. 刷新界面状态

## 🔒 安全建议

### ⚠️ 重要提醒

1. **Cookies 是敏感信息**
   - 相当于登录凭证
   - 不要分享给他人
   - 不要截图发送

2. **本地存储**
   - Cookies 只保存在本地
   - 不会上传到服务器
   - 文件权限建议设为私有

3. **定期更新**
   - Cookies 会过期（1-30天）
   - 过期后重新获取
   - 建议每周检查

### ✅ 最佳实践

1. **使用测试账号**
   ```
   创建专门的测试账号
   不要使用主账号
   降低安全风险
   ```

2. **及时清理**
   ```
   测试完成后清除 cookies
   或者在浏览器中退出登录
   使 cookies 失效
   ```

3. **定期更换**
   ```
   定期修改密码
   重新导出 cookies
   保持安全性
   ```

## 🧪 测试验证

### 验证 Cookies 是否有效

**方法 1：直接测试**

1. 配置 cookies
2. 输入视频链接
3. 点击开始处理
4. 观察是否成功下载

**方法 2：使用测试脚本**

```bash
python test_cookies.py
```

输出示例：
```
✓ Cookies 有效
视频标题: 测试视频
```

### 常见问题诊断

**问题 1：下载仍然失败**

检查清单：
- [ ] Cookies 格式是否正确
- [ ] 是否包含必要的字段
- [ ] Cookies 是否过期
- [ ] 账号是否被限制

**问题 2：Cookies 很快过期**

解决方案：
- 在浏览器中勾选 "保持登录"
- 不要在浏览器中退出登录
- 使用更稳定的账号

**问题 3：多平台冲突**

解决方案：
- 确保每个平台的 cookies 都完整
- 检查域名是否正确
- 尝试分别测试每个平台

## 💻 技术实现

### Session State

使用 Streamlit session state 管理：

```python
# 初始化
if 'cookies_content' not in st.session_state:
    st.session_state.cookies_content = ""

# 保存
st.session_state.cookies_content = cookies_input

# 使用
cookies = st.session_state.cookies_content
```

### 自动持久化

```python
# 保存到文件
cookies_path.write_text(cookies_input, encoding='utf-8')

# 启动时加载
if cookies_path.exists():
    st.session_state.cookies_content = cookies_path.read_text()
```

### 实时更新

```python
# 保存后刷新
st.rerun()

# 状态立即更新
```

## 📝 使用示例

### 示例 1：B站视频

```
1. 登录 bilibili.com
2. 导出 cookies（包含 SESSDATA）
3. 粘贴到应用
4. 输入链接：https://www.bilibili.com/video/BV1xx411c7mD
5. 开始处理
```

### 示例 2：小红书

```
1. 登录 xiaohongshu.com
2. 导出 cookies（包含 web_session）
3. 粘贴到应用
4. 输入小红书视频链接
5. 开始处理
```

### 示例 3：多平台

```
1. 分别登录 B站和小红书
2. 导出两个平台的 cookies
3. 合并到一个文本框
4. 保存
5. 可以处理两个平台的视频
```

## 🎯 优势总结

### vs 文件管理

| 特性 | 前端输入 | 文件管理 |
|------|---------|---------|
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 更新速度 | 即时 | 需要重新上传 |
| 可视化 | 清晰 | 不直观 |
| 历史保存 | 自动 | 手动 |
| 多平台 | 方便合并 | 需要手动编辑 |

### 用户体验

- ✅ 无需离开应用
- ✅ 即时反馈
- ✅ 操作简单
- ✅ 状态清晰
- ✅ 自动保存

## 🎬 Demo 演示

### 演示脚本（3分钟）

**1. 展示功能**（30秒）
- 打开侧边栏
- 展示 Cookies 配置区域
- 说明两种输入方式

**2. 文本输入演示**（1分钟）
- 打开浏览器
- 导出 cookies
- 复制内容
- 粘贴到应用
- 点击保存
- 显示成功提示

**3. 使用测试**（1分钟）
- 输入视频链接
- 开始处理
- 展示下载成功

**4. 更新演示**（30秒）
- 修改 cookies
- 重新保存
- 说明自动持久化

---

**更新时间**：2024-12-23  
**状态**：✅ 前端输入功能已完成
