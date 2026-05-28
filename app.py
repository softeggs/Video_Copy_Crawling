from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st
from sqlalchemy import func, or_, select

from backend.constants import COMPLETED_STATUS, FAILED_STATUS, PENDING_STATUS, PROCESSING_STATUS
from backend.database import DATABASE_URL, SessionLocal
from backend.models import User, Video
from core.db_scheduler import DatabaseScheduler, DatabaseWritebackAdapter
from utils.config import config

st.set_page_config(page_title="内部调试台", page_icon="🛠️", layout="wide")


def fetch_backend_health() -> dict[str, Any]:
    """读取当前配置指向的后端健康状态。"""

    url = f"{config.API_BASE_URL}/health"
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=2) as response:  # noqa: S310 - 本地固定调试地址
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return {"status": "http_error", "detail": str(exc), "url": url}
    except URLError as exc:
        return {"status": "offline", "detail": str(exc), "url": url}
    except Exception as exc:  # noqa: BLE001 - 调试台需要完整兜底
        return {"status": "error", "detail": str(exc), "url": url}


def get_dashboard_snapshot() -> dict[str, Any]:
    """读取数据库摘要。"""

    with SessionLocal() as session:
        total_users = session.execute(select(func.count(User.id))).scalar_one()
        active_users = session.execute(select(func.count(User.id)).where(User.is_active.is_(True))).scalar_one()
        total_videos = session.execute(select(func.count(Video.id))).scalar_one()
        pending_videos = session.execute(
            select(func.count(Video.id)).where(Video.status.in_((PENDING_STATUS, PROCESSING_STATUS)))
        ).scalar_one()
        status_rows = session.execute(select(Video.status, func.count(Video.id)).group_by(Video.status)).all()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_videos": total_videos,
        "pending_videos": pending_videos,
        "status_counts": {status: count for status, count in status_rows},
    }


def list_users(limit: int = 20, keyword: str = "") -> list[dict[str, Any]]:
    """按关键字查询用户明细。"""

    with SessionLocal() as session:
        stmt = select(User)
        if keyword.strip():
            like = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(User.username.like(like), User.email.like(like), User.display_name.like(like))
            )
        users = session.execute(stmt.order_by(User.created_at.desc(), User.id.desc()).limit(limit)).scalars().all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "table_id": user.table_id,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat(),
        }
        for user in users
    ]


def list_videos(limit: int = 30, keyword: str = "", status_filter: str = "全部") -> list[dict[str, Any]]:
    """按状态和关键字查询视频明细。"""

    with SessionLocal() as session:
        stmt = select(Video)

        if status_filter != "全部":
            stmt = stmt.where(Video.status == status_filter)

        if keyword.strip():
            like = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    Video.title.like(like),
                    Video.author.like(like),
                    Video.url.like(like),
                    Video.error_msg.like(like),
                )
            )

        videos = session.execute(stmt.order_by(Video.created_at.desc(), Video.id.desc()).limit(limit)).scalars().all()

    return [
        {
            "id": video.id,
            "user_id": video.user_id,
            "title": video.title or "未命名视频",
            "author": video.author or "未知作者",
            "video_type": video.video_type,
            "status": video.status,
            "url": video.url,
            "summary": video.summary,
            "created_at": video.created_at.isoformat(),
            "processed_at": video.processed_at.isoformat() if video.processed_at else "",
            "error_msg": video.error_msg,
        }
        for video in videos
    ]


def get_user_detail(user_id: int) -> dict[str, Any] | None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user is None:
            return None

        video_count = session.execute(select(func.count(Video.id)).where(Video.user_id == user.id)).scalar_one()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "table_id": user.table_id,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat(),
            "video_count": video_count,
        }


