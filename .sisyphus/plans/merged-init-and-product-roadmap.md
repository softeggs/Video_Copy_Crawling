# 仓库统一执行计划（整合 init 守卫规则与业务主线）

## 摘要
> **概述**：将 `.sisyphus/plans/init-deep.md` 的有效守卫规则吸收到新的业务实施主线中，基于当前活代码重写 `plans/PLAN.md` 的过期路线图，形成一份可直接执行的单一计划。
> **交付物**：
> - 基于现有 `backend/` 的后端契约稳定化与本地运行基线
> - 基于现有 `core/` 的 `db_scheduler` 数据库消费与回写链路
> - 基于现有 iOS 工程的双数据源模式改造（数据库模式 / 飞书测试模式）
> - API 级管理员能力、端到端联调矩阵、文档/计划回写
> **工作量**：XL
> **可并行**：YES - 4 个执行波次
> **关键路径**：1 → 2 → 3/4/5 → 6/7/8 → 9/10 → 11/12/13 → 14 → 15

## 背景
### 原始请求
- 将之前 init 的计划与 `D:\code\Video_Copy_Crawling\plans\PLAN.md` 的 plan 整合，输出新的计划。
- 若存在疑问，需要及时沟通。

### 访谈与调研结论
- `plans/PLAN.md:24-37` 已明显过期：文件把 `backend/main.py`、`database.py`、`models.py`、`schemas.py`、`routers/*` 视为“待创建”，但这些文件都已存在于当前仓库。
- `.sisyphus/plans/init-deep.md:21-31` 的核心价值不在于继续执行 AGENTS 生成，而在于其排除规则、活代码优先、证据化验证、文档防漂移守卫。
- 当前仓库的真实主线是：`backend/` FastAPI 服务、`core/` 处理流水线、`ios_app/iOS_Video_Intelligence/` iOS 客户端、`test/` 脚本式 smoke/integration 检查。
- 当前仓库无项目级 CI 或正式测试框架配置；`test/` 更偏手工脚本集合，不能假设已具备完整自动化回归体系。
- 用户已确认：`init-deep` 只吸收为守卫规则；验证策略采用“实现后测试 + 联调/smoke 验证”。

### Metis / Oracle 复核（已吸收）
- 以活代码为唯一事实源；README 与旧计划仅作参考，不得压过现状代码。
- 后端 API 作为下一阶段 canonical contract；iOS 需对齐后端现有 `/auth/*`、`/videos*` 风格，而不是反向保留旧 `APIService.swift` 的 `/api/*` 路径。
- `admin-web/` 当前不存在，默认降级为 Deferred，不阻塞主链路验收。
- `app.py` / Streamlit 界面不纳入本阶段主线实现，只在文档中标记与新后端并行存在。
- 所有验证都必须零人工、可复跑，并将证据保存到 `.sisyphus/evidence/task-{N}-{slug}.{ext}`。

## 工作目标
### 核心目标
在不新增无效“脚手架创建”工作的前提下，基于现有后端、核心流水线与 iOS 工程，打通两条明确链路：
1. `iOS（数据库模式） → FastAPI → MySQL → db_scheduler → 回写结果`
2. `iOS（飞书测试模式） → 飞书直连`

### 交付物
- 一份基于活代码的统一执行计划，替代旧的过期“下一步任务规划”。
- 稳定的后端认证、视频、管理员 API 契约与本地运行基线。
- 与现有 `ProcessingPipeline.process(..., skip_feishu_sync=True)` 对接的数据库调度器方案。
- iOS 双模式登录、会话持久化、Repository 注入、页面接入与概览统计。
- 本地端到端联调矩阵、容器化启动方案、README 与 `plans/*` 的状态回写。

### 完成定义（可验证）
- `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001` 启动后，`curl http://127.0.0.1:8001/health` 返回 `{"status":"ok"}`。
- 使用固定测试用户 `plan_test_user / PlanPass123!`，`POST /auth/register`、`POST /auth/login`、`GET /auth/me` 全部通过；禁用用户与非管理员访问被正确拒绝。
- `POST /videos/submit` 成功写入 `status="待处理"`；`GET /videos`、`GET /videos/{id}`、`GET /videos/stats`、`GET /videos/overview` 的返回结构与 iOS 模型一致。
- `core/db_scheduler.py` 能把数据库中的 `待处理` 记录推进到 `处理中 / 已完成 / 失败`，并正确回写 `summary`、`core_points`、`golden_sentences`、`tags`、`video_type`、`corrected_text`、`markdown_content`、`processed_at`、`error_msg`。
- iOS `xcodebuild test -project "ios_app/iOS_Video_Intelligence/iOS_Video_Intelligence.xcodeproj" -scheme "iOS_Video_Intelligence" -destination "generic/platform=iOS Simulator"` 通过；数据库模式与飞书测试模式均可登录、提交、查看历史、进入详情与查看统计。
- `README.md` 与 `plans/*` 不再声称“待创建 backend 骨架”，且明确记录：admin-web deferred、Streamlit 非本阶段主线、`init-deep` 守卫规则已吸收。

### 必须具备
- 明确排除 `.tmp_research/`、`downloads/`、`outputs/`、`logs/`、`.vscode/`、`test/xdg_*`、`test/openclaw-workspace/`、`.env`、`cookies*.txt`。
- 先冻结契约，再做实现；后端/调度器/iOS 不允许各自演化一套接口语义。
- 所有任务都必须同时包含实现要求与测试/验证要求。
- 所有验收使用固定样例数据：
  - 用户名：`plan_test_user`
  - 邮箱：`plan_test@example.com`
  - 密码：`PlanPass123!`
  - 示例 URL：`https://www.example.com/video/demo`

### 严禁出现
- 把 AGENTS 生成继续当作主线实施任务。
- 把 `plans/PLAN.md` 中的“创建 backend 文件”照搬进新计划。
- 把 `APIService.swift` 旧 `/api/*` 路由当作下一阶段真源。
- 把 `admin-web/` 当成已存在目录或把它设成主链路阻塞项。
- 在证据、文档、示例中复制 `AppConfig.swift` 内的密钥值、`.env` 值或 `cookies*.txt` 内容。

## 验证策略
> **零人工介入**：所有验证必须可由 agent 直接执行。
- 测试决策：实现后测试 + smoke/integration 验证；不假设仓库已有正式 pytest/CI 基建。
- QA 政策：每个任务必须包含 happy path 与 failure/edge case 两类场景。
- 证据规范：统一落到 `.sisyphus/evidence/task-{N}-{slug}.{ext}`。
- 后端验证优先使用 `curl` + Python 脚本 + 本地 MySQL / docker compose。
- iOS 验证优先使用 `xcodebuild test`；若页面联调需 UI 校验，则以单元/集成测试覆盖逻辑，避免依赖人工点击。

## 执行策略
### 并行执行波次
> 每波目标 5 个左右任务；共享依赖优先前置，以便后续最大化并行。

Wave 1：活代码事实基线、契约冻结、本地验证基线、调度器状态机、iOS 双模式架构冻结。

Wave 2：后端鉴权与视频 API 稳定化、管理员 API、数据库调度器、容器化/本地启动入口。

Wave 3：iOS 模式持久化、服务注入、页面接入、端到端联调、文档与计划回写。

Wave 4：最终四路并发审查与收口。

