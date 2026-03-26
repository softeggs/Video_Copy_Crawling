# iOS 局域网联调目标文档

## 文档目的

本文件用于指导 macOS 环境中的另一个 agent 对 `ios_app/iOS_Video_Intelligence` 工程进行最小改动联调。

目标不是重构 iOS App，也不是优化 iOS 前端页面，而是：

- 在不修改现有 iOS App 前端页面、交互和信息结构的前提下
- 仅通过最小配置改动、最小服务接入改动
- 让 iOS App 能在本地局域网环境下与当前 Windows 机器上的后端通信

## 当前联调约束

### 必须遵守

- 不改 iOS 前端页面布局
- 不改现有页面信息结构
- 不做 UI/UX 优化
- 不新增复杂抽象层
- 不重写整套数据流

### 允许修改

- API 基址配置
- 端口配置
- 环境切换配置
- 最小必要的服务接入层替换
- 最小必要的数据模型/解码修正
- 最小必要的 Auth / Repository 绑定切换

## 联调环境

### Windows 后端所在机器

- 当前局域网 IPv4：`192.168.0.32`
- 后端目标端口：`8002`
- 局域网联调基址：`http://192.168.0.32:8002`

### 注意事项

- iOS 真机或 macOS 模拟器局域网联调时，不应继续使用 `127.0.0.1`
- `127.0.0.1` 只代表设备自身，不代表 Windows 后端机器
- 如果局域网 IP 变化，应只改配置，不改页面代码

## 当前 iOS 工程现状

### 仍在使用旧链路的地方

1. `AppConfig.useFeishuDirect = true`
   文件：
   - `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift`

2. `AppServices.authService` 仍然绑定 `LocalMockAuthService()`
   文件：
   - `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift`

3. `videoRepository` 仍然绑定 `FeishuVideoRepository`
   文件：
   - `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift`

4. `APIService.swift` 中的接口路径仍是旧格式，和当前 FastAPI 后端不一致
   当前代码示例：
   - `/api/auth/token`
   - `/api/videos/submit`
   - `/api/videos/list`

### 当前后端真实接口

认证：

- `POST /auth/login`
- `POST /auth/register`
- `GET /auth/me`

视频：

- `POST /videos/submit`
- `GET /videos`
- `GET /videos/{id}`
- `GET /videos/stats`
- `GET /videos/overview`

健康检查：

- `GET /health`

## 当前 iOS 与后端的不一致点

### 认证接口不一致

iOS 当前：

- `POST /api/auth/token`

后端实际：

- `POST /auth/login`

### 列表接口不一致

iOS 当前：

- `GET /api/videos/list`

后端实际：

- `GET /videos?page=1&page_size=20`

### 数据源不一致

iOS 当前主链路仍是：

- 本地 Mock 登录
- 飞书直连 Repository

目标主链路应切换为：

- 后端登录
- 后端视频列表
- 后端视频详情
- 后端视频提交
- 后端概览/统计

## macOS agent 修改目标

### 第一优先级：只完成通信，不改页面

必须完成：

1. 将 iOS 默认服务地址切换到局域网地址
   目标基址：
   - `http://192.168.0.32:8002`

2. 让认证走后端真实接口
   目标：
   - 登录页通过 `/auth/login` 获取 token 和 user

3. 让提交页走后端真实接口
   目标：
   - 提交视频通过 `/videos/submit`

4. 让历史页走后端真实接口
   目标：
   - 通过 `/videos` 拉列表
   - 保持现有分页/筛选入口尽量不改 UI

5. 让详情页走后端真实接口
   目标：
   - 通过 `/videos/{id}` 拉详情

6. 让个人页走后端真实接口
   目标：
   - 优先使用 `/videos/overview`
   - 如已有本地用户信息展示逻辑，仅补后端统计数据

### 第二优先级：最小清理旧链路

必须做到：

- 不再让默认模式依赖飞书直连
- 不再让默认模式依赖本地 Mock 登录

允许保留：

- 飞书直连代码
- Mock 登录代码

但要求：

- 这些代码只能作为保底或测试分支存在
- 默认联调入口必须切到统一后端

## 建议最小修改文件

高优先级建议检查：

