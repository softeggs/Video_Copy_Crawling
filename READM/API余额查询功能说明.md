# API 余额查询功能说明

## 📋 功能概述

新增了完整的 API Key 余额查询功能，支持多个查询接口：
- **订阅信息接口**: 查询总额度、支付方式等
- **使用量接口**: 查询指定时间段的使用量统计
- **调用记录接口**: 查询最近的 API 调用详情
- **综合查询**: 整合所有信息，自动计算剩余额度

## 🚀 使用方法

### 1. 快速查询余额

运行余额查询脚本：

```bash
python check_balance.py
```

输出示例：
```
✅ 剩余额度: $1.16 / $2.20 | 总额度: $2.20 | 最近 30 天使用: 104 usage ($1.04) | 13 次调用，35,516 tokens

💰 额度详情:
  总额度: $2.20
  已使用: $1.04 (47.3%)
  剩余额度: $1.16
  ⚠️  提示: 余额较低，建议关注

📊 使用统计:
  总使用量: 104 usage
  等价费用: $1.04

📝 最近 5 次调用:
  1. 2025-12-24 11:32:35
     模型: gemini-3-pro-preview-h
     Tokens: 372 (输入: 9, 输出: 363)
     耗时: 8s
  ...
```

### 2. 详细测试（所有接口）

运行详细测试脚本：

```bash
python test_balance_detailed.py
```

这会测试所有查询接口并显示原始数据。

### 2. 自动查询（API 失败时）

当 AI 处理失败时，系统会自动查询余额并显示在日志中：

```python
# 在 core/ai_processor.py 中自动触发
# 无需手动调用
```

日志输出示例：
```
2025-12-25 14:00:00 - ERROR - AI 处理最终失败: ...
2025-12-25 14:00:01 - INFO - 正在查询 API Key 余额...
💰 剩余额度: $1.16 / $2.20 | 总额度: $2.20 | 最近 30 天使用: 104 usage ($1.04)
```

### 3. 在代码中使用

```python
from utils.api_balance_checker import APIBalanceChecker

# 创建检查器
checker = APIBalanceChecker("https://api2.qiandao.mom/v1")

# 综合查询（推荐）
result = checker.check_balance("sk-your-api-key")
if result and result['success']:
    print(f"剩余额度: ${result['remaining']:.2f}")
    print(f"总额度: ${result['total_limit']:.2f}")
    print(f"已使用: ${result['used_amount']:.2f}")

# 单独查询订阅信息
subscription = checker.check_subscription("sk-your-api-key")

# 单独查询使用量（最近 30 天）
usage = checker.check_usage("sk-your-api-key", days=30)
```

## 📊 查询接口说明

### 1. 订阅信息接口

**端点**: `GET /v1/dashboard/billing/subscription`

**返回示例**:
```json
{
  "object": "billing_subscription",
  "has_payment_method": true,
  "soft_limit_usd": 2.2,
  "hard_limit_usd": 2.2,
  "system_hard_limit_usd": 2.2,
  "access_until": 0
}
```

**说明**:
- `hard_limit_usd`: 总额度（美元）
- `soft_limit_usd`: 软限制额度
- `has_payment_method`: 是否绑定支付方式

### 2. 使用量接口

**端点**: `GET /v1/dashboard/billing/usage?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

**返回示例**:
```json
{
  "object": "list",
  "total_usage": 104
}
```

**说明**:
- `total_usage`: 总使用量（usage 单位）
- **重要**: 1 usage = $0.01
- 费用计算: `total_usage × 0.01 = 总费用（美元）`

### 3. 调用记录接口

**端点**: `GET /api/log/token?key=<api-key>`

**返回示例**:
```json
{
  "data": [
    {
      "id": 981,
      "created_at": 1766547155,
      "model_name": "gemini-3-pro-preview-h",
      "quota": 40000,
      "prompt_tokens": 9,
      "completion_tokens": 363,
      "use_time": 8
    }
  ],
  "success": true
}
```

**说明**:
- 返回最近的 API 调用记录
- 包含 token 使用量、耗时等详细信息

## 💰 余额计算公式

```
剩余额度 = 总额度 - (总使用量 × 0.01)
```

**示例**:
- 总额度: $2.20
- 总使用量: 104 usage
- 已使用: 104 × $0.01 = $1.04
- 剩余额度: $2.20 - $1.04 = $1.16

## 📊 返回数据说明

### 综合查询返回格式

```python
{
    'success': True,
    'subscription': {  # 订阅信息
        'success': True,
        'data': {...},
        'message': '总额度: $2.20'
    },
    'usage': {  # 使用量信息
        'success': True,
        'data': {...},
        'message': '最近 30 天使用: 104 usage ($1.04)'
    },
    'logs': {  # 调用记录
        'success': True,
        'data': {...},
        'message': '13 次调用，35,516 tokens'
    },
    'message': '剩余额度: $1.16 / $2.20 | 总额度: $2.20 | ...',
    'remaining': 1.16,  # 剩余额度
    'total_limit': 2.20,  # 总额度
    'used_amount': 1.04  # 已使用额度
}
```

## 🔧 配置要求

余额查询功能需要以下配置（在 `.env` 文件中）：

```env
# 必需：API Key
OPENAI_API_KEY=sk-your-api-key-here

