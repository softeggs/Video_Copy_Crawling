# 下一步任务规划（实施追踪版）

> 更新日期：2026-03-12  
> 用途：作为下一阶段开发执行清单与进度跟踪面板  
> 覆盖文件：`plans/下一步任务规划.md`

---

## 摘要

- [ ] 以 **FastAPI 后端 + MySQL + db_scheduler + React 管理后台** 作为下一阶段主线
- [ ] iOS App 保持现有主要功能不变，但登录时新增 **数据库模式 / 飞书测试模式** 选择
- [ ] 飞书测试模式继续保留 **本地测试登录（test / 0104）**
- [ ] 数据库模式接入新后端，实现独立用户体系、视频提交、历史查询、统计展示
- [ ] 本阶段验收目标：本地跑通  
  `iOS（数据库模式） → FastAPI → MySQL → db_scheduler → 回写结果`
- [ ] 同时保留  
  `iOS（飞书测试模式） → 飞书直连`  
  作为功能测试链路
- [ ] 文档在本阶段收尾时统一回写，清理与代码不一致的旧记录

---

## P0：后端基础骨架（优先开始）

### 1. 创建 `backend/` 项目骨架
- [ ] 新建 `backend/main.py`
- [ ] 新建 `backend/database.py`
- [ ] 新建 `backend/models.py`
- [ ] 新建 `backend/schemas.py`
- [ ] 新建 `backend/auth.py`
- [ ] 新建 `backend/dependencies.py`
- [ ] 新建 `backend/routers/auth.py`
- [ ] 新建 `backend/routers/videos.py`
- [ ] 新建 `backend/routers/admin.py`
- [ ] 新建 `backend/requirements.txt`
- [ ] 补充后端启动入口与本地开发说明

### 2. 建立数据库连接与基础配置
- [ ] 采用 `FastAPI + SQLAlchemy 2.x + PyMySQL + Pydantic`
- [ ] 新增 MySQL 环境变量配置项
- [ ] 实现数据库会话管理
- [ ] 实现应用启动时建表或初始化逻辑
- [ ] 补充开发环境默认配置示例（不提交敏感信息）

### 3. 设计并落地用户表 `users`
- [ ] 建立字段：`id`
- [ ] 建立字段：`username`
- [ ] 建立字段：`email`
- [ ] 建立字段：`password_hash`
- [ ] 建立字段：`display_name`
- [ ] 建立字段：`is_active`
- [ ] 建立字段：`is_admin`
- [ ] 建立字段：`created_at`
- [ ] 对 `username` 和 `email` 建唯一约束

### 4. 设计并落地视频表 `videos`
- [ ] 建立字段：`id`
- [ ] 建立字段：`user_id`
- [ ] 建立字段：`url`
- [ ] 建立字段：`title`
- [ ] 建立字段：`author`
- [ ] 建立字段：`summary`
- [ ] 建立字段：`core_points`（JSON）
- [ ] 建立字段：`golden_sentences`（JSON）
- [ ] 建立字段：`tags`（JSON）
- [ ] 建立字段：`video_type`
- [ ] 建立字段：`status`
- [ ] 建立字段：`corrected_text`（TEXT）
- [ ] 建立字段：`markdown_content`（TEXT）
- [ ] 建立字段：`error_msg`
- [ ] 建立字段：`created_at`
- [ ] 建立字段：`processed_at`
- [ ] 建立 `user_id` 外键与必要索引
- [ ] 统一状态值为：`待处理 / 处理中 / 已完成 / 失败`

---

## P1：认证与用户接口

### 5. 实现认证能力
- [ ] 实现密码哈希（`bcrypt`）
- [ ] 实现 JWT 签发
- [ ] 实现 JWT 校验
- [ ] 实现当前用户依赖注入
- [ ] 实现管理员权限依赖注入

### 6. 实现用户认证接口
- [ ] 实现 `POST /auth/register`
- [ ] 实现 `POST /auth/login`
- [ ] 实现 `GET /auth/me`
- [ ] 保持返回结构兼容 iOS 当前 `LoginResponse`
- [ ] `user` 返回中保留兼容字段 `table_id`
- [ ] 数据库模式下 `table_id` 固定返回空字符串

