# URL 清理功能说明

## 功能概述

系统现在支持自动清理视频 URL 中的敏感信息和不必要的参数，同时保留视频访问所需的关键参数。

## 清理策略

### 默认模式（保守清理）⭐ **推荐**

**只移除敏感信息**，保留所有其他参数：

#### 移除的参数类型：
- **Cookies 和 Token**
  - `cookie`, `cookies`
  - `session`, `sessdata`
  - `token`, `access_token`, `auth_token`
  - `xsec_token`（小红书安全令牌）
  - `auth`, `key`, `secret`, `api_key`

- **用户标识**（隐私保护）
  - `uid`, `user_id`, `openid`

- **设备标识**（隐私保护）
  - `device_id`, `imei`, `mac`

#### 保留的参数：
- ✅ 所有视频定位参数
- ✅ 平台功能参数
- ✅ 分享参数（可能影响视频访问）
- ✅ 时间戳和版本信息

### 深度清理模式（激进清理）

**额外移除追踪参数**，可能影响某些视频访问：

#### 额外移除：
- 分享追踪：`share_source`, `share_medium`, `share_session_id`, `share_id`, `share_tag`
- 来源追踪：`from_source`, `from_spmid`, `spm_id_from`, `enter_from`, `enter_method`, `previous_page`
- 营销追踪：`utm_source`, `utm_medium`, `utm_campaign`

⚠️ **注意**：深度清理可能导致某些视频无法访问，建议只在必要时使用。

## 使用方法

### 在应用中使用

1. **输入视频链接**
   - 粘贴完整的视频 URL

2. **选择清理模式**
   - 默认：保守清理（推荐）
   - 勾选"深度清理"：激进清理

3. **自动处理**
   - 系统自动检测并清理 URL
   - 显示清理结果和详情

### 清理示例

#### B站视频

**原始 URL**:
```
https://www.bilibili.com/video/BV1JiqSBaEpm/?spm_id_from=333.1007.tianma.3-3-9.click&vd_source=abc123&session=xyz
```

**保守清理后**:
```
https://www.bilibili.com/video/BV1JiqSBaEpm/?spm_id_from=333.1007.tianma.3-3-9.click&vd_source=abc123
```
移除：`session` (敏感信息)
保留：`spm_id_from`, `vd_source` (可能需要)

**深度清理后**:
```
https://www.bilibili.com/video/BV1JiqSBaEpm/?vd_source=abc123
```
额外移除：`spm_id_from` (追踪参数)

#### 小红书视频

**原始 URL**:
```
https://www.xiaohongshu.com/explore/693c2d5c000000001e010175?app_platform=ios&app_version=8.97.1&xsec_token=ABC123&type=video&share_id=xyz
```

**保守清理后**:
```
https://www.xiaohongshu.com/explore/693c2d5c000000001e010175?app_platform=ios&app_version=8.97.1&type=video&share_id=xyz
```
移除：`xsec_token` (安全令牌)
保留：其他所有参数

**深度清理后**:
```
https://www.xiaohongshu.com/explore/693c2d5c000000001e010175?app_platform=ios&app_version=8.97.1&type=video
```
额外移除：`share_id` (追踪参数)

## 技术实现

### URLCleaner 类

```python
from utils.url_cleaner import URLCleaner

# 保守清理（默认）
cleaned_url = URLCleaner.clean_url(url, platform_name, aggressive=False)

# 深度清理
cleaned_url = URLCleaner.clean_url(url, platform_name, aggressive=True)

# 验证 URL
is_valid = URLCleaner.is_valid_video_url(url)

# 提取视频 ID
video_id = URLCleaner.extract_video_id(url, platform_name)
```

### 自动检测

系统会自动：
1. 验证 URL 格式
2. 检测视频平台
3. 清理敏感参数
4. 保留必要参数
5. 显示清理结果

## 优势

### 1. 隐私保护
- 移除个人标识信息
- 移除设备指纹
- 移除会话令牌

### 2. 安全性
- 防止 token 泄露
- 防止 cookies 暴露
- 防止 API key 泄露

### 3. 简洁性
- URL 更短更清晰
- 易于分享和存储
- 减少不必要的参数

### 4. 兼容性
- 保守模式确保视频可访问
- 保留平台必需参数
- 向后兼容

## 注意事项

### 1. 保守清理（默认）
✅ **优点**：
- 确保视频可访问
- 保留所有功能参数
- 安全可靠

⚠️ **限制**：
- 可能保留一些追踪参数
- URL 可能仍然较长

### 2. 深度清理
✅ **优点**：
- URL 更简洁
- 移除所有追踪
- 隐私保护更好

⚠️ **风险**：
- 可能影响视频访问
- 某些功能可能失效
- 需要测试验证

## 最佳实践

### 推荐做法

1. **默认使用保守清理**
   - 适用于大多数场景
   - 确保功能正常

2. **必要时使用深度清理**
   - 需要最大隐私保护
   - 确认不影响访问后使用

3. **验证清理结果**
   - 查看清理详情
   - 确认视频可访问
   - 测试下载功能

### 故障排查

**如果清理后无法访问视频**：

1. 取消勾选"深度清理"
2. 使用原始 URL
3. 检查是否移除了必需参数
4. 联系技术支持

## 测试工具

### 命令行测试

```bash
# 运行测试脚本
python test_url_cleaner.py
```

测试内容：
- URL 格式验证
- 清理功能测试
- 视频 ID 提取
- 边界情况处理

### 手动测试

```python
from utils.url_cleaner import URLCleaner

# 测试 URL
url = "https://www.bilibili.com/video/BV123?session=abc&spm_id_from=333"

# 保守清理
cleaned = URLCleaner.clean_url(url, aggressive=False)
print(f"保守清理: {cleaned}")

# 深度清理
cleaned_aggressive = URLCleaner.clean_url(url, aggressive=True)
print(f"深度清理: {cleaned_aggressive}")
```

## 常见问题

### Q1: 为什么有些参数没有被移除？
A: 保守模式只移除明确的敏感信息，保留可能影响视频访问的参数。

### Q2: 深度清理后视频无法访问怎么办？
A: 取消勾选"深度清理"，使用保守模式或原始 URL。

### Q3: 如何知道哪些参数被移除了？
A: 点击"查看清理详情"展开查看原始 URL 和清理后的对比。

### Q4: 可以完全不清理吗？
A: 可以，直接使用原始 URL，系统会自动处理。

### Q5: 清理会影响下载质量吗？
A: 不会。清理只影响 URL 参数，不影响视频内容和质量。

## 更新日志

### v2.0 (2024-12-24)
- ✅ 实现保守清理模式（默认）
- ✅ 实现深度清理模式（可选）
- ✅ 添加 URL 验证功能
- ✅ 添加视频 ID 提取
- ✅ 添加清理详情显示
- ✅ 支持 B站、小红书、抖音

### 未来计划
- ⏳ 智能清理（AI 判断必需参数）
- ⏳ 自定义清理规则
- ⏳ 批量 URL 清理
- ⏳ 清理历史记录

## 总结

URL 清理功能提供了：
1. ✅ 隐私保护（移除敏感信息）
2. ✅ 安全性（防止泄露）
3. ✅ 兼容性（保留必需参数）
4. ✅ 灵活性（两种清理模式）

**推荐配置**：
- 日常使用：保守清理（默认）
- 隐私优先：深度清理（测试后使用）

---

**更新时间**: 2024-12-24
**版本**: v2.0
