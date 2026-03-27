"""登录与注册页面。"""

from __future__ import annotations

import streamlit as st

from web.auth import login, logout, register

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "登录"

# ---- 已登录状态 ----
if st.session_state.logged_in:
    st.success(f"已登录：{st.session_state.user.get('display_name', st.session_state.user.get('username', ''))}")
    if st.button("退出登录"):
        logout()
        st.rerun()
    st.stop()

# ---- 登录 / 注册切换 ----
tab_login, tab_register = st.tabs(["登录", "注册新账号"])

with tab_login:
    st.subheader("登录账号")
    username = st.text_input("用户名", placeholder="请输入用户名", key="login_username")
    password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")

    if st.button("登录", type="primary", use_container_width=True):
        if not username or not password:
            st.warning("请填写用户名和密码。")
        else:
            ok, err = login(username, password)
            if ok:
                st.success("登录成功！")
                st.rerun()
            else:
                st.error(f"登录失败：{err}")

    st.caption("提示：使用飞书对接时创建的账号登录。如未注册，请切换到「注册新账号」。")

with tab_register:
    st.subheader("注册新账号")
    new_username = st.text_input("用户名", placeholder="用于登录", key="reg_username")
    new_email = st.text_input("邮箱", placeholder="your@email.com", key="reg_email")
    new_display = st.text_input("显示名称", placeholder="在应用中显示的名称", key="reg_display")
    new_password = st.text_input("密码", type="password", placeholder="至少 6 位", key="reg_password")
    new_password2 = st.text_input("确认密码", type="password", placeholder="再次输入密码", key="reg_password2")

    if st.button("注册", type="primary", use_container_width=True):
        if not new_username or not new_email or not new_display or not new_password:
            st.warning("请填写所有字段。")
        elif new_password != new_password2:
            st.warning("两次输入的密码不一致。")
        elif len(new_password) < 6:
            st.warning("密码长度至少为 6 位。")
        else:
            ok, err = register(new_username, new_email, new_display, new_password)
            if ok:
                st.success("注册成功，已自动登录！")
                st.rerun()
            else:
                st.error(f"注册失败：{err}")
