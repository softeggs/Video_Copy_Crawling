# P7 本地部署演练落地任务

- 所属模块：backend-server
- 所属阶段：P7 服务器迁移准备
- 当前状态：开发中
- 最后更新：2026-05-28
- 回链：`status/MASTER_STATUS.md`

## 背景与目标

当前统一后端、Streamlit 正式入口与调试台都已可本地手动运行，但仓库缺少可复制的部署资产。P7 第一阶段目标不是上云，而是补齐 Docker 化演练资产，让后续接入真实服务器时只需要替换机器参数和密钥。

## 已完成

- 已确定第一阶段范围：`SQLite + FastAPI + db-scheduler + Streamlit 用户端 + 调试台`
- 已新增数据库调度常驻入口 `scripts/run_db_scheduler.py`
- 已补镜像构建资产 `Dockerfile`
- 已补编排资产 `docker-compose.yml`
- 已补 Nginx 反向代理配置
- 已补 `.env.deploy.example`
- 已补本地部署演练文档 `docs/P7_LOCAL_DEPLOYMENT.md`
- 已通过 `docker compose config`
- 已完成 `backend-api` 镜像构建
- 已完成 `db-scheduler` 镜像重建并切换到 DeepSeek 配置
- 已完成 `docker compose up -d`
- 已确认 `backend-api`、`web-console`、`debug-console`、`db-scheduler`、`reverse-proxy` 全部启动
- 已验证注册 / 登录 / 提交视频接口在容器环境下可用
- 已验证数据库调度器可认领任务并将未知平台链接写回为失败状态
- 已验证 DeepSeek 在容器环境下成功完成 AI 润色
- 已验证抖音真实链接成功写回飞书，飞书记录 ID：`recvkTEMvRWG0T`

## 未完成

- 收敛当前部署镜像体积
- 输出真实服务器接入参数

## 验收标准

- 仓库内存在完整部署资产
- `db-scheduler` 不依赖调试台可独立运行
- 用户端、调试台、后端、调度器具备明确启动命令
- 本地部署文档可直接指导演练

## 下一步建议

1. 先做 Compose 配置校验
2. 再做镜像构建验证
3. 最后做容器联调验收并回写状态中心
