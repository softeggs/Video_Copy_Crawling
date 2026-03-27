"""仪表盘 — 展示整体数据概览。"""

from __future__ import annotations

import streamlit as st

from web.api_client import APIError, api_client
from web.auth import logout, require_auth

require_auth()

# ---- 顶部导航 ----
col_logo, col_user, col_logout = st.columns([3, 6, 1])
with col_logo:
    st.title("📊 仪表盘")
with col_user:
    display_name = st.session_state.user.get("display_name", st.session_state.user.get("username", ""))
    st.markdown(f"<div style='text-align:right; line-height:60px; color:#888;'>欢迎，{display_name}</div>", unsafe_allow_html=True)
with col_logout:
    if st.button("退出登录", use_container_width=True):
        logout()
        st.rerun()

st.divider()

# ---- 快捷导航 ----
nav_cols = st.columns(4)
nav_labels = ["📋 历史记录", "➕ 提交视频", "🔑 密钥管理"]
nav_pages = ["历史记录", "提交视频", "密钥管理"]
for i, label in enumerate(nav_labels):
    if nav_cols[i].button(label, use_container_width=True):
        st.session_state.page = nav_pages[i]
        st.rerun()

st.divider()

# ---- 概览数据 ----
try:
    overview = api_client.get_overview()
    stats = api_client.get_stats()

    col_total, col_today, col_pending, col_completed = st.columns(4)
    col_total.metric("总记录数", overview.total, help="累计已提交的视频总数")
    col_today.metric("今日提交", overview.today, help="今天提交的视频数量")
    col_pending.metric("处理中", overview.pending, help="当前处于待处理或处理中的任务数量")
    completed = overview.total - overview.pending
    col_completed.metric("已完成", completed, help="处理完成的视频数量")

    if stats:
        st.subheader("📈 各类型统计")
        st.dataframe(
            [{"视频类型": s.video_type, "数量": s.count} for s in stats],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("暂无统计数据，提交视频后会自动统计。")

except APIError as exc:
    if exc.status_code == 401:
        st.warning("会话已过期，请重新登录。")
        logout()
        st.rerun()
    else:
        st.error(f"加载失败：{exc.message}")
