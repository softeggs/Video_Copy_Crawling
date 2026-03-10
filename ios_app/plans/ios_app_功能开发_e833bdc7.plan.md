---
name: iOS App 功能开发
overview: iOS 直连飞书 REST API 作为临时数据库，通过 Repository 协议层做好抽象，实现真实登录、Records 数据展示、主页类型统计、视频链接提交四大功能，未来只需替换实现层即可接入真实服务器。
todos:
  - id: feishu-service
    content: 新建 FeishuAPIClient.swift（飞书 Token 获取 + CRUD）和 AppConfig.swift（配置常量）
    status: pending
  - id: repository-protocol
    content: 新建 VideoRepository.swift（Repository 协议 + FeishuVideoRepository 实现）和 AuthService.swift（Auth 协议 + LocalMockAuthService 实现）
    status: pending
  - id: auth-manager
    content: 修改 AuthManager.swift：移除 mock_token，接入 AuthService 协议，支持 UserDefaults 持久化登录态
    status: pending
  - id: models-update
    content: 更新 VideoRecord.swift：新增 TypeStat、FeishuRecord 等模型
    status: pending
  - id: views-update
    content: 更新 LoginView（账号提示）、SubmitView（动态类型统计）、HistoryView（真实数据 + 分页）
    status: pending
isProject: false
---

# iOS App 功能开发计划（修订版）

## 核心变更：去掉 Python 后端，iOS 直连飞书

> 现阶段不开发 Python FastAPI 后端。iOS App 直接调用飞书 Open API REST 接口，  
> 但用协议层隔离，保证未来切换真实服务器时 View 层代码**零改动**。

## 架构设计

```
Views (SwiftUI)
      ↓  使用协议，不关心实现
Repository 协议层
      ↓  当前实现        ↓ 未来实现
FeishuVideoRepository   ServerVideoRepository
      ↓                       ↓
飞书 REST API            真实后端 API
(open.feishu.cn)        (你的服务器)
```

数据库设计约定（未来服务器对接时的接口规范）：

- 每个用户对应一个独立的飞书表格（`table_id` 绑定到 user）
- 用户信息接口：`POST /auth/login` → `{token, user_id, table_id, display_name}`
- 视频数据接口：全部带 Bearer Token，服务器根据 token 识别用户和对应表格

---

## Part 1：新建服务层文件

### 1.1 `Services/AppConfig.swift`（新建）

集中管理所有配置常量，未来切换服务器只改这一个文件：

```swift
enum AppConfig {
    // ── 当前模式 ──────────────────────────────────────────
    // 切换到服务器模式时，将 useFeishuDirect 改为 false
    static let useFeishuDirect = true

    // ── 飞书直连配置（测试阶段）────────────────────────────
    enum Feishu {
        static let appId     = "cli_a9c17878db38dced"
        static let appSecret = "PJkZZukSOeKMdUQluzT2aeYqC3ZRZfYp"
        static let appToken  = "ZPKVb5lDqaoRpAsBv7wccjuAnOe"
        static let baseURL   = "https://open.feishu.cn/open-apis"
    }

    // ── 服务器配置（未来启用）──────────────────────────────
    enum Server {
        static let baseURL = "https://your-server.com/api"  // TODO: 替换为真实地址
    }
}
```

### 1.2 `Services/FeishuAPIClient.swift`（新建）

负责飞书 REST API 的底层通信：

- `getTenantAccessToken()` → 获取并缓存飞书 tenant_access_token（2小时自动过期刷新）
- `listRecords(tableId:pageToken:pageSize:filter:)` → 查询记录列表
- `getRecord(tableId:recordId:)` → 查询单条记录
- `createRecord(tableId:fields:)` → 创建新记录（提交视频 URL 用）

飞书 API 端点：

- `POST /auth/v3/tenant_access_token/internal` → token
- `GET  /bitable/v1/apps/{appToken}/tables/{tableId}/records` → 列表
- `GET  /bitable/v1/apps/{appToken}/tables/{tableId}/records/{recordId}` → 详情
- `POST /bitable/v1/apps/{appToken}/tables/{tableId}/records` → 创建

### 1.3 `Services/VideoRepository.swift`（新建）

定义 Repository 协议，并提供飞书实现：