### 依赖矩阵（全量）
- 1 阻塞 2、3、4、5、15
- 2 阻塞 6、7、8、11、12、13、14、15
- 3 阻塞 6、7、8、9、10、14
- 4 阻塞 9、14
- 5 阻塞 11、12、13、14
- 6 阻塞 8、11、12、14
- 7 阻塞 9、11、12、13、14
- 8 阻塞 14、15
- 9 阻塞 14、15
- 10 阻塞 14、15
- 11 阻塞 12、13、14
- 12 阻塞 13、14
- 13 阻塞 14、15
- 14 阻塞 15

### Agent 派发摘要
- Wave 1 → 5 个任务 → deep / unspecified-high / writing / quick
- Wave 2 → 5 个任务 → deep / unspecified-high / quick
- Wave 3 → 5 个任务 → deep / unspecified-high / quick / writing
- Wave 4 → 4 个审查任务 → oracle / deep / unspecified-high

## TODOs
> 实现 + 测试 = 同一个任务；不得拆开。
> 每个任务都必须给执行代理足够的上下文，不能依赖本次对话记忆。

- [ ] 1. 建立活代码事实基线与全局排除清单

  **要做什么**：先把新计划的事实源固定下来：哪些目录算主线代码、哪些目录必须排除、哪些旧文档只能作为参考。输出一份“活代码事实表”，明确 `backend/`、`core/`、`ios_app/iOS_Video_Intelligence/`、`test/`、`README.md`、`plans/PLAN.md`、`.sisyphus/plans/init-deep.md` 在后续实施中的角色。
  **禁止事项**：不要把 `.tmp_research/`、`downloads/`、`outputs/`、`logs/`、`.vscode/`、`test/xdg_*`、`test/openclaw-workspace/`、`.env`、`cookies*.txt` 纳入实施范围或证据内容。

  **推荐 Agent Profile**：
  - Category: `deep` — 原因：需要做仓库级事实源冻结与旧计划去伪存真
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: NO | Wave 1 | Blocks: 2, 3, 4, 5, 15 | Blocked By: none

  **参考资料**：
  - 活代码：`backend/main.py:7-22` — 证明后端骨架已存在，不应再规划“创建 backend 文件”
  - 活代码：`backend/database.py:7-30` — 证明数据库 URL、engine、SessionLocal 已落地
  - 活代码：`ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-30` — 证明 iOS 已有双数据源雏形，但 server mode 未实现
  - 旧计划：`plans/PLAN.md:11-20` — 业务主线目标仍有效，应保留
  - 旧计划：`plans/PLAN.md:24-37` — backend 骨架条目已过期，必须改写而不是继承
  - 守卫规则：`.sisyphus/plans/init-deep.md:21-31` — 活代码优先、无 CI、test 噪音目录等结论可继承
  - 排除规则：`.gitignore:14-35` — `downloads/`、`outputs/`、`logs/`、`test/*` 都提示这些目录不能直接当成权威源码集

  **验收标准**：
  - [ ] 生成 `.sisyphus/evidence/task-1-live-truth.md`，列出主线代码目录、参考文档、排除目录、敏感文件与陈旧文档告警。
  - [ ] 证据中明确声明：`plans/PLAN.md` 的 backend 骨架条目失效，`init-deep` 只作为守卫规则来源。
  - [ ] 证据中不得出现任何敏感值原文，只能出现路径与风险分类。

  **QA 场景**：
  ```
  Scenario: Happy path 活代码事实冻结
    Tool: Bash
    Steps: 扫描 `backend/`、`core/`、`ios_app/iOS_Video_Intelligence/`、`test/`、`plans/PLAN.md`、`.sisyphus/plans/init-deep.md`；生成 `.sisyphus/evidence/task-1-live-truth.md`。
    Expected: 证据明确区分“活代码真源 / 仅参考文档 / 必须排除目录 / 敏感文件”，并把 `plans/PLAN.md:24-37` 标记为过期段落。
    Evidence: .sisyphus/evidence/task-1-live-truth.md

  Scenario: Failure/edge case 噪音目录污染
    Tool: Bash
    Steps: 校验事实表是否错误包含 `.tmp_research/`、`downloads/`、`outputs/`、`logs/`、`.env`、`cookies*.txt` 作为实施对象。
    Expected: 一旦任一噪音/敏感路径被纳入主线事实集，验证立即失败并输出 offending path。
    Evidence: .sisyphus/evidence/task-1-live-truth-error.txt
  ```

  **Commit**：NO | Message: `docs(plan): freeze live repo truth and exclusions` | Files: `.sisyphus/evidence/task-1-live-truth.md`