### 7. 认证验收
- [ ] 新用户可注册
- [ ] 正常用户可登录并获得 JWT
- [ ] 错误密码返回明确错误
- [ ] 被禁用用户不可登录
- [ ] 普通用户无法访问管理员接口

---

## P1：视频业务接口

### 8. 实现用户视频接口
- [ ] 实现 `POST /videos/submit`
- [ ] 实现 `GET /videos`
- [ ] 实现 `GET /videos/{id}`
- [ ] 实现 `GET /videos/stats`
- [ ] 实现 `GET /videos/overview`

### 9. 明确接口职责
- [ ] `/videos/submit`：写入数据库，初始状态为 `待处理`
- [ ] `/videos`：返回当前登录用户的视频分页列表
- [ ] `/videos/{id}`：返回当前登录用户的视频详情
- [ ] `/videos/stats`：只返回按视频类型聚合的数据
- [ ] `/videos/overview`：只返回 `累计 / 今日 / 待处理` 概览数据

### 10. 与 iOS 的兼容约束
- [ ] 保持列表返回结构兼容 `VideoListResponse`
- [ ] 保持详情返回结构兼容 `VideoRecord`
- [ ] 保持提交返回结构兼容 `VideoSubmitResponse`
- [ ] 新增概览统计响应结构，供 ProfileView 使用
- [ ] 数据库模式下忽略 iOS 传入的 `tableId` 语义

### 11. 视频接口验收
- [ ] 提交 URL 后数据库生成一条 `待处理` 记录
- [ ] 列表接口仅返回当前用户自己的记录
- [ ] 详情接口不可越权访问其他用户数据
- [ ] 类型统计结果可被 iOS 现有统计卡片直接使用
- [ ] 概览统计结果可驱动 ProfileView 的真实数字显示

---

## P1：调度器改造（数据库模式）

### 12. 新建数据库调度器
- [ ] 新建 `core/db_scheduler.py`
- [ ] 保留现有 `core/scheduler.py` 不动
- [ ] 新调度器轮询 MySQL 中 `status=待处理` 的记录
- [ ] 抢占任务时先更新为 `处理中`
- [ ] 调用现有 `ProcessingPipeline.process(url, skip_feishu_sync=True)`

### 13. 实现数据库写回逻辑
- [ ] 成功时回写 `title`
- [ ] 成功时回写 `author`
- [ ] 成功时回写 `summary`
- [ ] 成功时回写 `core_points`
- [ ] 成功时回写 `golden_sentences`
- [ ] 成功时回写 `tags`
- [ ] 成功时回写 `video_type`
- [ ] 成功时回写 `corrected_text`
- [ ] 成功时回写 `markdown_content`
- [ ] 成功时回写 `processed_at`
- [ ] 成功时更新状态为 `已完成`

### 14. 实现失败处理
- [ ] 失败时写入 `error_msg`
- [ ] 失败时更新状态为 `失败`
- [ ] 保证失败不会新建重复记录
- [ ] 保证异常不会导致数据库状态卡死在 `处理中`

### 15. 数据清理策略
- [ ] 实现大字段清理服务函数
- [ ] 处理完成超过 30 天的数据清空 `corrected_text`
- [ ] 处理完成超过 30 天的数据清空 `markdown_content`
- [ ] 保留 `url / title / summary / tags / video_type` 等轻量字段
- [ ] 预留每日自动清理入口
- [ ] 提供管理员手动清理接口

### 16. 调度器验收
- [ ] `待处理 → 处理中 → 已完成` 状态流转正确
- [ ] 失败记录正确进入 `失败`
- [ ] 回写内容能被 iOS 历史记录与详情页读取
- [ ] 清理动作不会删除记录本身

---

## P1：iOS 双数据源模式改造

### 17. 登录页新增数据源选择
- [ ] 在 `LoginView` 增加模式切换 UI
- [ ] 提供选项：`数据库模式`
- [ ] 提供选项：`飞书测试模式`
- [ ] 默认选中 `数据库模式`
- [ ] 选中飞书测试模式时显示 `test / 0104` 提示

### 18. 会话与模式持久化
- [ ] 新增 `DataSourceMode` 类型
- [ ] 在 `AuthManager` 中持久化当前模式
- [ ] 登录成功后同时保存 `token / user / mode`
- [ ] 退出登录时清除模式与会话
- [ ] App 重启后恢复最近一次登录模式

