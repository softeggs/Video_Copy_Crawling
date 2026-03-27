# 状态中心

本目录是项目唯一的开发进度入口，用于同步阶段目标、模块现状、阻塞点、验证结果和后续任务。

## 优先查看

- 总控看板：`status/MASTER_STATUS.md`
- 阶段路线图：`status/roadmap.md`
- 下一阶段路线：`status/next_phase_ios_web_plan.md`
- 模块详情：`status/modules/*.md`

## 维护规则

- 每个阶段完成后，同时更新 `status/MASTER_STATUS.md`、`status/roadmap.md` 和对应模块文档。
- 模块状态统一使用：`已运行`、`开发中`、`阻塞`、`缺失源码`、`已降级`、`暂缓`。
- 文档字段固定包含：`模块定位`、`当前状态`、`已完成`、`未完成`、`验证证据`、`当前难点`、`下一步任务`、`最后更新`。
- 当前阶段优先级以 `status/MASTER_STATUS.md`、`status/roadmap.md` 和 `status/next_phase_ios_web_plan.md` 为准。

## 当前主线

- 主线 1：iOS 最小联调已完成，下一阶段进入产品功能增强。
- 主线 2：后端先补统一数据模型、记录状态、收藏、删除和快捷指令密钥能力。
- 主线 3：Web 与 iOS 共用同一套后端接口推进功能优化。
- 主线 4：快捷指令采用“独立密钥”方案，不采用“每次提交账号密码”方案。
- 后置项：PostgreSQL 与服务器迁移继续后排。

最后更新：2026-03-26