def list_failed_videos(limit: int = 20) -> list[dict[str, Any]]:
    """专门聚合最近失败任务，降低在全量明细里排障的成本。"""

    with SessionLocal() as session:
        videos = (
            session.execute(
                select(Video)
                .where(Video.status == FAILED_STATUS)
                .order_by(Video.processed_at.desc(), Video.created_at.desc(), Video.id.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )

    return [
        {
            "id": video.id,
            "user_id": video.user_id,
            "title": video.title or "未命名视频",
            "status": video.status,
            "video_type": video.video_type,
            "url": video.url,
            "error_msg": video.error_msg or "未写入错误信息",
            "created_at": video.created_at.isoformat(),
            "processed_at": video.processed_at.isoformat() if video.processed_at else "",
        }
        for video in videos
    ]


def get_failed_error_summary(limit: int = 20) -> list[dict[str, Any]]:
    """按错误原因汇总失败任务，便于判断是否为同类问题批量出现。"""

    with SessionLocal() as session:
        rows = session.execute(
            select(Video.error_msg, func.count(Video.id))
            .where(Video.status == FAILED_STATUS)
            .group_by(Video.error_msg)
            .order_by(func.count(Video.id).desc(), Video.error_msg.asc())
            .limit(limit)
        ).all()

    return [
        {
            "error_msg": error_msg or "未写入错误信息",
            "count": count,
        }
        for error_msg, count in rows
    ]


def get_video_detail(video_id: int) -> dict[str, Any] | None:
    with SessionLocal() as session:
        video = session.get(Video, video_id)
        if video is None:
            return None

        return {
            "id": video.id,
            "user_id": video.user_id,
            "url": video.url,
            "title": video.title,
            "author": video.author,
            "summary": video.summary,
            "core_points": video.core_points,
            "corrected_text": video.corrected_text,
            "golden_sentences": video.golden_sentences,
            "tags": video.tags,
            "video_type": video.video_type,
            "status": video.status,
            "markdown_content": video.markdown_content,
            "error_msg": video.error_msg,
            "created_at": video.created_at.isoformat(),
            "processed_at": video.processed_at.isoformat() if video.processed_at else None,
        }


async def _pipeline_processor(url: str) -> dict[str, Any]:
    """复用现有流水线处理数据库中的任务。"""

    from core.pipeline import ProcessingPipeline

    pipeline = ProcessingPipeline(
        ai_provider=config.AI_PROVIDER,
        enable_ai_polish=config.ENABLE_AI_POLISH,
        whisper_model=config.WHISPER_MODEL,
    )
    return await pipeline.process(url, progress_callback=None, skip_feishu_sync=False)


def run_scheduler_once(batch_size: int) -> dict[str, int]:
    # 调试台默认只依赖数据库与后端查询；真正触发流水线时再按需导入重依赖，
    # 这样可以把日常运维镜像与 AI/Whisper/下载栈解耦。
    adapter = DatabaseWritebackAdapter(session_factory=SessionLocal)
    scheduler = DatabaseScheduler(
        adapter=adapter,
        processor=_pipeline_processor,
        recover_timeout_seconds=config.DB_SCHEDULER_RECOVER_TIMEOUT,
    )
    return asyncio.run(scheduler.run_once(batch_size=batch_size))


def render_status_counts(status_counts: dict[str, int]) -> None:
    ordered = [
        (PENDING_STATUS, status_counts.get(PENDING_STATUS, 0)),
        (PROCESSING_STATUS, status_counts.get(PROCESSING_STATUS, 0)),
        (COMPLETED_STATUS, status_counts.get(COMPLETED_STATUS, 0)),
        (FAILED_STATUS, status_counts.get(FAILED_STATUS, 0)),
    ]
    st.table([{"状态": name, "数量": count} for name, count in ordered])


st.title("🛠️ 内部调试台")
st.caption("当前页面仅面向本地开发和排障使用，用于检查后端、数据库、任务执行和环境配置。")

health = fetch_backend_health()
snapshot = get_dashboard_snapshot()

overview_tab, database_tab, operations_tab, env_tab = st.tabs(["系统概览", "数据库明细", "任务触发", "环境配置"])

with overview_tab:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总用户数", snapshot["total_users"], help="数据库中的用户总量")
    col2.metric("活跃用户", snapshot["active_users"], help="当前 `is_active = true` 的用户数量")
    col3.metric("总视频数", snapshot["total_videos"], help="数据库中的视频记录总量")
    col4.metric("待处理任务", snapshot["pending_videos"], help="状态为待处理或处理中")

    st.subheader("后端健康状态")
    st.json(health)

    st.subheader("任务状态分布")
    render_status_counts(snapshot["status_counts"])

with database_tab:
    st.subheader("数据库明细查看")
    st.caption("这里直接读取当前数据库，不依赖前端页面，适合确认用户、视频和错误信息是否真实入库。")

    user_keyword_col, user_limit_col = st.columns([3, 1])
    user_keyword = user_keyword_col.text_input("用户检索关键词", placeholder="用户名 / 邮箱 / 显示名")
    user_limit = user_limit_col.number_input("用户数量", min_value=5, max_value=100, value=20)
    st.dataframe(list_users(limit=int(user_limit), keyword=user_keyword), use_container_width=True)

    with st.expander("查看单个用户原始详情"):
        user_detail_id = st.number_input("输入用户 ID", min_value=1, step=1, value=1, key="user_detail_id")
        if st.button("查询用户详情", key="query_user_detail"):
            user_detail = get_user_detail(int(user_detail_id))
            if user_detail is None:
                st.warning("未找到对应的用户记录。")
            else:
                st.json(user_detail)

    st.divider()

    video_keyword_col, video_status_col, video_limit_col = st.columns([3, 2, 1])
    video_keyword = video_keyword_col.text_input("视频检索关键词", placeholder="标题 / 作者 / URL / 错误信息")
    video_status = video_status_col.selectbox(
        "视频状态筛选",
        options=["全部", PENDING_STATUS, PROCESSING_STATUS, COMPLETED_STATUS, FAILED_STATUS],
        index=0,
    )
    video_limit = video_limit_col.number_input("视频数量", min_value=5, max_value=200, value=30)
    st.dataframe(
        list_videos(limit=int(video_limit), keyword=video_keyword, status_filter=video_status),
        use_container_width=True,
    )

    with st.expander("查看单个视频原始详情"):
        video_detail_id = st.number_input("输入视频 ID", min_value=1, step=1, value=1, key="video_detail_id")
        if st.button("查询视频详情", key="query_video_detail"):
            video_detail = get_video_detail(int(video_detail_id))
            if video_detail is None:
                st.warning("未找到对应的视频记录。")
            else:
                st.json(video_detail)

with operations_tab:
    st.subheader("手动触发数据库调度")
    st.write("该操作会认领数据库中的待处理视频，并调用现有 `core.pipeline` 执行完整处理。")

    batch_size = st.number_input("本次处理批量大小", min_value=1, max_value=20, value=config.DB_SCHEDULER_BATCH_SIZE)

    if "last_scheduler_result" not in st.session_state:
        st.session_state.last_scheduler_result = None

    if st.button("执行一次调度", type="primary"):
        with st.spinner("正在执行数据库调度..."):
            st.session_state.last_scheduler_result = run_scheduler_once(batch_size=int(batch_size))

    if st.session_state.last_scheduler_result:
        st.success("调度已完成")
        st.json(st.session_state.last_scheduler_result)

    st.subheader("当前数据库状态快照")
    render_status_counts(get_dashboard_snapshot()["status_counts"])

    st.divider()
    st.subheader("失败任务排障视图")
    st.caption("集中查看最近失败任务、错误原因分布和单条失败详情，避免在全量明细里人工筛查。")

    failed_limit_col, failed_detail_col = st.columns([1, 1])
    failed_limit = failed_limit_col.number_input("最近失败任务数量", min_value=5, max_value=100, value=20)
    failed_detail_id = failed_detail_col.number_input(
        "失败任务 ID",
        min_value=1,
        step=1,
        value=1,
        key="failed_video_detail_id",
    )

    failed_videos = list_failed_videos(limit=int(failed_limit))
    failed_error_summary = get_failed_error_summary()

    failed_table_col, failed_summary_col = st.columns([2, 1])

    with failed_table_col:
        if failed_videos:
            st.dataframe(failed_videos, use_container_width=True)
        else:
            st.info("当前没有失败任务，最近调度结果比较稳定。")

    with failed_summary_col:
        st.markdown("**高频错误汇总**")
        if failed_error_summary:
            st.dataframe(failed_error_summary, use_container_width=True, hide_index=True)
        else:
            st.success("当前没有可统计的失败错误。")

    if st.button("查询失败任务详情", key="query_failed_video_detail"):
        failed_detail = get_video_detail(int(failed_detail_id))
        if failed_detail is None:
            st.warning("未找到对应的视频记录。")
        elif failed_detail["status"] != FAILED_STATUS:
            st.info("该 ID 当前不是失败状态，以下仍展示原始详情供核对。")
            st.json(failed_detail)
        else:
            # 单独高亮错误原因，避免在长 JSON 中不易发现真正的失败入口。
            st.error(f"错误信息：{failed_detail['error_msg'] or '未写入错误信息'}")
            st.json(failed_detail)

with env_tab:
    st.subheader("当前运行配置")
    st.code(
        "\n".join(
            [
                f"API_BASE_URL={config.API_BASE_URL}",
                f"DATABASE_URL={DATABASE_URL}",
                f"WHISPER_MODEL={config.WHISPER_MODEL}",
                f"AI_PROVIDER={config.AI_PROVIDER}",
                f"ENABLE_AI_POLISH={config.ENABLE_AI_POLISH}",
                f"FEISHU_ENABLED={bool(config.FEISHU_APP_ID and config.FEISHU_APP_SECRET)}",
                f"DB_SCHEDULER_BATCH_SIZE={config.DB_SCHEDULER_BATCH_SIZE}",
            ]
        ),
        language="text",
    )

    st.subheader("第三方配置状态")
    st.table(
        [
            {"配置项": "OpenAI", "状态": "已配置" if config.OPENAI_API_KEY else "未配置"},
            {"配置项": "Gemini", "状态": "已配置" if config.GEMINI_API_KEY else "未配置"},
            {"配置项": "Kimi", "状态": "已配置" if config.KIMI_API_KEY else "未配置"},
            {"配置项": "飞书", "状态": "已配置" if config.FEISHU_APP_ID and config.FEISHU_APP_SECRET else "未配置"},
        ]
    )