### 19. 服务注入改造
- [ ] 将 `AppServices` 改为按当前模式解析服务
- [ ] 数据库模式使用 `ServerAuthService`
- [ ] 数据库模式使用 `ServerVideoRepository`
- [ ] 飞书测试模式使用 `LocalMockAuthService`
- [ ] 飞书测试模式使用 `FeishuVideoRepository`
- [ ] 清理当前“Server mode is not implemented yet”阻塞点

### 20. 协议与模型兼容
- [ ] 保留 `VideoRepositoryProtocol` 现有方法
- [ ] 新增 `fetchOverviewStats(tableId:)`
- [ ] 保留当前 `User.tableId` 字段，避免本阶段大重构
- [ ] 数据库模式下允许 `tableId` 为空字符串
- [ ] 统一由 repository 内部处理模式差异

### 21. 页面接入改造
- [ ] `SubmitView` 接入数据库模式的提交与统计
- [ ] `HistoryView` 接入数据库模式的列表与详情
- [ ] `DetailView` 接入数据库模式详情展示
- [ ] `ProfileView` 改为真实概览统计
- [ ] `ProfileView` 显示当前数据源模式
- [ ] 保持两种模式下页面功能一致

### 22. iOS 验收
- [ ] 数据库模式可登录
- [ ] 飞书测试模式可登录
- [ ] 两种模式都可提交 URL
- [ ] 两种模式都可查看历史列表
- [ ] 两种模式都可进入详情页
- [ ] SubmitView 类型统计在两种模式下都正常
- [ ] ProfileView 概览统计在两种模式下都正常
- [ ] 切换模式后不会误用上一模式的数据源实例

---

## P2：管理员接口与管理后台

### 23. 管理员接口开发
- [ ] 实现 `GET /admin/users`
- [ ] 实现 `POST /admin/users`
- [ ] 实现 `PUT /admin/users/{id}`
- [ ] 实现 `GET /admin/videos/pending`
- [ ] 实现 `GET /admin/stats`
- [ ] 实现 `GET /admin/api-balance`
- [ ] 实现 `POST /admin/cleanup`

### 24. 管理后台骨架
- [ ] 新建 `admin-web/`
- [ ] 采用 `React 18 + TypeScript + Ant Design Pro`
- [ ] 完成后台登录页
- [ ] 完成 Dashboard 页面
- [ ] 完成用户管理页面
- [ ] 完成待处理队列页面
- [ ] 完成 API 余额页面
- [ ] 完成数据清理页面

### 25. 管理后台验收
- [ ] 管理员可登录后台
- [ ] Dashboard 正常显示总览指标
- [ ] 用户管理支持分页与搜索
- [ ] 用户可被启用/禁用
- [ ] 待处理队列能看到正在排队的记录
- [ ] API 余额可查询 OpenAI / Kimi / Gemini
- [ ] 手动清理可成功触发

---

## P2：联调与本地运行

### 26. 本地联调准备
- [ ] 整理后端 `.env` 配置项
- [ ] 整理 MySQL 本地初始化步骤
- [ ] 整理调度器启动步骤
- [ ] 整理 iOS 数据库模式联调说明
- [ ] 整理飞书测试模式联调说明

### 27. 端到端联调
- [ ] 跑通 `iOS（数据库模式） → FastAPI → MySQL`
- [ ] 跑通 `MySQL → db_scheduler → 回写结果`
- [ ] 跑通 `iOS 历史列表 / 详情页读取数据库结果`
- [ ] 跑通 `iOS（飞书测试模式） → 飞书直连`
- [ ] 验证两条链路可以独立工作

### 28. 部署准备
- [ ] 编写 `backend/Dockerfile`
- [ ] 编写 `docker-compose.yml`
- [ ] 覆盖 `FastAPI + MySQL` 的本地容器化启动
- [ ] 明确管理后台是否纳入 compose
- [ ] 补充容器化启动文档

---

## P2：测试清单