# 必需：中转 API 的 Base URL
OPENAI_BASE_URL=https://api2.qiandao.mom/v1
```

## �  使用场景

### 1. 定期检查使用情况
```bash
# 每天运行一次，了解 API 使用情况
python check_balance.py
```

### 2. 调试 API 问题
当 AI 处理失败时，查看余额信息可以帮助判断：
- API Key 是否有效
- 是否还有剩余额度
- 最近的调用是否成功
- 使用率是否过高

### 3. 成本监控
通过查看使用统计，可以：
- 了解每次调用的成本
- 优化 prompt 以减少 usage
- 预估未来的 API 费用
- 设置余额警告阈值

### 4. 预估可用次数
根据剩余额度和平均消耗，预估还能调用多少次：
```
剩余可调用次数 ≈ 剩余额度 / 0.01
例如: $1.16 / $0.01 = 116 次
```

## 🎯 统计信息说明

### Usage 说明
- **1 usage = $0.01**
- 每次 API 调用消耗的 usage 数量不固定
- 取决于输入输出的 token 数量和模型类型

### Token 统计
- **输入 tokens (prompt_tokens)**: 发送给 AI 的文本长度
- **输出 tokens (completion_tokens)**: AI 返回的文本长度
- **总 tokens**: 输入 + 输出

### 余额警告
- 剩余 < $1.00: ⚠️ 警告，建议及时充值
- 剩余 < $5.00: ⚠️ 提示，建议关注
- 使用率 > 80%: 建议充值或更换 API Key

### 耗时统计
- **use_time**: 每次 API 调用的响应时间（秒）
- 可用于评估 API 性能和优化超时设置

## ⚠️ 注意事项

1. **仅支持中转 API**
   - 此功能仅适用于配置了 `OPENAI_BASE_URL` 的中转 API
   - OpenAI 官方 API 和 Gemini 官方 API 不支持此查询接口

2. **网络要求**
   - 需要能够访问中转 API 的查询端点
   - 查询超时时间为 10 秒

3. **隐私保护**
   - API Key 在日志中会被部分隐藏（只显示前 20 个字符）
   - 建议不要在公共环境中运行查询命令

## 🔍 故障排查

### 查询失败（404）
```
❌ 查询失败（状态码: 404）
```
**原因**: Base URL 配置错误或查询端点不存在  
**解决**: 检查 `OPENAI_BASE_URL` 配置是否正确

### 查询超时
```
❌ 查询超时，请检查网络连接
```
**原因**: 网络连接问题或 API 服务响应慢  
**解决**: 检查网络连接，稍后重试

### API Key 无效
```
❌ 查询失败（状态码: 401）
```
**原因**: API Key 错误或已过期  
**解决**: 更新 `.env` 文件中的 `OPENAI_API_KEY`

## 📚 相关文件

- `utils/api_balance_checker.py` - 余额查询核心模块
- `check_balance.py` - 命令行查询工具（快速查询）
- `test_balance_detailed.py` - 详细测试脚本（所有接口）
- `core/ai_processor.py` - 集成了自动查询功能
- `test_balance_on_failure.py` - 失败场景测试

## 🎉 总结

余额查询功能让你可以：
- ✅ 实时了解 API 余额和使用情况
- ✅ 快速诊断 API 调用问题
- ✅ 监控成本和优化使用
- ✅ 在失败时自动获取诊断信息
- ✅ 预估剩余可用次数
- ✅ 设置余额警告阈值

建议定期运行 `python check_balance.py` 来监控 API 使用情况！

## 📖 更多信息

- 余额计算公式: `剩余 = 总额度 - (usage × 0.01)`
- 1 usage = $0.01
- 支持查询最近 30 天的使用量
- 自动整合多个查询接口的数据
- 提供友好的余额警告提示
