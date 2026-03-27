# Web Console 模块

## 模块概述

Streamlit Web 前端，与后端 8002 强耦合，提供用户面向的功能页面。

## 技术选型

- **框架**：Streamlit 1.37+
- **路由**：`st.navigation` 多页面
- **API 层**：`web/api_client.py`（对标 iOS `APIService`）
- **认证**：Bearer Token 存于 `st.session_state`

## 页面清单

| 页面 | 文件 | 状态 |
|------|------|------|
| 登录 / 注册 | `pages/01_登录注册.py` | ✅ 已完成 |
| 仪表盘 | `pages/02_仪表盘.py` | ✅ 已完成 |
| 历史记录（含删除/收藏/状态） | `pages/03_历史记录.py` | ✅ 已完成 |
| 提交视频 | `pages/04_提交视频.py` | ✅ 已完成 |
| 快捷指令密钥管理 | `pages/05_快捷指令密钥管理.py` | ✅ 已完成 |

## 已接入的后端能力

| 后端能力 | 对应接口 | 接入页面 |
|----------|----------|----------|
| 用户认证 | `POST /auth/login` `POST /auth/register` | 登录注册页 |
| 仪表盘概览 | `GET /videos/overview` | 仪表盘页 |
| 分类统计 | `GET /videos/stats` | 仪表盘页 |
| 视频列表 | `GET /videos` | 历史记录页 |
| 视频详情 | `GET /videos/{id}` | 历史记录页（展开） |
| 删除记录 | `DELETE /videos/{id}` | 历史记录页 |
| 收藏切换 | `POST /videos/{id}/favorite` | 历史记录页 |
| 状态轮询 | `GET /videos/{id}/status` | 历史记录页（处理中展示） |
| 提交视频 | `POST /videos/submit` | 提交视频页 |
| 快捷提交 | `POST /shortcut-submit` | 提交视频页 |
| 密钥列表 | `GET /shortcut-keys` | 密钥管理页 |
| 生成密钥 | `POST /shortcut-keys` | 密钥管理页 |
| 吊销密钥 | `DELETE /shortcut-keys/{id}` | 密钥管理页 |

## 启动方式

```bash
streamlit run web_main.py
# 后端需先启动：uvicorn backend.main:app --port 8002 --reload
```

## 最后更新

2026-03-27

## 调试记录

- **2026-03-27**：首次启动时因 `videos` 表缺少 P3 新增字段（`is_favorited`、`processing_stage` 等）导致 Internal Server Error。直接通过 `ALTER TABLE` 手工修复，并将 Alembic 版本锚定至 `20260327_p3_new_fields`，无需重新执行迁移脚本。
- `shortcut_keys` 表在首次迁移前已由 SQLAlchemy `Base.metadata.create_all` 预建，需在 Alembic 标记时同步确认。
- Streamlit 多页面架构中，`st.set_page_config()` 必须在入口文件 `web_main.py` 中调用一次，子页面不得重复调用。
