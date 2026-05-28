# 发布结构设计

## 目标

本文件定义统一后端项目的持续发布结构，覆盖：

- 本地开发部署
- `staging` 验证环境
- `production` 正式环境
- 镜像版本管理
- 发布步骤
- 回滚步骤
- smoke check

不覆盖：

- Kubernetes
- 灰度发布平台
- iOS App 发版流程

## 环境分层

### 1. 本地环境

- 入口文件：`docker-compose.yml`
- 环境文件：`.env.deploy`
- 用途：开发联调、故障复现、本地部署演练

### 2. Staging 环境

- 入口文件：`docker-compose.staging.yml`
- 环境文件：`.env.staging`
- 用途：上线前验证镜像、迁移、配置、接口和 smoke test

### 3. Production 环境

- 入口文件：`docker-compose.production.yml`
- 环境文件：`.env.production`
- 用途：正式对外服务

## 镜像分层

### 当前镜像职责

- `backend-api`
  - 提供认证、视频记录、管理、快捷指令接口
- `db-scheduler`
  - 承载下载、转写、DeepSeek 润色、飞书写回
- `web-console`
  - 正式 Streamlit 用户入口
- `debug-console`
  - 内部运维调试入口

### 镜像 tag 规则

禁止只使用 `latest` 作为正式发布标识。

推荐格式：

- `v0.1.0`
- `v0.1.1`
- `v0.2.0`

如果有 staging 验证，可再加：

- `staging-v0.1.1`

## 目录与文件职责

- `docker-compose.yml`
  - 本地默认运行结构，保留 `build`
- `docker-compose.staging.yml`
  - Staging 独立入口，使用固定镜像 tag，不走本地 build
- `docker-compose.production.yml`
  - Production 独立入口，使用正式镜像 tag，不走本地 build
- `.env.staging.example`
  - staging 环境模板
- `.env.production.example`
  - production 环境模板
- `deploy/nginx/staging.conf`
  - staging 反向代理模板
- `deploy/nginx/production.conf`
  - production 反向代理模板
- `scripts/release_smoke_check.py`
  - 发布后 smoke check 脚本

## 发布流程

### Staging 发布

1. 本地完成代码验证
2. 构建镜像并打版本 tag
3. 推送镜像到仓库
4. 在 staging 服务器准备 `.env.staging`
5. 执行：

```bash
docker compose --env-file .env.staging -f docker-compose.staging.yml pull
docker compose --env-file .env.staging -f docker-compose.staging.yml up -d
```

6. 执行 smoke check：

```bash
python scripts/release_smoke_check.py \
  http://127.0.0.1:18002/health \
  http://127.0.0.1:18080 \
  http://127.0.0.1:18081
```

7. 验证真实抖音链接处理和飞书写回

### Production 发布

1. staging 验证通过
2. 固定正式镜像 tag
3. 在 production 服务器准备 `.env.production`
4. 先备份数据库和关键目录
5. 执行：

```bash
docker compose --env-file .env.production -f docker-compose.production.yml pull
docker compose --env-file .env.production -f docker-compose.production.yml up -d
```

6. 执行 smoke check：

```bash
python scripts/release_smoke_check.py \
  http://127.0.0.1:8002/health \
  http://127.0.0.1:8080 \
  http://127.0.0.1:8081
```

7. 验证真实任务写回

## 数据库迁移规则

只要存在 schema 变化，必须：

1. 写 Alembic migration
2. 先在 staging 跑迁移
3. staging 验证通过后再进 production

禁止把生产发布建立在手工 `ALTER TABLE` 之上。

## 回滚规则

### 无 schema 变化

直接回滚到上一个镜像 tag：

1. 修改 `.env.staging` 或 `.env.production` 中的镜像 tag
2. 执行 `docker compose up -d`

### 有 schema 变化

必须区分：

- 镜像可回滚
- 数据库是否可回滚

如果 migration 不可逆，必须在发布前先做数据库备份。

## Smoke Check 基线

发布后至少检查：

- 后端健康检查
- Web 正式入口
- Debug 调试台
- 登录
- 提交视频
- 调度器日志
- 飞书写回

## 服务器迁移前置输入

真正进入服务器迁移前，需要准备：

- SSH 登录方式
- 服务器 OS
- Docker / Docker Compose 可用性
- 域名或公网 IP
- HTTPS 证书方案
- 持久化目录路径
- 防火墙 / 安全组端口
- 镜像仓库地址
- 生产环境密钥注入方式