### 29. 后端测试
- [ ] 注册成功测试
- [ ] 登录成功测试
- [ ] 错误密码测试
- [ ] 禁用用户登录失败测试
- [ ] 视频提交测试
- [ ] 视频列表分页测试
- [ ] 视频详情权限测试
- [ ] 视频类型统计测试
- [ ] 视频概览统计测试
- [ ] 管理员接口权限测试
- [ ] 清理接口测试

### 30. 调度器测试
- [ ] 单条任务成功处理测试
- [ ] 单条任务失败回写测试
- [ ] 并发轮询不重复消费测试
- [ ] 回写字段完整性测试
- [ ] 自动清理安全性测试

### 31. iOS 测试
- [ ] 数据库模式登录测试
- [ ] 飞书测试模式登录测试
- [ ] 提交 URL 测试
- [ ] 历史记录分页加载测试
- [ ] 搜索与排序测试
- [ ] 详情页展示完整性测试
- [ ] SubmitView 类型统计测试
- [ ] ProfileView 概览统计测试
- [ ] 退出登录与恢复会话测试
- [ ] 模式切换后实例隔离测试

---

## P3：文档与收尾

### 32. 计划文档同步
- [ ] 更新 `plans/项目总览与进度.md`
- [ ] 更新 `plans/iOS_App开发计划.md`
- [ ] 更新 `plans/全栈后端与管理系统开发计划.md`
- [ ] 更新 `plans/已知问题与修复记录.md`

### 33. 清理过期记录
- [ ] 修正文档中“日志轮转未修复”的过期描述
- [ ] 标记当前真实未完成项
- [ ] 将已完成项从“待办”转为“已完成”
- [ ] 保持各计划文档之间状态一致

### 34. README 收尾
- [ ] 补充后端启动方式
- [ ] 补充 MySQL 配置说明
- [ ] 补充数据库模式 / 飞书测试模式说明
- [ ] 补充本地联调说明
- [ ] 补充管理后台入口说明

---

## 重要接口与类型约束

- [ ] 后端公开接口固定为：
  - [ ] `POST /auth/register`
  - [ ] `POST /auth/login`
  - [ ] `GET /auth/me`
  - [ ] `POST /videos/submit`
  - [ ] `GET /videos`
  - [ ] `GET /videos/{id}`
  - [ ] `GET /videos/stats`
  - [ ] `GET /videos/overview`
- [ ] 管理接口固定为：
  - [ ] `GET /admin/users`
  - [ ] `POST /admin/users`
  - [ ] `PUT /admin/users/{id}`
  - [ ] `GET /admin/videos/pending`
  - [ ] `GET /admin/stats`
  - [ ] `GET /admin/api-balance`
  - [ ] `POST /admin/cleanup`
- [ ] iOS 新增类型：`DataSourceMode`
- [ ] iOS 新增类型：`VideoOverviewStats`
- [ ] iOS 协议新增方法：`fetchOverviewStats(tableId:)`
- [ ] 旧 `APIService.swift` 不作为本阶段兼容目标

---

## 默认约束与假设

- [ ] 数据库使用 `MySQL 8.x`
- [ ] 后端首版使用同步 SQLAlchemy，会话模型优先简单可维护
- [ ] 列表型字段使用 JSON 列，长文本使用 TEXT
- [ ] 飞书测试模式仅用于功能测试，不纳入普通用户正式链路
- [ ] 普通用户正式使用数据库模式
- [ ] 管理后台与普通用户后端共用同一套登录体系
- [ ] 管理员权限由 `is_admin` 控制
- [ ] 本阶段不兼容旧草稿中的 `/api/*` 与 `/auth/token` 风格接口

---

## 阶段完成标准

### 里程碑 A：后端可用
- [ ] 注册、登录、提交、列表、详情、统计全部可用
- [ ] MySQL 建表与本地启动稳定

### 里程碑 B：处理链路可用
- [ ] db_scheduler 能从数据库消费任务并写回结果
- [ ] 失败状态与错误信息可见

### 里程碑 C：iOS 双模式可用
- [ ] 登录时可选择数据库模式 / 飞书测试模式
- [ ] 两种模式下核心页面都可正常使用

### 里程碑 D：管理后台可用
- [ ] 管理员可查看总览、用户、待处理队列、API 余额、清理入口

### 里程碑 E：文档完成
- [ ] 计划文档、README、问题记录与当前代码状态一致

