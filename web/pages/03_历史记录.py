"""历史记录页面 — 展示所有视频记录，支持删除、收藏、状态轮询。"""

from __future__ import annotations

import time

import streamlit as st

from web.api_client import APIError, api_client
from web.auth import logout, require_auth
from web.constants import PENDING_LIKE_STATUSES, STAGE_LABELS

require_auth()

# ---- 顶部导航 ----
col_logo, col_user, col_logout = st.columns([3, 6, 1])
with col_logo:
    st.title("📋 历史记录")
with col_user:
    display_name = st.session_state.user.get("display_name", st.session_state.user.get("username", ""))
    st.markdown(f"<div style='text-align:right; line-height:60px; color:#888;'>欢迎，{display_name}</div>", unsafe_allow_html=True)
with col_logout:
    if st.button("退出登录", use_container_width=True):
        logout()
        st.rerun()

st.divider()

# ---- 过滤器 ----
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([3, 2, 1, 1])
keyword = filter_col1.text_input("搜索关键词", placeholder="标题 / 作者 / 标签 / 摘要...", key="history_keyword")
status_filter = filter_col2.selectbox(
    "状态筛选",
    options=["全部", "待处理", "处理中", "已完成", "失败"],
    index=0,
    key="history_status",
)
page_num = filter_col3.number_input("页码", min_value=1, value=1, key="history_page")
auto_refresh = filter_col4.checkbox("自动刷新 (5s)", value=False, key="history_auto_refresh")

if auto_refresh:
    time.sleep(5)
    st.rerun()

# 映射筛选值
status_map = {"待处理": "待处理", "处理中": "处理中", "已完成": "已完成", "失败": "失败"}
api_status = status_map.get(status_filter, None)

# ---- 加载数据 ----
try:
    resp = api_client.get_videos(page=int(page_num), page_size=20, status=api_status)
    videos = resp.items

    # 前端关键词过滤（分页后本地过滤，避免过度请求）
    if keyword.strip():
        kw = keyword.strip().lower()
        videos = [
            v
            for v in videos
            if kw
            in (
                f"{v.title} {v.author} {v.summary} {' '.join(v.tags)} {' '.join(v.core_points)}"
            ).lower()
        ]

    st.caption(f"第 {resp.page} 页，共约 {resp.total} 条记录 {'(有更多)' if resp.has_more else ''}")
except APIError as exc:
    if exc.status_code == 401:
        logout()
        st.rerun()
    st.error(f"加载失败：{exc.message}")
    videos = []

# ---- 视频列表 ----
if not videos:
    st.info("暂无记录。")
else:
    for video in videos:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])

            # 状态徽章
            stage_label = STAGE_LABELS.get(video.processing_stage, "")
            if video.status in PENDING_LIKE_STATUSES and stage_label:
                status_badge = f"🔄 {video.status} · {stage_label}"
            elif video.status == "已完成":
                status_badge = "✅ 已完成"
            elif video.status == "失败":
                status_badge = "❌ 失败"
            else:
                status_badge = f"⏳ {video.status}"

            with col1:
                fav_icon = "⭐" if video.is_favorited else "☆"
                st.markdown(f"## {fav_icon}")
            with col2:
                st.markdown(f"**{video.title}**")
                st.caption(f"👤 {video.author} · {video.video_type}")
                if video.processing_detail:
                    st.caption(f"📍 {video.processing_detail}")
                if video.tags:
                    st.caption("🏷️ " + " ".join(f"`{t}`" for t in video.tags[:4]))
            with col3:
                st.write(status_badge)
                if video.estimated_seconds_remaining:
                    st.caption(f"⏱️ {video.estimated_seconds_remaining}s")

            # 操作按钮
            with col4:
                new_fav = not video.is_favorited
                fav_label = "取消收藏" if video.is_favorited else "⭐ 收藏"
                if st.button(fav_label, key=f"fav_{video.id}", use_container_width=True):
                    try:
                        api_client.toggle_favorite(video.id, new_fav)
                        st.rerun()
                    except APIError as exc:
                        st.error(f"操作失败：{exc.message}")

            with col5:
                del_key = f"del_confirm_{video.id}"
                if st.session_state.get(del_key, False):
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("确认", key=f"del_yes_{video.id}", use_container_width=True):
                            try:
                                api_client.delete_video(video.id)
                                st.success("已删除")
                                st.rerun()
                            except APIError as exc:
                                st.error(f"删除失败：{exc.message}")
                    with col_no:
                        if st.button("取消", key=f"del_no_{video.id}", use_container_width=True):
                            st.session_state[del_key] = False
                            st.rerun()
                else:
                    if st.button("🗑️ 删除", key=f"del_{video.id}", use_container_width=True):
                        st.session_state[del_key] = True
                        st.rerun()

            # 详情展开
            with st.expander("查看详情"):
                if video.url:
                    st.markdown(f"🔗 [打开链接]({video.url})")
                if video.summary:
                    st.markdown(f"**摘要：** {video.summary}")
                if video.core_points:
                    st.markdown("**核心观点：**")
                    for pt in video.core_points:
                        st.markdown(f"- {pt}")
                if video.golden_sentences:
                    st.markdown("**金句：**")
                    for gs in video.golden_sentences:
                        st.markdown(f"> {gs}")
                if video.corrected_text:
                    st.markdown("**详细内容：**")
                    st.text(video.corrected_text[:500] + ("..." if len(video.corrected_text) > 500 else ""))
                if video.markdown_content:
                    st.markdown(f"**Markdown：** `{video.markdown_content}`")
                if video.last_stage_update_at:
                    st.caption(f"最后更新：{video.last_stage_update_at}")

            st.divider()
