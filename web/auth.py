"""认证状态管理 — 封装登录/注册/登出操作，与 Streamlit session_state 绑定。"""

from __future__ import annotations

import streamlit as st

from web.api_client import APIError, api_client


def require_auth() -> None:
    """强制重定向未登录用户到登录页。"""

    if not st.session_state.get("logged_in"):
        st.warning("请先登录。")
        st.session_state.page = "登录"
        st.rerun()


def logout() -> None:
    """清除认证状态。"""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.user = None
    api_client.set_token(None)


def login(username: str, password: str) -> tuple[bool, str]:
    """登录，返回 (是否成功, 错误信息)。"""
    try:
        resp = api_client.login(username, password)
        st.session_state.logged_in = True
        st.session_state.token = resp.token
        st.session_state.user = {"username": resp.user.username, "display_name": resp.user.display_name}
        api_client.set_token(resp.token)
        return True, ""
    except APIError as exc:
        return False, exc.message


def register(username: str, email: str, display_name: str, password: str) -> tuple[bool, str]:
    """注册并登录，返回 (是否成功, 错误信息)。"""
    try:
        resp = api_client.register(username, email, display_name, password)
        st.session_state.logged_in = True
        st.session_state.token = resp.token
        st.session_state.user = {"username": resp.user.username, "display_name": resp.user.display_name}
        api_client.set_token(resp.token)
        return True, ""
    except APIError as exc:
        return False, exc.message
