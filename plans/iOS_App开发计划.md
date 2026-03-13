# iOS App 开发计划（当前阶段）

> 创建时间：2026-03-12  
> 最后更新：2026-03-12  
> 对应 `ios_app/plans/ios_app_功能开发_e833bdc7.plan.md` 的执行追踪

---

## 架构回顾

```
Views (SwiftUI)
      ↓  使用协议，不关心实现
Repository 协议层
      ↓  当前实现            ↓ 未来实现
FeishuVideoRepository    ServerVideoRepository
      ↓                         ↓
飞书 REST API              真实后端 API
```

---

## 已完成任务

| 任务 ID | 内容 | 状态 | 完成文件 |
|---------|------|------|----------|
| feishu-service | 新建 FeishuAPIClient.swift + AppConfig.swift | ✅ 完成 | `Services/FeishuAPIClient.swift`、`Services/AppConfig.swift` |
| repository-protocol | 新建 VideoRepository.swift + AuthService.swift | ✅ 完成 | `Services/VideoRepository.swift`、`Services/AuthService.swift` |
| auth-manager | 修改 AuthManager.swift：接入 AuthService 协议 + UserDefaults 持久化 | ✅ 完成 | `Services/AuthManager.swift` |
| models-update | 更新 VideoRecord.swift：新增 TypeStat、FeishuRecord 等模型 | ✅ 完成 | `Models/VideoRecord.swift` |
| views-update | 更新 LoginView、SubmitView（动态类型统计）、HistoryView（真实数据+分页） | ✅ 完成 | `Views/` 目录下各文件 |

**原计划 5 个任务全部完成。**

---

## 当前阶段总结

**飞书直连阶段（第一阶段）已基本完成。**  
iOS App 核心功能均已实现，数据通过飞书 REST API 直接交互，Repository 协议层已做好抽象，后续切换真实后端时 View 层零改动。

---

## 遗留待处理项

### 1. ProfileView 统计数据硬编码

**文件：** `Views/ProfileView.swift`

当前"统计概览"中的数字（累计 156、今日 12、处理中 3）是静态硬编码。

> **优先级调整**：由于后端开发计划已确定，此项可推迟到切换 `ServerVideoRepository` 时一并实现（后端接口天然支持统计查询），无需在飞书直连阶段单独开发。

**状态：** ⏸ 暂缓，随后端切换一并实现

---

### 2. 真机测试

**状态：** 🔲 待测试

**测试清单（飞书直连阶段验收）：**

- [ ] 登录（test / 0104）→ 成功进入主界面
- [ ] 历史记录列表从飞书加载真实数据
- [ ] 滚动到底部触发分页加载
- [ ] 搜索功能（中文关键词）
- [ ] 排序切换（最新优先 / 最早优先）
- [ ] 分类筛选（视频类型）
- [ ] 点击卡片进入详情页
- [ ] 详情页字段完整显示（核心观点、金句、标签）
- [ ] 原始链接可跳转
- [ ] 提交新视频 URL → 飞书表格新增记录
- [ ] SubmitView 类型统计卡片数据正确
- [ ] 退出登录 → 重新登录（验证 UserDefaults 持久化）
- [ ] 断网状态下的错误提示

---

## 飞书配置信息

| 配置项 | 值 |
|--------|-----|
| App ID | `cli_a9c17878db38dced` |
| App Token | `ZPKVb5lDqaoRpAsBv7wccjuAnOe` |
| 默认 Table ID | `tbl339YsqSYxEygQ`（test 账号绑定） |
| 测试账号 | test / 0104 |

---

## 飞书字段映射（已实现）

| 飞书字段 | Swift 字段 | 类型 |
|----------|-----------|------|
| 标题 | title | String |
| 作者 | author | String |
| 一句话总结 | summary | String |
| 核心观点 | corePoints | [String]（按换行分割） |
| 详细内容 | correctedText | String |
| 金句 | goldenSentences | [String]（按换行分割） |
| 标签 | tags | [String]（飞书多选） |
| 视频类型 | videoType | String（单选） |
| 处理状态 | status | String（单选） |
| 原始链接 | url | String（取 .link） |
| 处理时间 | processedAt | String?（毫秒时间戳 → ISO8601） |

---

## 下一阶段：切换到 FastAPI 后端

当 `全栈后端与管理系统开发计划.md` 中的后端本地联调完成后，iOS 端只需：

1. 新建 `Services/ServerVideoRepository.swift`，实现 `VideoRepositoryProtocol`（调用 FastAPI 接口）
2. 新建 `Services/ServerAuthService.swift`，实现 `AuthServiceProtocol`（调用 `/auth/login`）
3. 修改 `Services/AppConfig.swift`：`useFeishuDirect = false`，`Server.baseURL = "http://127.0.0.1:8000"`
4. 修改 `Services/AppServices.swift`（依赖注入入口）：注入 Server 实现类

**View 层代码零改动。**

同时在此阶段一并实现 ProfileView 的动态统计数据（调用后端 `/videos/stats` 接口）。