- `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift`
- `ios_app/iOS_Video_Intelligence/Services/APIService.swift`
- `ios_app/iOS_Video_Intelligence/Services/AuthService.swift`
- `ios_app/iOS_Video_Intelligence/Services/AuthManager.swift`
- `ios_app/iOS_Video_Intelligence/Services/VideoRepository.swift`
- `ios_app/iOS_Video_Intelligence/Models/VideoRecord.swift`

低优先级：

- `Views/*.swift`

说明：

- 视图层仅允许做“为了接现有接口所需的最小绑定调整”
- 不允许进行页面重构和界面优化

## 建议实现策略

### 推荐做法

1. 在 `AppConfig.Server.baseURL` 中直接写局域网地址
   - `http://192.168.0.32:8002`

2. 新建或修正一个后端模式的 AuthService
   - 对接 `/auth/login`

3. 新建或修正一个后端模式的 VideoRepository
   - `fetchRecords` -> `/videos`
   - `fetchRecord` -> `/videos/{id}`
   - `submitVideo` -> `/videos/submit`
   - `fetchTypeStats` -> `/videos/stats`

4. 将 `AppServices` 默认绑定切换到“后端模式”

### 不推荐做法

- 为了兼容旧代码而大量改 View
- 将飞书字段模型硬塞进后端 DTO
- 继续沿用 `/api/...` 旧路径再在后端做兼容层
- 为了联调去重写整个 iOS 工程

## 后端返回结构提示

### 登录返回

`POST /auth/login`

返回结构：

```json
{
  "token": "string",
  "user": {
    "user_id": "string",
    "username": "string",
    "display_name": "string",
    "table_id": "string"
  }
}
```

### 提交返回

`POST /videos/submit`

```json
{
  "success": true,
  "record_id": "string",
  "status": "待处理",
  "estimated_time": "2-5分钟",
  "message": null
}
```

### 列表返回

`GET /videos`

```json
{
  "total": 1,
  "page": 1,
  "page_size": 20,
  "items": [],
  "has_more": false
}
```

## iOS 手动测试点

以下测试由你手动执行，要求逐项记录结果。

### A. 基础连通性

1. App 能正常启动
2. 不改页面布局的前提下，能正常进入登录页
3. 不出现明显因局域网地址导致的初始化崩溃

### B. 登录联调

1. 输入有效用户名密码可以登录成功
2. 登录后能持久化 token
3. 重启 App 后登录态符合当前设计预期
4. 无效密码时能收到明确错误提示

### C. 提交联调

1. 合法 URL 可以提交成功
2. 非法 URL 会收到后端或前端已有逻辑的拦截反馈
3. 提交成功后不会破坏当前页面结构

### D. 历史记录联调

1. 能拉到当前账号的视频列表
2. 分页能正常工作
3. 状态筛选如已存在，能返回正确结果
4. 空列表时不会崩溃

### E. 详情页联调

1. 能进入单条视频详情
2. 能看到标题、摘要、状态等基础信息
3. 对于未完成或空内容记录，页面能稳定展示

### F. 个人页联调

1. 能显示当前用户基本信息
2. 能显示总视频数、今日新增、待处理等统计
3. 没有统计数据时页面不崩溃

### G. 局域网特有验证

1. 关闭 Windows 本机浏览器后，iOS 仍可访问后端
2. iOS 使用的基址明确为 `192.168.0.32:8002`
3. 不能再出现任何默认 `127.0.0.1` 联调地址

## 联调通过标准

满足以下条件即可认为本轮 iOS 联调通过：

- 不改现有 iOS 页面结构
- iOS 默认入口成功切到统一后端
- 登录、提交、历史、详情、个人页全部能通信
- 局域网环境下可稳定访问 Windows 后端
- 未再依赖默认飞书直连和本地 Mock 登录作为主链路

## 交付要求给 macOS agent

macOS 侧 agent 完成后，应至少给出：

1. 修改了哪些文件
2. 哪些改动只是配置切换
3. 哪些改动是最小必要的服务接入修正
4. 哪些旧链路代码被保留但不再作为默认入口
5. 当前仍剩余哪些联调问题

## 本地后端保持要求

Windows 侧联调期间，后端需保持可访问：

- 监听地址：`0.0.0.0`
- 端口：`8002`
- 局域网访问地址：`http://192.168.0.32:8002`

如果后端重启或 IP 变化，本文件中的局域网地址需要同步更新。
