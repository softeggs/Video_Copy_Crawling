"""Web 前端主入口 — Streamlit 多页面应用。"""

from __future__ import annotations

import streamlit as st

# 初始化 session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "登录"

st.set_page_config(page_title="视频智能助手", page_icon="🎬", layout="wide")

main_pages = [
    st.Page("web/pages/02_仪表盘.py", title="📊 仪表盘", default=True),
    st.Page("web/pages/03_历史记录.py", title="📋 历史记录"),
    st.Page("web/pages/04_提交视频.py", title="➕ 提交视频"),
    st.Page("web/pages/05_快捷指令密钥管理.py", title="🔑 密钥管理"),
]
auth_page = st.Page("web/pages/01_登录注册.py", title="登录 / 注册")

if st.session_state.get("logged_in"):
    selected = st.navigation(main_pages)
else:
    selected = st.navigation({"账号": [auth_page]})

selected.run()
