# P7 本地部署演练指南

## 目标

本指南用于完成 P7 第一阶段的本地部署演练，范围仅覆盖：

- `backend-api`：FastAPI 统一后端
- `db-scheduler`：数据库调度常驻服务
- `web-console`：`web_main.py` 正式用户入口
- `debug-console`：`app.py` 内部调试台
- `reverse-proxy`：Nginx 反向代理

本轮不包含：

- React `web_app`
- MySQL / PostgreSQL
- 真实线上域名与 HTTPS
- 云主机接入

## 目录与资产

- 镜像构建：`Dockerfile`
- 编排入口：`docker-compose.yml`
- 运行配置模板：`.env.deploy.example`
- 反向代理配置：`deploy/nginx/default.conf`
- 调度器入口：`scripts/run_db_scheduler.py`
- 健康检查脚本：`scripts/http_healthcheck.py`

## 首次初始化

1. 复制部署环境文件：

```powershell
Copy-Item .env.deploy.example .env.deploy
```

2. 按需修改 `.env.deploy` 中的以下关键项：

- `JWT_SECRET`
- `OPENAI_API_KEY` / `GEMINI_API_KEY` / `KIMI_API_KEY`
- `FEISHU_*`
- `COOKIES_FILE`

3. 确保本地存在以下目录或文件：

- `data/`
- `downloads/`
- `outputs/`
- `logs/`
- `cookies.txt`

如果 `data/` 不存在，Docker 挂载时会自动创建。

## 启动步骤

1. 构建全部镜像：

```powershell
docker compose build
```

2. 启动整套服务：

```powershell
docker compose up -d
```

3. 查看服务状态：

```powershell
docker compose ps
```

## 访问入口

- 正式用户端：`http://127.0.0.1:8080`
- 内部调试台：`http://127.0.0.1:8081`
- 后端 API：`http://127.0.0.1:8002`
- 健康检查：`http://127.0.0.1:8002/health`

说明：

- 当前 Nginx 采用双端口转发，避免把 Streamlit 调试台塞到 `/debug` 子路径导致前端静态资源和 websocket 行为不稳定。
- `web-console` 与 `debug-console` 在容器内都会通过 `API_BASE_URL=http://backend-api:8002` 访问后端。

## 健康检查与验收

### 1. 基础健康检查

```powershell
python scripts/http_healthcheck.py http://127.0.0.1:8002/health
python scripts/http_healthcheck.py http://127.0.0.1:8080/_stcore/health
python scripts/http_healthcheck.py http://127.0.0.1:8081/_stcore/health
```

说明：

- 如果你经由 Nginx 访问 Streamlit，`_stcore/health` 是否透传取决于代理行为。
- 当上述 URL 不稳定时，以 `docker compose ps` 和容器日志为准。

### 2. 业务验收顺序

1. 打开 `http://127.0.0.1:8080`
2. 完成注册 / 登录
3. 提交一条合法视频 URL
4. 打开 `http://127.0.0.1:8081` 查看数据库摘要与任务状态
5. 观察 `db-scheduler` 日志，确认待处理记录被认领并回写成功或失败
6. 回到用户端验证历史记录、概览和快捷指令密钥管理页面

### 3. 调度器验收

查看调度器日志：

```powershell
docker compose logs -f db-scheduler
```

验收重点：

- 能持续轮询数据库
- 能在异常后继续下一轮
- 不依赖 `app.py` 手动触发

## 停止、重启与日志

停止：

```powershell
docker compose down
```

停止但保留容器：

```powershell
docker compose stop
```

重启某个服务：

```powershell
docker compose restart backend-api
docker compose restart db-scheduler
docker compose restart web-console
docker compose restart debug-console
```

查看日志：

```powershell
docker compose logs -f backend-api
docker compose logs -f db-scheduler
docker compose logs -f web-console
docker compose logs -f debug-console
docker compose logs -f reverse-proxy
```

## 常见故障排查

### 1. `backend-api` 起不来

重点检查：

- `.env.deploy` 是否存在
- `JWT_SECRET` 是否为空
- `DATABASE_URL` 是否指向可写路径
- `requirements.deploy.txt` 中依赖是否成功安装

### 2. `web-console` / `debug-console` 无法访问

重点检查：

- `backend-api` 是否先健康
- `API_BASE_URL` 是否仍指向 `backend-api:8002`
- Nginx 是否成功启动
- `docker compose logs -f reverse-proxy`

### 3. `db-scheduler` 没有处理记录

重点检查：

- 数据库里是否存在 `status=待处理` 的记录
- AI / 飞书配置是否缺失
- `downloads/`、`outputs/`、`logs/` 目录是否可写
- `docker compose logs -f db-scheduler`

### 4. 容器重启后数据丢失

重点检查：

- 是否误删 `data/`、`downloads/`、`outputs/`
- `DATABASE_URL` 是否仍指向 `/app/data/local_dev.sqlite3`
- Compose 卷挂载路径是否被改动

## 回滚方式

本轮没有数据库类型切换，也没有正式线上发布，因此回滚以“恢复到本地手动运行方式”为主：

1. `docker compose down`
2. 保留 `data/`、`downloads/`、`outputs/`、`logs/`
3. 改回本地命令启动：

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8002
streamlit run web_main.py --server.port 8501 --server.address 0.0.0.0
streamlit run app.py --server.port 8502 --server.address 0.0.0.0
python -m scripts.run_db_scheduler
```

## 第二阶段线上迁移前置清单

上线真实服务器前，需要补齐以下信息：

- 云主机 SSH / 登录方式
- 公网 IP 或域名
- HTTPS 证书方案
- 服务器操作系统版本
- Docker / Docker Compose 可用性
- 持久化磁盘路径
- 防火墙 / 安全组放行端口
- 线上 `.env` 注入方式
- Cookies / 密钥文件存放策略

## 备注

当前仓库中的 `scheduler_app.py` 和 `core/scheduler.py` 仍服务旧飞书轮询链路；P7 第一阶段新增的是数据库调度常驻服务，不替换旧链路，只为统一后端部署闭环补足后台处理能力。
