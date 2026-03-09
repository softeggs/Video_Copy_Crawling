# 定时任务自动启动配置指南

## 📋 功能说明

系统支持在 Docker 启动时自动开启定时任务，无需每次手动在界面中启动。

## ⚙️ 配置方法

### 1. 编辑 .env 文件

在 `.env` 文件中添加或修改以下配置：

```bash
# 定时任务配置
AUTO_START_SCHEDULER=true                  # 设置为 true 启用自动启动
SCHEDULER_CHECK_INTERVAL=300               # 检查间隔（秒），默认 300 秒（5 分钟）
```

### 2. 配置飞书信息（必需）

自动启动需要完整的飞书配置：

```bash
FEISHU_APP_ID=cli_your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_BITABLE_APP_TOKEN=your_bitable_app_token
FEISHU_BITABLE_TABLE_ID=your_table_id
```

### 3. 重启 Docker 容器

```bash
docker-compose restart video-processor-web
```

或者完全重新启动：

```bash
docker-compose down
docker-compose up -d video-processor-web
```

## 🎯 配置示例

### 示例 1: 每 5 分钟检查一次（默认）

```bash
AUTO_START_SCHEDULER=true
SCHEDULER_CHECK_INTERVAL=300
```

### 示例 2: 每 10 分钟检查一次

```bash
AUTO_START_SCHEDULER=true
SCHEDULER_CHECK_INTERVAL=600
```

### 示例 3: 每 30 分钟检查一次

```bash
AUTO_START_SCHEDULER=true
SCHEDULER_CHECK_INTERVAL=1800
```

### 示例 4: 每 1 小时检查一次

```bash
AUTO_START_SCHEDULER=true
SCHEDULER_CHECK_INTERVAL=3600
```

### 示例 5: 禁用自动启动（手动控制）

```bash
AUTO_START_SCHEDULER=false
```

## ✅ 验证自动启动

### 方法 1: 查看界面提示

启动后访问 http://localhost:8501，如果自动启动成功，会在右上角看到提示：

```
✅ 定时任务已自动启动（每 X 分钟检查一次）
```

### 方法 2: 查看定时任务状态

在界面中进入 "⏰ 定时任务" 标签页，查看状态：

- 🟢 运行中 - 表示定时任务已启动
- ⚪ 未运行 - 表示定时任务未启动

### 方法 3: 查看日志

```bash
docker-compose logs -f video-processor-web
```

如果看到类似日志，说明自动启动成功：

```
后台定时任务已启动，检查间隔: 300秒
后台定时任务线程启动
```

## 🔧 工作原理

1. **Docker 启动** → 容器启动，Streamlit 应用运行
2. **检查配置** → 读取 `AUTO_START_SCHEDULER` 配置
3. **验证飞书** → 检查飞书配置是否完整
4. **自动启动** → 如果配置正确，自动启动后台定时任务
5. **持续运行** → 按设定间隔自动检查和处理空白链接

## 📊 两种运行模式对比

### 模式 1: 自动启动（推荐）

**配置：**
```bash
AUTO_START_SCHEDULER=true
```

**优点：**
- ✅ Docker 启动后自动运行
- ✅ 无需手动操作
- ✅ 适合长期运行

**适用场景：**
- 生产环境
- 需要 24/7 自动处理
- 团队协作

### 模式 2: 手动启动

**配置：**
```bash
AUTO_START_SCHEDULER=false
```

**优点：**
- ✅ 完全手动控制
- ✅ 可以随时启动/停止
- ✅ 适合测试和调试

**适用场景：**
- 开发测试
- 临时使用
- 需要精确控制执行时间

## 🎛️ 运行时控制

即使启用了自动启动，你仍然可以在界面中：

1. **查看状态** - 实时查看运行状态和最后检查时间
2. **停止任务** - 点击"停止定时任务"按钮
3. **重新启动** - 停止后可以重新启动
4. **立即执行** - 点击"立即执行一次"手动触发
5. **修改间隔** - 停止后可以修改检查间隔并重新启动

## 🔄 修改配置后生效

修改 `.env` 文件后，需要重启容器：

```bash
# 方法 1: 快速重启
docker-compose restart video-processor-web

# 方法 2: 完全重启（推荐）
docker-compose down
docker-compose up -d video-processor-web
```

## 💡 最佳实践

### 1. 选择合适的检查间隔

- **高频使用**（1-5 分钟）：适合测试环境或需要快速响应
- **中频使用**（5-10 分钟）：推荐用于个人使用
- **低频使用**（10-30 分钟）：适合团队使用
- **极低频**（30-60 分钟）：适合低频更新的场景

### 2. 监控运行状态

定期查看日志，确保任务正常运行：

```bash
docker-compose logs -f video-processor-web | grep "定时"
```

### 3. 资源优化

如果服务器资源有限，可以：
- 增加检查间隔（减少 CPU 使用）
- 使用独立定时任务容器（分离资源）

### 4. 错误处理

如果自动启动失败，检查：
- ✅ 飞书配置是否完整
- ✅ `.env` 文件格式是否正确
- ✅ Docker 容器是否有权限访问文件

## 🆘 常见问题

### Q1: 自动启动没有生效？

**检查清单：**
1. `.env` 中 `AUTO_START_SCHEDULER=true`
2. 飞书配置完整（4 个参数都配置）
3. 重启了 Docker 容器
4. 查看日志是否有错误信息

### Q2: 如何临时禁用自动启动？

**方法 1: 修改配置**
```bash
# 编辑 .env
AUTO_START_SCHEDULER=false

# 重启容器
docker-compose restart video-processor-web
```

**方法 2: 在界面中停止**
- 进入"定时任务"标签页
- 点击"停止定时任务"

### Q3: 自动启动后可以修改检查间隔吗？

可以，但需要重新启动：
1. 在界面中停止当前任务
2. 选择新的检查间隔
3. 点击"启动定时任务"

或者修改 `.env` 中的 `SCHEDULER_CHECK_INTERVAL` 并重启容器。

### Q4: 自动启动会影响手动处理吗？

不会。定时任务和手动处理是独立的，互不影响。

### Q5: 如何查看定时任务的执行历史？

在"定时任务"标签页可以看到：
- 上次检查时间
- 处理结果（总计、成功、失败）
- 执行耗时

详细日志可以通过以下命令查看：
```bash
docker-compose logs video-processor-web
```

## 📚 相关文档

- [Docker 部署指南](./DOCKER_GUIDE.md)
- [定时任务使用指南](./定时任务使用指南.md)
- [定时任务快速开始](./定时任务快速开始.md)