- [ ] 2. 冻结后端 canonical API 契约、状态枚举与 iOS 对齐策略

  **要做什么**：把下一阶段唯一允许实现的接口契约冻结成文档：认证接口、视频接口、管理员接口、统一状态值、字段命名、iOS 对应模型。明确“后端是契约真源，iOS 适配后端”，并修复 `videos` 路由中静态路由落在动态 `/{video_id}` 之后的风险。
  **禁止事项**：不要同时维护两套路径风格；不要继续沿用 `APIService.swift` 的 `/api/auth/token` 与 `/api/videos/list` 作为实施目标；不要遗漏 `overview` 对 `ProfileView` 的支撑。

  **推荐 Agent Profile**：
  - Category: `deep` — 原因：这是整个计划的核心决策面，后续所有实现都依赖它
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: NO | Wave 1 | Blocks: 6, 7, 8, 11, 12, 13, 14, 15 | Blocked By: 1

  **参考资料**：
  - 后端真源：`backend/routers/auth.py:22-56` — 现有认证路径为 `/auth/register`、`/auth/login`、`/auth/me`
  - 后端真源：`backend/routers/videos.py:43-137` — 现有视频路径为 `/videos/submit`、`/videos`、`/videos/{id}`、`/videos/stats`、`/videos/overview`
  - 风险点：`backend/routers/videos.py:97-137` — 动态路由 `/{video_id}` 先于 `/stats`、`/overview`，需在实施时先调整顺序
  - 后端模型：`backend/schemas.py:30-87` — 登录、提交、列表、详情、统计、概览的 Pydantic 契约
  - 数据模型：`backend/models.py:24-44` — `videos` 表字段与状态值基线
  - 旧 iOS 预期：`ios_app/iOS_Video_Intelligence/Services/APIService.swift:18-20`、`44-46`、`65-67` — 仍在请求 `/api/*` 路径，必须废止为参考实现
  - iOS 模型：`ios_app/iOS_Video_Intelligence/Models/VideoRecord.swift:49-109` — `User`、`LoginResponse`、`VideoListResponse`、`TypeStat`
  - iOS 统计页诉求：`ios_app/iOS_Video_Intelligence/Views/ProfileView.swift:27-68` — 需要真实概览统计，而不是硬编码数字

  **验收标准**：
  - [ ] 生成 `.sisyphus/evidence/task-2-api-contract.md`，逐条冻结 endpoint、method、请求体、响应体、状态码、状态枚举、iOS 对应模型。
  - [ ] 契约文档中明确写明：canonical path 采用 `/auth/*`、`/videos*`、`/admin/*`；iOS 旧 `/api/*` 仅作历史遗留。
  - [ ] 契约文档中明确列出 `待处理 / 处理中 / 已完成 / 失败` 的语义与页面使用场景。

  **QA 场景**：
  ```
  Scenario: Happy path 契约冻结
    Tool: Bash
    Steps: 读取后端 router/schema 与 iOS model/service；生成 `.sisyphus/evidence/task-2-api-contract.md`；列出所有 endpoint 映射与状态值。
    Expected: 契约文档只保留一套 canonical API，且包含 `ProfileView` 所需的 `overview` 响应结构。
    Evidence: .sisyphus/evidence/task-2-api-contract.md

  Scenario: Failure/edge case 双真源漂移
    Tool: Bash
    Steps: 校验契约文档中是否同时把 `/api/*` 与 `/auth/*`/`/videos*` 视为当前真源，或遗漏 `/videos/overview`。
    Expected: 若存在双真源、遗漏 endpoint、或未标记动态路由顺序风险，则验证失败。
    Evidence: .sisyphus/evidence/task-2-api-contract-error.txt
  ```

  **Commit**：NO | Message: `docs(plan): freeze canonical backend contract` | Files: `.sisyphus/evidence/task-2-api-contract.md`

- [ ] 3. 建立本地 MySQL 验证基线、样例数据与启动约定

  **要做什么**：在正式改动业务逻辑前，先把本地验证基线固定下来：数据库连接方式、最小化 docker compose / 启动命令、样例测试用户、端口、环境变量、服务启动顺序、数据清理/重置方式。所有后续后端与调度器验收都必须复用这套基线。
  **禁止事项**：不要依赖开发者本地已有数据库的隐式状态；不要把真实 `.env` 或 `AppConfig.swift` 中的密钥写进示例；不要把 README 中不存在的 `requirements.txt` 当作安装真源。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：需要搭出可复跑的运行基线，支撑后续所有验证
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 1 | Blocks: 6, 7, 8, 9, 10, 14 | Blocked By: 1

  **参考资料**：
  - 数据库配置：`backend/database.py:7-28` — 当前支持 `DATABASE_URL` 或 `MYSQL_*` 环境变量
  - 服务启动：`backend/main.py:10-22` — 启动时自动建表，提供 `/health`
  - 依赖清单：`backend/requirements.txt:1-8` — 当前后端依赖真源
  - README 偏差：`README.md:27-56` 与 `README.md:107-124` — 文档仍指向根级 `requirements.txt` 和老项目结构，不能直接照搬
  - 守卫规则：`.sisyphus/plans/init-deep.md:67-71` — 无 CI 情况下必须依赖可复跑证据

  **验收标准**：
  - [ ] 生成 `.sisyphus/evidence/task-3-local-baseline.md`，定义端口 `8001`、测试用户、数据库名、启动顺序、重置方式与不含敏感值的 env 示例。
  - [ ] 基线中包含最小启动命令集合：MySQL 启动、后端启动、健康检查、测试用户初始化。
  - [ ] 后续任务可以直接引用该基线，无需再次发明新的样例用户或端口。

  **QA 场景**：
  ```
  Scenario: Happy path 本地验证基线落地
    Tool: Bash
    Steps: 基于 `backend/database.py`、`backend/main.py`、`backend/requirements.txt` 生成 `.sisyphus/evidence/task-3-local-baseline.md`，写明端口、环境变量、docker compose / python 启动约定、测试用户与数据清理命令。
    Expected: 证据可直接复用到后续所有 API 与调度器验收，不包含真实密钥值。
    Evidence: .sisyphus/evidence/task-3-local-baseline.md

  Scenario: Failure/edge case 隐式环境依赖
    Tool: Bash
    Steps: 校验基线是否引用真实 `.env`、硬编码 App Secret、或要求人工猜测数据库名/端口。
    Expected: 只要存在隐式环境依赖或敏感信息泄露，验证立即失败。
    Evidence: .sisyphus/evidence/task-3-local-baseline-error.txt
  ```

  **Commit**：NO | Message: `docs(plan): define local mysql validation baseline` | Files: `.sisyphus/evidence/task-3-local-baseline.md`

- [ ] 4. 冻结 db_scheduler 状态机、字段映射、幂等与失败恢复规则

  **要做什么**：在写 `core/db_scheduler.py` 之前，先把数据库调度器的行为契约冻结：如何从 `videos` 表抢占 `待处理` 任务、何时转成 `处理中`、如何调用 `ProcessingPipeline.process(url, skip_feishu_sync=True)`、如何把 `processed_content` 映射回数据库字段、失败时如何写 `error_msg`、如何避免重复消费、如何恢复卡死在 `处理中` 的记录。
  **禁止事项**：不要重写或替换现有 `core/scheduler.py`；不要直接把飞书调度器逻辑生搬到数据库表；不要让 QA 依赖外部视频平台、AI 服务和真实飞书环境才能验证。

  **推荐 Agent Profile**：
  - Category: `deep` — 原因：需要同时冻结状态机、回写映射与可验证的失败路径
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 1 | Blocks: 9, 14 | Blocked By: 1

  **参考资料**：
  - 处理入口：`core/pipeline.py:39-147` — `process(..., skip_feishu_sync=True)` 的返回结构与错误返回方式
  - Markdown 输出：`core/pipeline.py:94-139` — `markdown_path` 与 `processed_content` 来源
  - 飞书调度器现状：`core/scheduler.py:168-215` — 当前失败写回与状态推进方式
  - 飞书详情回写：`core/scheduler.py:217-269` — 可借鉴字段映射，但目标介质应改为 `videos` 表
  - 数据模型：`backend/models.py:24-44` — `videos` 表现有字段就是数据库回写目标
  - 旧计划目标：`plans/PLAN.md:139-177` — `db_scheduler`、失败处理、清理策略的业务意图仍有效

  **验收标准**：
  - [ ] 生成 `.sisyphus/evidence/task-4-db-scheduler-contract.md`，明确状态机、字段映射、幂等策略、失败恢复与清理策略。
  - [ ] 契约中明确要求：调度器验证必须支持可控假数据/桩结果，不依赖真实外部平台即可覆盖成功与失败路径。
  - [ ] 契约中明确写明：现有 `core/scheduler.py` 保持不动，`core/db_scheduler.py` 作为独立实现面。

  **QA 场景**：
  ```
  Scenario: Happy path 调度契约冻结
    Tool: Bash
    Steps: 读取 `core/pipeline.py`、`core/scheduler.py`、`backend/models.py` 与旧计划调度段落；输出 `.sisyphus/evidence/task-4-db-scheduler-contract.md`。
    Expected: 契约文档完整覆盖状态流转、回写字段、失败处理、幂等与清理，并明确需要桩化验证路径。
    Evidence: .sisyphus/evidence/task-4-db-scheduler-contract.md

  Scenario: Failure/edge case 外部依赖绑死
    Tool: Bash
    Steps: 校验调度契约是否仍要求真实飞书 / 真实视频平台 / 真实 AI key 才能验证成功与失败路径。
    Expected: 若无法在本地通过可控桩结果验证调度行为，则判定契约不完整并失败。
    Evidence: .sisyphus/evidence/task-4-db-scheduler-contract-error.txt
  ```

  **Commit**：NO | Message: `docs(plan): freeze db scheduler contract` | Files: `.sisyphus/evidence/task-4-db-scheduler-contract.md`

- [ ] 5. 冻结 iOS 双模式架构、会话持久化方案与 Deferred 范围

  **要做什么**：在动 iOS 代码前，先把客户端架构冻结：新增 `DataSourceMode`，由 `AuthManager` 同时持久化 `token / user / mode`，`AppServices` 不再用静态 `fatalError` 分支，而是按模式解析 `AuthServiceProtocol` 与 `VideoRepositoryProtocol`。同时显式冻结本阶段范围：`admin-web/` deferred、`app.py`/Streamlit 非主线、飞书测试模式继续保留 `test / 0104`。
  **禁止事项**：不要在未冻结模式边界前直接改多个页面；不要删除 `User.tableId`；不要把数据库模式与飞书测试模式混成同一套 repository 逻辑分支；不要把 admin-web 偷偷恢复为主线任务。

  **推荐 Agent Profile**：
  - Category: `deep` — 原因：需要在 iOS 客户端层先冻结架构，再分发后续实现任务
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 1 | Blocks: 11, 12, 13, 14 | Blocked By: 1

  **参考资料**：
  - 模式现状：`ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-30` — 当前默认直连飞书，server mode 直接 `fatalError`
  - 会话现状：`ios_app/iOS_Video_Intelligence/Services/AuthManager.swift:4-64` — 当前只持久化 `token` 与 `user`
  - 本地测试登录：`ios_app/iOS_Video_Intelligence/Services/AuthService.swift:42-60` — `test / 0104` 已存在，应该保留在飞书测试模式
  - 登录页现状：`ios_app/iOS_Video_Intelligence/Views/LoginView.swift:37-111` — 当前仅有用户名/密码，没有模式切换
  - 页面调用现状：`ios_app/iOS_Video_Intelligence/Views/SubmitView.swift:12-13`、`HistoryView.swift:22-23` — 页面直接拿 `AppServices.videoRepository`
  - 旧计划目标：`plans/PLAN.md:181-228` — 双模式、模式持久化、服务注入、页面接入是有效业务目标

  **验收标准**：
  - [ ] 生成 `.sisyphus/evidence/task-5-ios-architecture.md`，固定 `DataSourceMode`、会话持久化字段、服务解析策略、页面注入方式与 deferred 范围。
  - [ ] 文档中明确写明：`User.tableId` 暂时保留，数据库模式下允许为空字符串；admin-web deferred；Streamlit 仅文档标记不改造。
  - [ ] 文档中明确写明：飞书测试模式继续使用 `LocalMockAuthService`，数据库模式新增 `ServerAuthService` / `ServerVideoRepository`。

  **QA 场景**：
  ```
  Scenario: Happy path iOS 双模式架构冻结
    Tool: Bash
    Steps: 读取 `AppConfig.swift`、`AuthManager.swift`、`AuthService.swift`、`LoginView.swift` 与旧计划相关段落，生成 `.sisyphus/evidence/task-5-ios-architecture.md`。
    Expected: 文档明确模式枚举、持久化字段、服务注入方式、`tableId` 兼容策略与 deferred 范围。
    Evidence: .sisyphus/evidence/task-5-ios-architecture.md

  Scenario: Failure/edge case 范围蔓延
    Tool: Bash
    Steps: 校验架构文档是否把 `admin-web/` 重新拉入主线，或删除 `tableId`、或保留 `fatalError("Server mode is not implemented yet.")` 作为可接受状态。
    Expected: 任一情况出现即验证失败。
    Evidence: .sisyphus/evidence/task-5-ios-architecture-error.txt
  ```

  **Commit**：NO | Message: `docs(plan): freeze ios dual-mode architecture` | Files: `.sisyphus/evidence/task-5-ios-architecture.md`

- [ ] 6. 对齐后端认证、用户模型与权限依赖

  **要做什么**：基于现有 `backend/` 补齐并稳定化认证主线：注册、登录、当前用户、禁用用户拦截、管理员依赖、固定测试用户初始化与错误码。保留现有响应结构与 iOS 模型兼容，但把行为补全到可联调状态。
  **禁止事项**：不要改成旧 `OAuth2PasswordRequestForm` 风格；不要把数据库模式下的 `table_id` 变回必填；不要返回与 `UserResponse`/`LoginResponse` 不一致的字段名；不要让禁用用户仍拿到 token。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：已有骨架可复用，重点是稳定化与补齐测试
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 2 | Blocks: 8, 11, 12, 14 | Blocked By: 2, 3

  **参考资料**：
  - 鉴权实现：`backend/auth.py:8-33` — bcrypt / JWT 已存在
  - 依赖注入：`backend/dependencies.py:12-39` — `get_current_user`、`get_admin_user` 已存在
  - 路由实现：`backend/routers/auth.py:22-56` — 注册、登录、me 已存在但需补齐验证与 smoke
  - 数据模型：`backend/models.py:9-21` — `users` 表字段基线
  - Schema：`backend/schemas.py:6-37` — `UserRegisterRequest`、`UserLoginRequest`、`UserResponse`、`LoginResponse`
  - iOS 用户模型：`ios_app/iOS_Video_Intelligence/Models/VideoRecord.swift:49-71` — `user_id`、`display_name`、`table_id` 的兼容要求

  **验收标准**：
  - [ ] 运行后端并注册 `plan_test_user / plan_test@example.com / PlanPass123!`，`POST /auth/register` 返回 200，JSON 包含 `token` 与 `user.table_id=""`。
  - [ ] 使用正确密码调用 `POST /auth/login` 返回 200；错误密码返回 401；禁用用户返回 403。
  - [ ] 使用登录 token 调用 `GET /auth/me` 返回 200，字段与 `UserResponse` 完全一致。

  **QA 场景**：
  ```
  Scenario: Happy path 认证主线
    Tool: Bash
    Steps: 按 Task 3 基线启动 MySQL 与后端；调用 `POST /auth/register` 注册 `plan_test_user`；调用 `POST /auth/login` 获取 token；调用 `GET /auth/me`。
    Expected: register/login/me 全部成功，`table_id` 为空字符串，返回字段名与 iOS `LoginResponse` / `User` 解码一致。
    Evidence: .sisyphus/evidence/task-6-auth-happy.json

  Scenario: Failure/edge case 鉴权拒绝
    Tool: Bash
    Steps: 用错误密码登录一次；再把测试用户置为 `is_active=false` 后重新登录；最后用普通用户 token 调用 `/admin/users`。
    Expected: 错误密码返回 401，禁用用户返回 403，非管理员调用 `/admin/users` 返回 403。
    Evidence: .sisyphus/evidence/task-6-auth-error.json
  ```

  **Commit**：NO | Message: `feat(backend): stabilize auth and user contract` | Files: `backend/auth.py`, `backend/dependencies.py`, `backend/routers/auth.py`, `backend/schemas.py`, `backend/models.py`

- [ ] 7. 对齐后端视频接口、统计接口与动态路由顺序

  **要做什么**：基于 frozen contract 稳定化 `/videos` 体系：提交、列表、详情、类型统计、概览统计，并先修正静态路由 `/stats`、`/overview` 必须先于 `/{video_id}` 的顺序问题。补齐越权、分页、状态筛选与概览统计的 smoke 覆盖。
  **禁止事项**：不要继续保留旧 `/api/videos/list`；不要让 `/videos/stats` 或 `/videos/overview` 被动态路由吞掉；不要返回与 iOS `VideoListResponse` / `VideoRecord` 不兼容的字段名；不要让用户看到他人的视频记录。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：已有接口雏形，重点是纠正行为和兼容性
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 2 | Blocks: 9, 11, 12, 13, 14 | Blocked By: 2, 3

  **参考资料**：
  - 当前路由：`backend/routers/videos.py:43-137` — 已有 submit/list/detail/stats/overview 实现
  - 顺序风险：`backend/routers/videos.py:97-137` — `/{video_id}` 当前位于 `/stats`、`/overview` 之前
  - 数据模型：`backend/models.py:24-44` — `Video` 字段即接口返回基线
  - Schema：`backend/schemas.py:40-87` — 提交、详情、列表、统计、概览的字段定义
  - iOS 模型：`ios_app/iOS_Video_Intelligence/Models/VideoRecord.swift:3-47`、`73-109` — 详情、提交、列表、类型统计的客户端解码结构
  - 提交页依赖：`ios_app/iOS_Video_Intelligence/Views/SubmitView.swift:89-205` — 需要 submit + type stats
  - 历史页依赖：`ios_app/iOS_Video_Intelligence/Views/HistoryView.swift:144-220` — 需要分页、详情、日期与状态一致性
  - 我的页依赖：`ios_app/iOS_Video_Intelligence/Views/ProfileView.swift:27-68` — 需要 overview 真数据

  **验收标准**：
  - [ ] `POST /videos/submit` 使用登录 token 提交 `https://www.example.com/video/demo` 返回 200，`record_id` 存在且 `status="待处理"`。
  - [ ] `GET /videos?page=1&page_size=20` 仅返回当前用户记录，字段可被 iOS `VideoListResponse` 直接解码。
  - [ ] `GET /videos/stats` 与 `GET /videos/overview` 能被正确命中，不会被 `/{video_id}` 拦截；跨用户访问 `GET /videos/{id}` 返回 404。

  **QA 场景**：
  ```
  Scenario: Happy path 视频接口主线
    Tool: Bash
    Steps: 登录获取 token；提交 `https://www.example.com/video/demo`；依次调用 `/videos`、`/videos/stats`、`/videos/overview`；记录返回。
    Expected: submit 返回 `status=待处理`；列表仅含当前用户记录；stats 返回数组；overview 返回 `total/today/pending` 三字段。
    Evidence: .sisyphus/evidence/task-7-videos-happy.json

  Scenario: Failure/edge case 路由与越权
    Tool: Bash
    Steps: 先请求 `/videos/stats` 与 `/videos/overview`，确认不是 422/404；再用另一个用户 token 请求不属于自己的 `/videos/{id}`。
    Expected: 静态统计路由命中成功；跨用户详情返回 404；若 `/stats` 或 `/overview` 被动态路由吞掉则测试失败。
    Evidence: .sisyphus/evidence/task-7-videos-error.json
  ```

  **Commit**：NO | Message: `feat(backend): align video endpoints and stats` | Files: `backend/routers/videos.py`, `backend/schemas.py`, `backend/models.py`

- [ ] 8. 补强管理员 API、清理语义与 API 余额占位策略

  **要做什么**：把现有 `/admin/*` 收敛到可执行的 API-only 管理面：用户分页、创建、更新、待处理队列、总览统计、API 余额占位、数据清理。保留 admin-web 为 deferred，但保证所有管理员能力均能通过 API 单独验证。
  **禁止事项**：不要把 admin-web 前端拉进本阶段；不要让普通用户访问管理员接口；不要让清理接口删除记录本身；不要把 `api-balance` 包装成已接入真实供应商余额查询。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：API 已有雏形，重点在权限、语义、分页与清理行为
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 2 | Blocks: 14, 15 | Blocked By: 2, 3, 6

  **参考资料**：
  - 管理员路由：`backend/routers/admin.py:14-157` — 现有 users/pending/stats/api-balance/cleanup 已存在
  - 权限依赖：`backend/dependencies.py:36-39` — `get_admin_user`
  - 管理员用户模型：`backend/schemas.py:89-112` — `UserAdminResponse` / create / update schema
  - 视频模型：`backend/models.py:24-44` — cleanup 与 pending queue 的数据基础
  - 旧计划意图：`plans/PLAN.md:232-260` — 管理员接口仍然是有效业务需求，但前端管理后台可后置

  **验收标准**：
  - [ ] 管理员 token 调用 `/admin/users`、`/admin/videos/pending`、`/admin/stats`、`/admin/api-balance`、`/admin/cleanup` 全部成功。
  - [ ] 普通用户调用任意 `/admin/*` 返回 403。
  - [ ] `/admin/cleanup` 仅清空 `corrected_text` 与 `markdown_content`，不删除记录，不影响 `title / summary / tags / video_type` 等轻量字段。

  **QA 场景**：
  ```
  Scenario: Happy path 管理员 API
    Tool: Bash
    Steps: 使用管理员账号登录；依次调用 `/admin/users`、`/admin/videos/pending`、`/admin/stats`、`/admin/api-balance`、`/admin/cleanup?days=30`。
    Expected: 全部返回 200；`/admin/stats` 含 `total_users/active_users/total_videos/pending_videos`；`/admin/api-balance` 返回 `openai/kimi/gemini` 占位键。
    Evidence: .sisyphus/evidence/task-8-admin-happy.json

  Scenario: Failure/edge case 权限与误删
    Tool: Bash
    Steps: 用普通用户 token 调用 `/admin/users`；准备一条已完成记录后执行 `/admin/cleanup`，再次读取记录确认仍存在。
    Expected: 普通用户得到 403；cleanup 后记录仍存在，仅大字段被清空。
    Evidence: .sisyphus/evidence/task-8-admin-error.json
  ```

  **Commit**：NO | Message: `feat(backend): harden admin api semantics` | Files: `backend/routers/admin.py`, `backend/schemas.py`, `backend/models.py`

- [ ] 9. 实现 `core/db_scheduler.py` 与数据库回写适配层

  **要做什么**：新增独立的 `core/db_scheduler.py`，按 Task 4 冻结的契约从 `videos` 表拉取 `待处理` 记录，原子抢占为 `处理中`，调用 `ProcessingPipeline.process(url, skip_feishu_sync=True)`，再把结果映射回数据库字段；失败写入 `error_msg` 与 `失败` 状态；支持可控桩模式以验证成功与失败路径；保留 `core/scheduler.py` 不动。
  **禁止事项**：不要改写飞书调度器；不要直接依赖真实飞书记录；不要让异常把任务永久卡死在 `处理中`；不要允许并发消费同一条记录两次。

  **推荐 Agent Profile**：
  - Category: `deep` — 原因：涉及核心处理链路、状态机、并发与可验证性
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 2 | Blocks: 14, 15 | Blocked By: 3, 4, 7

  **参考资料**：
  - 处理入口：`core/pipeline.py:39-147` — `process()` 成功/失败返回结构
  - Markdown 产物：`core/pipeline.py:94-139` — `markdown_path` 与 `processed_content`
  - 旧调度器：`core/scheduler.py:153-215` — 处理一条记录的状态推进模式
  - 飞书字段映射参考：`core/scheduler.py:217-269` — 可类比到数据库字段写回
  - 数据模型：`backend/models.py:24-44` — `videos` 表字段就是回写目标
  - 旧计划目标：`plans/PLAN.md:139-177` — 新调度器、失败处理、数据清理是有效业务诉求
  - 契约基线：`.sisyphus/evidence/task-4-db-scheduler-contract.md` — 必须严格遵守已冻结的状态机与映射规则

  **验收标准**：
  - [ ] 新增 `core/db_scheduler.py`，并能把数据库中的 `待处理` 记录推进到 `处理中 / 已完成 / 失败`。
  - [ ] 成功时回写 `title / author / summary / core_points / golden_sentences / tags / video_type / corrected_text / markdown_content / processed_at`。
  - [ ] 失败时写入 `error_msg`，并保证异常后不会留下永久 `处理中` 的脏状态。

  **QA 场景**：
  ```
  Scenario: Happy path 数据库调度成功回写
    Tool: Bash
    Steps: 按 Task 3 基线启动 MySQL 与后端；插入一条 `待处理` 视频记录；以桩模式运行 `core/db_scheduler.py` 完成一次处理；读取数据库记录。
    Expected: 记录经历 `待处理 -> 处理中 -> 已完成`，并填充 `summary/core_points/golden_sentences/tags/video_type/corrected_text/markdown_content/processed_at`。
    Evidence: .sisyphus/evidence/task-9-db-scheduler-happy.json

  Scenario: Failure/edge case 失败回写与重复消费保护
    Tool: Bash
    Steps: 插入一条待处理记录；以失败桩模式运行调度器；再并发触发第二个 worker 尝试消费同一记录。
    Expected: 记录最终为 `失败` 且 `error_msg` 有值；同一条记录不会被两个 worker 同时重复消费；若任务中断，恢复逻辑可把卡死状态重新暴露给后续处理。
    Evidence: .sisyphus/evidence/task-9-db-scheduler-error.json
  ```

  **Commit**：NO | Message: `feat(core): add db scheduler and writeback flow` | Files: `core/db_scheduler.py`, `backend/models.py`, `backend/database.py`, `core/pipeline.py`

- [ ] 10. 固化本地运行入口、Dockerfile 与最小 compose 编排

  **要做什么**：把本阶段所有本地启动入口整理成可复跑的最小运行面：`backend/Dockerfile`、根级 `docker-compose.yml`、后端启动命令、MySQL 初始化、db_scheduler 启动命令、iOS 数据库模式联调目标地址。该任务的目的不是部署上云，而是为 Task 14 端到端联调提供统一运行脚手架。
  **禁止事项**：不要把 admin-web 一起拉入 compose；不要要求手工拼接数据库命令；不要沿用 README 中不存在的根级 `requirements.txt` 启动路径；不要把真实 `.env` 写进 compose。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：需要补齐本地运行基线与容器化入口
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 2 | Blocks: 14, 15 | Blocked By: 3

  **参考资料**：
  - 依赖真源：`backend/requirements.txt:1-8`
  - 服务入口：`backend/main.py:7-22`
  - 数据库配置：`backend/database.py:7-28`
  - README 旧描述：`README.md:27-56`、`107-124` — 仍指向旧的 root requirements 与旧项目结构
  - 守卫规则：`.gitignore:14-35` — 生成目录与测试噪音目录不能混入 compose 输入
  - 业务目标：`plans/PLAN.md:264-285` — 本地联调与部署准备是原计划后段目标，应保留为主线支撑项

  **验收标准**：
  - [ ] 新增 `backend/Dockerfile` 与根级 `docker-compose.yml`，至少能拉起 MySQL 与后端服务。
  - [ ] 文档化 `db_scheduler` 启动命令，并确保能在 compose 之外以单独命令运行。
  - [ ] 任何执行者都能按一套固定命令启动后端链路，不需要猜测路径与端口。

  **QA 场景**：
  ```
  Scenario: Happy path 本地运行编排
    Tool: Bash
    Steps: 执行 `docker compose up -d` 启动 MySQL 与 backend；等待服务就绪后请求 `curl http://127.0.0.1:8001/health`；再单独启动 db_scheduler 一次。
    Expected: compose 启动成功，`/health` 返回 `{"status":"ok"}`，db_scheduler 进程可成功连接数据库并进入待命/处理状态。
    Evidence: .sisyphus/evidence/task-10-local-runtime.txt

  Scenario: Failure/edge case 启动文档漂移
    Tool: Bash
    Steps: 校验 compose 或 README/运行说明是否仍指向不存在的 `requirements.txt`、错误端口或缺失 MySQL 环境变量。
    Expected: 只要命令无法按文档直接启动，或文档仍引用旧结构，即判定失败。
    Evidence: .sisyphus/evidence/task-10-local-runtime-error.txt
  ```

  **Commit**：NO | Message: `chore(dev): add local runtime and compose baseline` | Files: `backend/Dockerfile`, `docker-compose.yml`, `README.md`, `plans/PLAN.md`

- [ ] 11. 实现 iOS `DataSourceMode`、模式持久化与 `AppServices` 动态注入

  **要做什么**：基于 Task 5 架构冻结，新增 `DataSourceMode`，扩展 `AuthManager` 以持久化 `mode`，并让 `AppServices` 不再是固定静态实例，而是根据当前模式解析 `AuthServiceProtocol` / `VideoRepositoryProtocol`。登录页要能显式切换“数据库模式 / 飞书测试模式”，退出登录时清理模式与会话。
  **禁止事项**：不要继续使用 `fatalError("Server mode is not implemented yet.")`；不要只持久化 token 而遗漏 mode；不要把飞书测试模式的固定账号提示显示到数据库模式；不要在模式切换后复用上一个模式的 repository 实例。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：属于 iOS 架构重接线，影响登录与全部页面依赖解析
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 3 | Blocks: 12, 13, 14 | Blocked By: 2, 5, 6

  **参考资料**：
  - 当前配置：`ios_app/iOS_Video_Intelligence/Services/AppConfig.swift:3-30`
  - 当前会话：`ios_app/iOS_Video_Intelligence/Services/AuthManager.swift:4-64`
  - 本地 mock 登录：`ios_app/iOS_Video_Intelligence/Services/AuthService.swift:38-61`
  - 登录页：`ios_app/iOS_Video_Intelligence/Views/LoginView.swift:37-133`
  - 旧计划目标：`plans/PLAN.md:183-210` — 模式切换、模式持久化、服务注入、`tableId` 保留

  **验收标准**：
  - [ ] 新增 `DataSourceMode` 并持久化到 `UserDefaults`；App 重启后恢复最近一次模式。
  - [ ] `LoginView` 显示模式切换 UI，默认数据库模式；飞书测试模式显示 `test / 0104` 提示，数据库模式不显示。
  - [ ] 模式切换后，`AuthManager` 与 `AppServices` 解析出的 service/repository 实例立即跟随变化。

  **QA 场景**：
  ```
  Scenario: Happy path 模式持久化与注入
    Tool: Bash
    Steps: 执行 `xcodebuild test -project "ios_app/iOS_Video_Intelligence/iOS_Video_Intelligence.xcodeproj" -scheme "iOS_Video_Intelligence" -destination "generic/platform=iOS Simulator"`，覆盖 mode 持久化与 service 解析用例。
    Expected: 测试验证数据库模式为默认值，模式切换后重启仍能恢复，且 `AppServices` 返回的实现与当前模式一致。
    Evidence: .sisyphus/evidence/task-11-ios-mode.txt

  Scenario: Failure/edge case 模式串线
    Tool: Bash
    Steps: 在测试中先登录飞书测试模式，再切到数据库模式并重新登录；断言 repository/authService 实例未复用旧模式对象。
    Expected: 若数据库模式仍落到 `LocalMockAuthService` 或飞书模式误用 server repository，则测试失败。
    Evidence: .sisyphus/evidence/task-11-ios-mode-error.txt
  ```

  **Commit**：NO | Message: `feat(ios): add datasource mode persistence` | Files: `ios_app/iOS_Video_Intelligence/Services/AppConfig.swift`, `ios_app/iOS_Video_Intelligence/Services/AuthManager.swift`, `ios_app/iOS_Video_Intelligence/Services/AuthService.swift`, `ios_app/iOS_Video_Intelligence/Views/LoginView.swift`

- [ ] 12. 实现 `ServerAuthService`、`ServerVideoRepository` 与概览统计模型

  **要做什么**：在 iOS 侧补齐真正消费后端 canonical API 的实现：新增 `ServerAuthService`、`ServerVideoRepository`，废弃旧 `APIService.swift` 的 `/api/*` 路径假设，扩展 `VideoRepositoryProtocol` 支持 `fetchOverviewStats(tableId:)`，并新增数据库模式所需的概览统计模型与解码逻辑。
  **禁止事项**：不要继续保留旧 `APIService.swift` 作为本阶段真源；不要把数据库模式强行要求 `tableId` 非空；不要在 repository 外层让页面自己判断模式分支；不要让新服务依赖 `AppConfig.Feishu` 的直连配置。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：iOS 与后端契约落地的核心接缝都在这个任务里
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 3 | Blocks: 13, 14 | Blocked By: 2, 5, 6, 7, 11

  **参考资料**：
  - 旧客户端实现：`ios_app/iOS_Video_Intelligence/Services/APIService.swift:16-90` — 旧 `/api/*` 约定必须被替换
  - Repository 协议：`ios_app/iOS_Video_Intelligence/Services/VideoRepository.swift:3-149` — 需要保留现有方法并新增概览统计
  - iOS 模型：`ios_app/iOS_Video_Intelligence/Models/VideoRecord.swift:49-109` — 登录、提交、列表、类型统计模型
  - 后端鉴权契约：`backend/routers/auth.py:22-56`
  - 后端视频契约：`backend/routers/videos.py:43-137`
  - 后端 schema：`backend/schemas.py:30-87`
  - 概览需求：`ios_app/iOS_Video_Intelligence/Views/ProfileView.swift:27-68`

  **验收标准**：
  - [ ] 新增 `ServerAuthService` 与 `ServerVideoRepository`，数据库模式下可完整覆盖登录、提交、列表、详情、类型统计、概览统计。
  - [ ] 扩展 `VideoRepositoryProtocol` 支持 `fetchOverviewStats(tableId:)`，数据库模式允许 `tableId` 为空字符串。
  - [ ] 旧 `APIService.swift` 不再作为页面直接依赖，且任何新实现都只请求 canonical `/auth/*`、`/videos*` 路径。

  **QA 场景**：
  ```
  Scenario: Happy path iOS 消费 canonical API
    Tool: Bash
    Steps: 启动本地 backend；执行 `xcodebuild test -project "ios_app/iOS_Video_Intelligence/iOS_Video_Intelligence.xcodeproj" -scheme "iOS_Video_Intelligence" -destination "generic/platform=iOS Simulator"`，覆盖 `ServerAuthService` / `ServerVideoRepository` 的网络解码与协议适配测试。
    Expected: 测试通过，且请求路径全部落在 `/auth/*`、`/videos*`；概览统计模型可被正确解码。
    Evidence: .sisyphus/evidence/task-12-ios-server-repo.txt

  Scenario: Failure/edge case 旧路由回潮
    Tool: Bash
    Steps: 在测试或静态校验中扫描 iOS 服务层，确认没有新的 `/api/auth/token`、`/api/videos/list` 请求；再验证数据库模式下 `tableId=""` 不会导致 repository 抛错。
    Expected: 若仍调用旧 `/api/*` 路由，或数据库模式强依赖 `tableId`，则验证失败。
    Evidence: .sisyphus/evidence/task-12-ios-server-repo-error.txt
  ```

  **Commit**：NO | Message: `feat(ios): add server auth and video repositories` | Files: `ios_app/iOS_Video_Intelligence/Services/APIService.swift`, `ios_app/iOS_Video_Intelligence/Services/AuthService.swift`, `ios_app/iOS_Video_Intelligence/Services/VideoRepository.swift`, `ios_app/iOS_Video_Intelligence/Models/VideoRecord.swift`

- [ ] 13. 接入 `LoginView` / `SubmitView` / `HistoryView` / `DetailView` / `ProfileView` 的双模式行为

  **要做什么**：将数据库模式与飞书测试模式真正接入现有页面：`LoginView` 增加模式切换；`SubmitView`、`HistoryView`、`DetailView` 走统一 repository；`ProfileView` 从概览接口/飞书聚合读取真实数据并显示当前模式；两种模式下页面功能保持一致但数据源不同。
  **禁止事项**：不要让页面自己散落大量 `if mode == ...` 的分支；不要保留 `ProfileView` 的硬编码统计数字；不要让数据库模式和飞书测试模式显示同一份缓存数据；不要把详情页改成只能展示某一模式的数据结构。

  **推荐 Agent Profile**：
  - Category: `unspecified-high` — 原因：多页面接线，容易出现模式串线与 UI 状态不一致
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: YES | Wave 3 | Blocks: 14, 15 | Blocked By: 2, 5, 7, 11, 12

  **参考资料**：
  - 登录页：`ios_app/iOS_Video_Intelligence/Views/LoginView.swift:37-133`
  - 提交页：`ios_app/iOS_Video_Intelligence/Views/SubmitView.swift:12-205`
  - 历史页：`ios_app/iOS_Video_Intelligence/Views/HistoryView.swift:13-220`
  - 详情页：`ios_app/iOS_Video_Intelligence/Views/DetailView.swift:3-176`
  - 我的页：`ios_app/iOS_Video_Intelligence/Views/ProfileView.swift:3-135`
  - Video 模型：`ios_app/iOS_Video_Intelligence/Models/VideoRecord.swift:3-47`
  - 双模式基线：`.sisyphus/evidence/task-5-ios-architecture.md`
  - Repository 基线：`ios_app/iOS_Video_Intelligence/Services/VideoRepository.swift:3-149`

  **验收标准**：
  - [ ] `LoginView` 默认数据库模式，可切换到飞书测试模式；飞书测试模式显示 `test / 0104` 提示。
  - [ ] `SubmitView`、`HistoryView`、`DetailView` 在两种模式下都可工作，且页面层不直接知道底层来源是 Feishu 还是 backend。
  - [ ] `ProfileView` 使用真实概览统计，显示当前数据源模式，不再展示硬编码 `156 / 12 / 3`。

  **QA 场景**：
  ```
  Scenario: Happy path 页面双模式接入
    Tool: Bash
    Steps: 执行 `xcodebuild test -project "ios_app/iOS_Video_Intelligence/iOS_Video_Intelligence.xcodeproj" -scheme "iOS_Video_Intelligence" -destination "generic/platform=iOS Simulator"`，覆盖登录模式切换、提交、历史列表、详情、Profile 统计。
    Expected: 两种模式下页面逻辑均通过测试；`ProfileView` 显示真实统计与当前模式；`LoginView` 提示语随模式切换。
    Evidence: .sisyphus/evidence/task-13-ios-ui.txt

  Scenario: Failure/edge case 模式数据串线
    Tool: Bash
    Steps: 先在飞书测试模式下加载历史数据，再切到数据库模式重新登录；断言页面展示的数据与新模式对应，且不残留旧模式统计或列表。
    Expected: 若页面缓存跨模式串线，或 `ProfileView` 仍显示硬编码数字，则验证失败。
    Evidence: .sisyphus/evidence/task-13-ios-ui-error.txt
  ```

  **Commit**：NO | Message: `feat(ios): wire dual-mode views` | Files: `ios_app/iOS_Video_Intelligence/Views/LoginView.swift`, `ios_app/iOS_Video_Intelligence/Views/SubmitView.swift`, `ios_app/iOS_Video_Intelligence/Views/HistoryView.swift`, `ios_app/iOS_Video_Intelligence/Views/DetailView.swift`, `ios_app/iOS_Video_Intelligence/Views/ProfileView.swift`

- [ ] 14. 执行本地端到端联调并固化验收矩阵

  **要做什么**：把本阶段真正的“完成”跑通并证据化：数据库模式下完成 `iOS → FastAPI → MySQL → db_scheduler → 回写结果 → iOS 读取`；飞书测试模式下完成 `iOS → 飞书直连`；管理员 API 能独立工作；所有链路以固定命令矩阵与固定证据路径收口。
  **禁止事项**：不要用“我本地看起来可以”代替证据；不要要求用户手工点页面；不要只测 happy path；不要把 admin-web 或 Streamlit 塞进本阶段联调入口。

  **推荐 Agent Profile**：
  - Category: `deep` — 原因：这是所有子系统交汇的最终联调任务
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: NO | Wave 3 | Blocks: 15 | Blocked By: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13

  **参考资料**：
  - 后端入口：`backend/main.py:7-22`
  - 视频 API：`backend/routers/videos.py:43-137`
  - 管理员 API：`backend/routers/admin.py:14-157`
  - 调度入口：`core/pipeline.py:39-147`
  - iOS 工程/target：`ios_app/iOS_Video_Intelligence/iOS_Video_Intelligence.xcodeproj/project.pbxproj:44-46`、`187-220`
  - 旧业务目标：`plans/PLAN.md:11-20`、`264-321` — E2E、本地运行、测试清单仍有效
  - 守卫规则：`.sisyphus/plans/init-deep.md:67-71` — 证据必须可复跑、零人工

  **验收标准**：
  - [ ] `docker compose up -d` 后，`curl http://127.0.0.1:8001/health` 返回 `{"status":"ok"}`。
  - [ ] 数据库模式：登录、提交、列表、详情、类型统计、概览统计、调度回写全部打通，并在数据库中可见状态推进。
  - [ ] 飞书测试模式：`test / 0104` 登录、提交、历史、详情、统计链路保持可用，且不依赖新后端。

  **QA 场景**：
  ```
  Scenario: Happy path 双链路端到端联调
    Tool: Bash
    Steps: 1) `docker compose up -d`；2) 启动 backend 与 db_scheduler；3) 执行后端 smoke（register/login/submit/list/detail/stats/overview/admin）；4) 执行 `xcodebuild test -project "ios_app/iOS_Video_Intelligence/iOS_Video_Intelligence.xcodeproj" -scheme "iOS_Video_Intelligence" -destination "generic/platform=iOS Simulator"`；5) 汇总数据库状态与 iOS 测试结果。
    Expected: 数据库模式与飞书测试模式测试全部通过；数据库模式记录完成回写；管理员 API 可用；所有证据路径可复查。
    Evidence: .sisyphus/evidence/task-14-e2e.md

  Scenario: Failure/edge case 断链定位
    Tool: Bash
    Steps: 人为让一条数据库模式任务走失败桩路径，并再次执行端到端矩阵；同时校验飞书测试模式不受影响。
    Expected: 数据库模式失败被正确记录为 `失败` 且 `error_msg` 有值；飞书测试模式链路继续通过；若任一链路互相污染则失败。
    Evidence: .sisyphus/evidence/task-14-e2e-error.md
  ```

  **Commit**：NO | Message: `test(integration): validate backend scheduler and ios flows` | Files: `.sisyphus/evidence/task-14-e2e.md`, `.sisyphus/evidence/task-14-e2e-error.md`

- [ ] 15. 同步 README / `plans/*` / 问题记录并清理过期叙述

  **要做什么**：把所有计划与文档同步到活代码：删掉“创建 backend 骨架”的过期叙述；标记 admin-web 为 deferred；说明 Streamlit 非本阶段主线；写清数据库模式 / 飞书测试模式、后端启动方式、MySQL 配置、本地联调步骤、当前真实未完成项。所有文档更新必须建立在 Task 14 实际证据之上。
  **禁止事项**：不要在联调未完成前抢先改文档；不要继续声称存在根级 `requirements.txt` 启动路径；不要把旧 `/api/*` 路由写回 README 或计划；不要复制敏感配置值。

  **推荐 Agent Profile**：
  - Category: `writing` — 原因：这是基于真实实现结果的收口型文档同步任务
  - Skills: `[]` — 不需要额外技能
  - Omitted: `[git-master]` — 本任务不涉及 git 操作

  **并行性**：Can Parallel: NO | Wave 3 | Blocks: none | Blocked By: 1, 2, 8, 9, 10, 13, 14

  **参考资料**：
  - 现有 README：`README.md:17-55`、`107-124` — 技术栈与项目结构存在过时描述
  - 旧主计划：`plans/PLAN.md:11-37` — 业务目标可保留，但 backend 骨架条目必须删除或改写
  - init 守卫规则：`.sisyphus/plans/init-deep.md:51-71` — 排除目录、秘密安全、证据化验证需要吸收到文档说明
  - 本计划证据：`.sisyphus/evidence/task-14-e2e.md`、`.sisyphus/evidence/task-14-e2e-error.md`

  **验收标准**：
  - [ ] `README.md`、`plans/PLAN.md`、相关 `plans/*` 文档与当前实现一致，不再写“待创建 backend 骨架”。
  - [ ] 文档明确说明：admin-web deferred、Streamlit 非本阶段主线、canonical API 采用 `/auth/*` 与 `/videos*`、本地启动依赖 `backend/requirements.txt` 与 compose。
  - [ ] 文档同步只引用非敏感示例与 Task 14 已验证过的命令。

  **QA 场景**：
  ```
  Scenario: Happy path 文档回写
    Tool: Bash
    Steps: 读取 Task 14 证据，更新 README 与 `plans/*`；随后扫描文档中的 backend 骨架、旧 `/api/*`、错误 requirements 路径、admin-web 已实现等表述。
    Expected: 所有过期叙述已移除或改写；文档中只保留已验证通过的启动与联调说明。
    Evidence: .sisyphus/evidence/task-15-doc-sync.md

  Scenario: Failure/edge case 文档再次漂移
    Tool: Bash
    Steps: 校验 README / `plans/*` 是否仍包含“创建 backend/main.py”“/api/videos/list”“根级 requirements.txt 为启动真源”等过期表述。
    Expected: 只要任一过期表述残留，或文档引用未验证命令，验证失败。
    Evidence: .sisyphus/evidence/task-15-doc-sync-error.txt
  ```

  **Commit**：NO | Message: `docs(plan): sync roadmap and readme to verified behavior` | Files: `README.md`, `plans/PLAN.md`, `plans/*.md`

## 最终验证波次（4 路并行，全部通过才算完成）
- [ ] F1. 计划合规审计 — oracle
- [ ] F2. 代码质量复核 — unspecified-high
- [ ] F3. 真实联调 QA — unspecified-high（若涉及 UI，补充 iOS/Playwright 等自动化）
- [ ] F4. 范围与守卫规则复核 — deep

## 提交策略
- 未经用户明确要求，不创建 git commit。
- 若后续要求提交，建议按单一可审查意图拆分：验证基线 → 后端契约 → 调度器 → iOS 双模式 → 文档同步。
- 不允许把后端契约修正、调度器接入、iOS 适配、文档回写混成一个不可回滚的大提交。

## 成功标准
- 新计划完全基于活代码，不再把过期脚手架工作当成待办。
- 后端、核心调度链路、iOS 双模式之间的接口、状态和值域全部冻结且一致。
- 所有关键链路都可以通过 agent 可执行命令完成本地验证。
- `init-deep` 的有效守卫规则已吸收，但不再作为独立工作流干扰业务主线。
- 文档、README、计划文件与当前代码状态一致，不再出现陈旧叙述。
