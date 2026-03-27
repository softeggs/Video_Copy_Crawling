"""提交视频页面。"""

from __future__ import annotations

import streamlit as st

from web.api_client import APIError, api_client
from web.auth import logout, require_auth

require_auth()

# ---- 顶部导航 ----
col_logo, col_user, col_logout = st.columns([3, 6, 1])
with col_logo:
    st.title("➕ 提交视频")
with col_user:
    display_name = st.session_state.user.get("display_name", st.session_state.user.get("username", ""))
    st.markdown(f"<div style='text-align:right; line-height:60px; color:#888;'>欢迎，{display_name}</div>", unsafe_allow_html=True)
with col_logout:
    if st.button("退出登录", use_container_width=True):
        logout()
        st.rerun()

st.divider()

# ---- 快捷导航 ----
nav_cols = st.columns(3)
nav_labels = ["📊 仪表盘", "📋 历史记录", "🔑 密钥管理"]
nav_pages = ["仪表盘", "历史记录", "密钥管理"]
for i, label in enumerate(nav_labels):
    if nav_cols[i].button(label, use_container_width=True):
        st.session_state.page = nav_pages[i]
        st.rerun()

st.divider()

# ---- 提交表单 ----
st.subheader("提交新视频")
st.caption("支持抖音、B站等主流视频平台链接。提交后自动排队处理。")

url_input = st.text_input("视频链接", placeholder="https://www.douyin.com/video/xxxx 或 https://www.bilibili.com/video/xxxx", key="submit_url")

submitted = st.button("🚀 提交", type="primary", use_container_width=True)

if submitted:
    if not url_input.strip():
        st.warning("请输入视频链接。")
    else:
        with st.spinner("正在提交..."):
            try:
                resp = api_client.submit_video(url_input.strip())
                if resp.success:
                    st.success(f"提交成功！记录 ID：`{resp.record_id}`，预计 {resp.estimated_time or '2-5分钟'} 完成。")
                    if resp.message:
                        st.info(resp.message)
                    st.session_state.submitted_url = url_input.strip()
                    st.session_state.submitted_id = resp.record_id
                else:
                    st.error(f"提交失败：{resp.message or '未知错误'}")
            except APIError as exc:
                if exc.status_code == 401:
                    logout()
                    st.rerun()
                st.error(f"提交失败：{exc.message}")

# ---- 提交历史提示 ----
if st.session_state.get("submitted_id"):
    st.info(f"上次提交：{st.session_state.submitted_url} → 记录 ID `{st.session_state.submitted_id}`。可在历史记录中查看处理状态。")

# ---- 快捷指令提交入口 ----
st.divider()
st.subheader("🔗 快捷指令提交")
st.caption("使用快捷指令密钥，无需登录即可提交视频链接（适用于自动化工作流）。")

sc_key = st.text_input("快捷指令密钥", placeholder="粘贴您保存的密钥字符串", type="password", key="sc_key_input")
sc_url = st.text_input("视频链接（快捷方式）", placeholder="视频链接", key="sc_url_input")

if st.button("⚡ 快捷提交", use_container_width=True):
    if not sc_key.strip() or not sc_url.strip():
        st.warning("请填写密钥和视频链接。")
    else:
        try:
            resp = api_client.shortcut_submit(sc_key.strip(), sc_url.strip())
            if resp.success:
                st.success(f"提交成功！记录 ID：`{resp.record_id}`，预计 {resp.estimated_time or '2-5分钟'} 完成。")
            else:
                st.error(f"快捷提交失败：{resp.message or '密钥无效或已被吊销'}")
        except APIError as exc:
            st.error(f"快捷提交失败：{exc.message}")
