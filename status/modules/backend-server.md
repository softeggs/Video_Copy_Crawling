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
- P3 新增 videos 表收藏与处理中状态字段
- P3 新增 `shortcut_keys` 表
- P3 新增记录能力接口（删除/收藏/状态轮询）
- P3 新增快捷指令密钥接口（生成/列表/吊销/快捷提交）
- P3 Alembic 新增迁移脚本
- `db_scheduler` 认领/成功/失败时写入 `processing_stage`
- P7 第一阶段新增数据库调度常驻入口 `scripts/run_db_scheduler.py`
- P7 第一阶段补齐 `Dockerfile`、`docker-compose.yml`、Nginx 配置和部署环境模板
- P7 第一阶段补齐本地部署演练文档 `docs/P7_LOCAL_DEPLOYMENT.md`
- P7 第一阶段完成基础 Docker 联调，确认后端健康检查可用
- P7 第一阶段确认数据库调度器可认领任务并写回失败状态
- P7 第一阶段完成 DeepSeek provider 接入
- P7 第一阶段完成抖音真实链接“下载 -> 转写 -> AI 润色 -> 飞书写回”闭环验证

## 未完成

- 为调度流程写入详细阶段和预计时间（流水线侧尚未接入）
- 验证本地 Docker 化演练闭环
- 后续接入 PostgreSQL 运行验证
- 第二阶段接入真实云主机参数
- 收敛 Docker 镜像体积与部署依赖

## 当前难点

- 当前机器同时存在 `8001` 旧服务和 `8002` 新后端，联调必须统一以 `8002` 为准
- 流水线侧尚未接入 `update_processing_stage`，处理中状态暂时依赖 db_scheduler 写入
- 处理中状态展示需要后端提供阶段、详情和预计时间，不能只靠一列状态字符串

## 下一步任务

- 执行 `docker compose config` 与镜像构建验证
- 验证 `backend-api`、`db-scheduler`、`web-console`、`debug-console` 容器联调
- 流水线侧接入 `update_processing_stage` 需单独跟进
- 继续优化部署产物与运行时资源占用

## 最后更新

2026-03-27
