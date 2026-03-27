# 总控进度看板

> 本文件是项目总控维护文件。
> 后续每完成一项工作，优先更新这里，再同步到对应模块文档。

## 当前阶段

- 当前主线：P3 下一轮产品能力补齐——后端能力已落地，待 Web 接入
- 当前状态：后端 P3 字段、接口与迁移脚本已完成
- 最近更新：2026-03-27

## 已完成

- [x] 建立 `status/` 文档体系
- [x] 建立总路线图 `status/roadmap.md`
- [x] 建立模块状态文档
- [x] 重建 `backend/` 基础结构
- [x] 重建认证接口 `/auth/register`、`/auth/login`、`/auth/me`
- [x] 重建视频接口 `/videos`、`/videos/submit`、`/videos/{id}`、`/videos/stats`、`/videos/overview`
- [x] 重建管理接口 `/admin/users`、`/admin/videos/pending`、`/admin/stats`、`/admin/api-balance`、`/admin/cleanup`
- [x] 新增健康检查接口 `/health`
- [x] 重建 `core/db_scheduler.py`
- [x] 打通数据库驱动的认领、写回、失败恢复逻辑
- [x] 建立 Alembic 基础迁移配置
- [x] 通过后端认证回归测试
- [x] 通过后端视频回归测试
- [x] 通过后端管理回归测试
- [x] 通过数据库调度回归测试
- [x] 建立 `web_app/` 前端项目骨架
- [x] 完成 Web 与 iOS 最小联调验证
- [x] 已完成下一轮 iOS / Web / Backend 统一路线设计
- [x] 已明确采用"快捷指令独立密钥"方案
- [x] 已明确不采用"快捷指令每次提交账号密码"方案
- [x] P3 后端新增 videos 表收藏与处理中状态字段（`is_favorited`、`processing_stage`、`processing_detail`、`estimated_seconds_remaining`、`last_stage_update_at`）
- [x] P3 后端新增 `shortcut_keys` 表模型
- [x] P3 后端新增记录能力接口：`DELETE /videos/{id}`、`POST /videos/{id}/favorite`、`GET /videos/{id}/status`
- [x] P3 后端新增快捷指令密钥接口：`POST /shortcut-keys`、`GET /shortcut-keys`、`DELETE /shortcut-keys/{id}`、`POST /shortcut-submit`
- [x] P3 Alembic 新增迁移脚本 `20260327_p3_new_fields.py`
- [x] `db_scheduler` 认领/成功/失败时写入 `processing_stage` 字段

## 下一步待做

- [ ] Web 先接删除、收藏、处理中状态展示与快捷指令密钥管理
- [ ] iOS 再接删除、收藏、处理中状态展示与快捷指令密钥能力
- [ ] 最后推进 Web 界面美化与交互细节优化
- [ ] 增加页面级测试、失败场景测试与安全验证

## 当前阻塞与注意事项

- [ ] 当前机器上同时存在 `8001` 旧服务和 `8002` 新后端，联调时必须以 `8002` 为准
- [ ] `8501` 调试台数据库列表目前未展示 `tags` 等完整字段，这属于展示层问题
- [ ] 服务器迁移继续后置，不作为当前阶段主任务

## 本地验证记录

- [x] `pytest -q test/test_backend_auth.py`
- [x] `pytest -q test/test_backend_videos.py`
- [x] `pytest -q test/test_backend_admin.py`
- [x] `pytest -q test/test_db_scheduler.py`
- [x] `alembic -c alembic.ini upgrade head`
- [x] `cd web_app && npm.cmd test`
- [x] `cd web_app && npm.cmd run build`
- [x] `python -m compileall backend core`
- [x] `http://127.0.0.1:8002/health` 已确认返回新后端健康信息和数据库路径
- [x] iPhone 浏览器访问局域网后端健康检查通过
- [x] iOS App 最小联调链路通过

## 维护规则

- [x] 已完成事项必须改为 `[x]`
- [ ] 未完成事项保留 `[ ]`
- [ ] 每次新增任务，先写入本文件，再执行实现
- [ ] 每次完成任务，先更新本文件，再更新模块文档