```swift
// ── 未来服务器接口规范（协议即接口文档）────────────────────
protocol VideoRepositoryProtocol {
    func fetchRecords(tableId: String, page: Int, status: String?) async throws -> VideoListResponse
    func fetchRecord(tableId: String, recordId: String) async throws -> VideoRecord
    func submitVideo(tableId: String, url: String) async throws -> VideoSubmitResponse
    func fetchTypeStats(tableId: String) async throws -> [TypeStat]
}

// ── 当前实现：直连飞书 ──────────────────────────────────────
class FeishuVideoRepository: VideoRepositoryProtocol { ... }

// ── 未来实现占位（切换服务器时填充）─────────────────────────
// class ServerVideoRepository: VideoRepositoryProtocol { ... }
```

飞书字段映射（中文字段名 → Swift 模型）：


| 飞书字段  | Swift 字段        | 备注                  |
| ----- | --------------- | ------------------- |
| 标题    | title           | String              |
| 作者    | author          | String              |
| 一句话总结 | summary         | String              |
| 核心观点  | corePoints      | 多行文本，按换行分割          |
| 详细内容  | correctedText   | 长文本                 |
| 金句    | goldenSentences | 多行文本，按换行分割          |
| 标签    | tags            | 飞书多选，返回 [{text}] 数组 |
| 视频类型  | videoType       | 单选                  |
| 处理状态  | status          | 单选                  |
| 原始链接  | url             | 链接类型，取 .link        |
| 处理时间  | processedAt     | 毫秒时间戳转 ISO8601      |


### 1.4 `Services/AuthService.swift`（新建）

```swift
// ── 未来服务器认证接口规范 ────────────────────────────────
protocol AuthServiceProtocol {
    func login(username: String, password: String) async throws -> LoginResponse
    // 未来扩展：register、resetPassword 等
}

// ── 当前实现：本地 Mock（test / 0104）────────────────────
class LocalMockAuthService: AuthServiceProtocol {
    // 本地验证账号密码，返回与飞书表格绑定的用户信息
    // 账号: test  密码: 0104  →  table_id: tbl339YsqSYxEygQ
}

// ── 未来实现占位 ──────────────────────────────────────────
// class ServerAuthService: AuthServiceProtocol { ... }
```

---

## Part 2：修改现有文件

### 2.1 `Services/AuthManager.swift`

- 移除 `mock_token` 自动登录逻辑，初始 `isAuthenticated = false`
- 持有 `AuthServiceProtocol` 实例（当前注入 `LocalMockAuthService`）
- App 启动时从 `UserDefaults` 恢复已登录状态（记住登录）
- 持有当前用户的 `tableId`（传给 Repository 使用）

### 2.2 `Models/VideoRecord.swift`

新增模型：

```swift
struct TypeStat: Identifiable {
    var id: String { videoType }
    let videoType: String
    let count: Int
}
```

### 2.3 `Views/LoginView.swift`

- 测试账号提示改为 `"测试账号：test / 0104"`
- 密码已使用 `SecureField`（密文显示）✓

### 2.4 `Views/SubmitView.swift`

- `onAppear` 时调用 `VideoRepository.fetchTypeStats(tableId:)`
- 将底部固定统计数字替换为动态视频类型统计卡片，例如：

```
  教程类  42    工具类  18
  评测类  15    其他    31
  

```

- 保留 "Today / Processing" 统计（从类型统计 API 同时获取）

### 2.5 `Views/HistoryView.swift`

- 列表数据改为调用 `VideoRepository.fetchRecords(tableId:page:status:)`
- VideoCard 已有标题/摘要/标签显示 ✓，需确保飞书标签字段正确解析

---

## 接口预留说明（给未来服务器对接）

未来只需：

1. 实现 `ServerVideoRepository` 和 `ServerAuthService`
2. 在 `AppConfig.swift` 将 `useFeishuDirect` 改为 `false`
3. 在 `AuthManager` 和视图的依赖注入处替换实现类

**View 层代码完全不需要修改。**

---

## 安全说明

飞书 `appId` / `appSecret` 当前硬编码在 `AppConfig.swift`，仅供开发测试。  
生产环境应由服务器持有密钥，iOS 只持有服务器颁发的用户 token。