# 总控进度看板

> 本文件是项目总控维护文件。  
> 后续每完成一项工作，优先更新这里，再同步到对应模块文档。

## 当前阶段

- 当前主线：前后端优先，`iOS` 暂缓
- 当前状态：前后端基础联通完成，进入 Web 可用性增强阶段
- 最近更新：2026-03-25

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
- [x] 实现 Web 登录页
- [x] 实现 Web 注册页
- [x] 实现 Web 提交页
- [x] 实现 Web 历史记录页
- [x] 实现 Web 详情页
- [x] 实现 Web 个人页
- [x] 完成 Web API 客户端封装
- [x] 完成 Web 最小单测
- [x] 完成 Web 构建验证
- [x] 已支持通过 `web_app/.env.local` 切换前端本地后端端口
- [x] 已定位前端注册失败原因为前端默认连接 `8001`，实际新后端运行在 `8002`
- [x] 已确认新后端 `8002` 使用数据库 `local_dev.sqlite3`
- [x] 已确认当前数据库中已有注册用户和视频记录
- [x] 前端提交页增加 URL 校验
- [x] 后端 `/videos/submit` 增加 URL 校验
- [x] 调试台增加数据库明细查看能力
- [x] 新增 URL 校验相关自动化测试
- [x] 将 `app.py` 改为内部调试台
- [x] 在调试台展示后端健康状态
- [x] 在调试台展示用户与视频摘要
- [x] 在调试台支持手动触发数据库调度
- [x] 创建长期模块分支
- [x] 手动测试 Web 提交页 URL 校验
- [x] 手动测试后端拒绝非法提交
- [x] 手动测试调试台数据库明细查看
- [x] 手动确认 `cd web_app && npm.cmd run dev` 联调可用
- [x] 手动确认 `streamlit run app.py` 联调可用
- [x] 验证合法视频链接可完成“提交 -> 调度 -> 转录 -> 写库 -> 飞书同步”全链路
- [x] 汇总手测结果并进入下一轮优化

## 待你手测

- [x] 手动测试 Web 提交页 URL 校验
- [x] 手动测试后端拒绝非法提交
- [x] 手动测试调试台数据库明细查看
- [x] 汇总手测问题并进入修复轮次

## 下一步待做

- [ ] 修复并清理历史失败任务的错误展示与排障体验
- [ ] 增加 Web 历史记录分页和状态筛选
- [ ] 增加 Web 空态、错误态和加载态优化
- [ ] 增强调试台的失败任务和错误详情展示
- [ ] 准备 PostgreSQL 配置与迁移说明
- [ ] 固化本地到服务器的迁移清单
- [ ] 等前后端稳定后，再切换 `iOS` 到后端主链路

## 当前阻塞与注意事项

- [ ] 当前机器上同时存在 `8001` 旧服务和 `8002` 新后端，联调时必须以 `8002` 为准
- [ ] 当前服务器迁移尚未开始，只完成了本地优先的实现与验证
- [ ] 当前仍存在历史失败记录，需区分“旧失败脏数据”和“现网主链路可用”两个事实

## 本地验证记录

- [x] `pytest -q test/test_backend_auth.py`
- [x] `pytest -q test/test_backend_videos.py`
- [x] `pytest -q test/test_backend_admin.py`
- [x] `pytest -q test/test_db_scheduler.py`
- [x] `alembic -c alembic.ini upgrade head`
- [x] `cd web_app && npm.cmd test`
- [x] `cd web_app && npm.cmd run build`
- [x] `python -m compileall app.py backend`
- [x] `http://127.0.0.1:8002/health` 已确认返回新后端健康信息和数据库路径
- [x] `cd web_app && npm.cmd run dev` 手动联调确认
- [x] `streamlit run app.py` 手动联调确认

## 维护规则

- [x] 已完成事项必须改为 `[x]`
- [ ] 未完成事项保留 `[ ]`
- [ ] 每次新增任务，先写入本文件，再执行实现
- [ ] 每次完成任务，先更新本文件，再更新模块文档
