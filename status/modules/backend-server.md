# 后端服务器

## 模块定位

统一承载用户认证、视频记录管理、后台管理接口、数据库调度写回和本地健康检查。

## 当前状态

已运行

## 已完成

- 建立全新的 `backend/` 包结构
- 建立数据库入口、模型、鉴权、依赖和主路由
- 固化公开接口合同：`/auth`、`/videos`、`/admin`、`/health`
- 建立 Alembic 配置和首个迁移脚本
- 通过认证、视频、管理、调度四组后端回归测试

## 未完成

- 补充服务器迁移说明
- 后续接入 PostgreSQL 运行验证
- 等待前端与调试台手测反馈后进入下一轮修复

## 验证证据

- `pytest -q test/test_backend_auth.py`
- `pytest -q test/test_backend_videos.py`
- `pytest -q test/test_backend_admin.py`
- `pytest -q test/test_db_scheduler.py`
- `alembic -c alembic.ini upgrade head`

## 当前难点

- 服务器侧数据库尚未切换到 PostgreSQL 验证
- 当前机器同时存在 `8001` 旧服务和 `8002` 新后端，联调必须统一以 `8002` 为准

## 下一步任务

- 准备 PostgreSQL 配置与迁移说明
- 为 Web 联调补充更多端到端测试
- 根据手测结果修复接口与联调问题

## 最后更新

2026-03-23
