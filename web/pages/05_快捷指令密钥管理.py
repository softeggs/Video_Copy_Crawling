"""快捷指令密钥管理页面。"""

from __future__ import annotations

import streamlit as st

from web.api_client import APIError, api_client
from web.auth import logout, require_auth

require_auth()

# ---- 顶部导航 ----
col_logo, col_user, col_logout = st.columns([3, 6, 1])
with col_logo:
    st.title("🔑 快捷指令密钥管理")
with col_user:
    display_name = st.session_state.user.get("display_name", st.session_state.user.get("username", ""))
    st.markdown(f"<div style='text-align:right; line-height:60px; color:#888;'>欢迎，{display_name}</div>", unsafe_allow_html=True)
with col_logout:
    if st.button("退出登录", use_container_width=True):
        logout()
        st.rerun()

st.divider()

# ---- 说明卡片 ----
with st.expander("ℹ️ 什么是快捷指令密钥？", expanded=False):
    st.markdown(
        """
**快捷指令密钥**是一种免登录提交方式，适合自动化工作流：

1. 在下方「生成密钥」生成一个新的密钥
2. **密钥只显示一次**，请立即复制保存
3. 使用密钥可直接提交视频链接，无需账号密码
4. 如密钥泄露，可在下方「已生成的密钥」中吊销

> ⚠️ 密钥生成后服务端只保存哈希，无法找回明文，请妥善保管！
"""
    )

st.divider()

# ---- 生成新密钥 ----
st.subheader("➕ 生成新密钥")
key_name = st.text_input("密钥名称（可选）", placeholder="例如：自动化脚本、快捷指令等", key="new_key_name")

if st.button("🔑 生成密钥", type="primary", use_container_width=True):
    name = key_name.strip() or "快捷指令密钥"
    try:
        resp = api_client.create_shortcut_key(name)
        st.success("✅ 密钥已生成！")
        st.warning("⚠️ 密钥只显示这一次，请立即复制保存！")
        st.code(resp.key, language="text")
        st.caption(f"名称：{resp.name} | 前缀：{resp.key_prefix} | 生成时间：{resp.created_at}")
        st.markdown("**使用示例（API 调用）：**")
        st.code(
            f'POST {api_client.base_url}/shortcut-submit\n'
            f'{{\n'
            f'  "key": "{resp.key}",\n'
            f'  "url": "https://www.douyin.com/video/xxxx"\n'
            f'}}',
            language="json",
        )
    except APIError as exc:
        if exc.status_code == 401:
            logout()
            st.rerun()
        st.error(f"生成失败：{exc.message}")

st.divider()

# ---- 已生成的密钥列表 ----
st.subheader("📋 已生成的密钥")

try:
    keys = api_client.list_shortcut_keys()
    if not keys:
        st.info("暂无已生成的密钥。")
    else:
        for k in keys:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

                with col1:
                    if k.is_active:
                        st.markdown("🟢 **有效**")
                    else:
                        st.markdown("⚫ 已吊销")
                with col2:
                    st.markdown(f"**{k.name}**")
                    st.caption(f"前缀：`{k.key_prefix}****`")
                with col3:
                    st.caption(f"创建：{k.created_at[:19] if k.created_at else '—'}")
                    if k.last_used_at:
                        st.caption(f"最后使用：{k.last_used_at[:19]}")
                    else:
                        st.caption("最后使用：从未")
                with col4:
                    if k.is_active:
                        revoke_key = f"revoke_confirm_{k.id}"
                        if st.session_state.get(revoke_key, False):
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("确认", key=f"revoke_yes_{k.id}", use_container_width=True):
                                    try:
                                        api_client.revoke_shortcut_key(k.id)
                                        st.success("已吊销")
                                        st.rerun()
                                    except APIError as exc:
                                        st.error(f"吊销失败：{exc.message}")
                            with col_no:
                                if st.button("取消", key=f"revoke_no_{k.id}", use_container_width=True):
                                    st.session_state[revoke_key] = False
                                    st.rerun()
                        else:
                            if st.button("🚫 吊销", key=f"revoke_{k.id}", use_container_width=True):
                                st.session_state[revoke_key] = True
                                st.rerun()
                    else:
                        st.caption("已吊销")
                st.divider()

except APIError as exc:
    if exc.status_code == 401:
        logout()
        st.rerun()
    st.error(f"加载密钥列表失败：{exc.message}")
