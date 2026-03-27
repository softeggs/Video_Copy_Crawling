# iOS App

## 模块定位

移动端用户入口，通过统一后端 8002 提供完整视频记录管理能力。

## 当前状态

已运行

## 已完成

- P2：最小联调完成（登录、提交、列表、详情、统计、概览接入统一后端）
- **P5**：产品能力补齐全部完成
  - `VideoRecord` 新增 `isFavorited`、`processingStage`、`processingDetail`、`estimatedSecondsRemaining`、`lastStageUpdateAt` 字段
  - `APIService` 新增 `deleteVideo`、`toggleFavorite`、`fetchVideoStatus` 接口
  - `APIService` 新增 `listShortcutKeys`、`createShortcutKey`、`revokeShortcutKey`、`shortcutSubmit` 接口
  - `VideoRepositoryProtocol` 新增全部 P3 方法声明
  - `BackendVideoRepository` 实现全部 P3 方法
  - `FeishuVideoRepository` 添加 P3 stubs，抛 `notSupported` 明确错误
  - `AuthServiceError` 新增 `notSupported` case
  - `HistoryView` 左滑删除（乐观更新 + 失败回滚）、星标收藏（乐观更新）、处理中状态（阶段标签 + 进度指示器）
  - `ProfileView` 新增"快捷指令密钥"入口
  - `ShortcutKeysView` 密钥列表、生成、复制、吊销完整实现

## 未完成

- 真机局域网联调验证（待进入 P6）
- `/auth/me` 会话校验（启动时自动校验 token）

## 技术细节

### P3 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `isFavorited` | Bool | 是否收藏 |
| `processingStage` | String | 当前处理阶段 key（如 `queued`, `downloading`） |
| `processingDetail` | String | 阶段具体描述 |
| `estimatedSecondsRemaining` | Int? | 预计剩余秒数 |
| `lastStageUpdateAt` | String? | 阶段更新时间 |

### 乐观更新策略

- **删除**：立即从列表移除，失败则恢复
- **收藏**：立即更新状态，失败则恢复
- 两者均通过 `withAnimation` 驱动 UI 平滑过渡

## 下一步任务

- P6：真机联调验证
- P6：越权/伪造密钥安全验证
- P7：服务器迁移

## 最后更新

2026-03-27
