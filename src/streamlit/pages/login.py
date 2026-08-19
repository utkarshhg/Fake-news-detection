

import streamlit as st
from src.auth.auth import authenticate_user, register_user
from src.config import ROLES


def render_login_page():
    
    st.markdown(
        '<div style="text-align:center; padding:56px 0 8px;">'
        '<div style="display:inline-block; padding:6px 14px; border-radius:999px; '
        'background:#eef0ff; color:#3538cd; font-size:0.7rem; font-weight:700; '
        'letter-spacing:0.14em; text-transform:uppercase;">Verified Journalism Toolkit</div>'
        '<h1 style="font-family:Sora, Inter, sans-serif; font-size:2.6rem; font-weight:700; '
        'color:#101828; letter-spacing:-0.03em; margin:18px 0 10px;">Fake News Detector</h1>'
        '<p style="color:#475467; font-size:1rem; max-width:520px; margin:0 auto; '
        'line-height:1.6;">An AI-assisted workspace for scoring article credibility, '
        'tracing sources and flagging misinformation before it spreads.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2, 1])

    with center:
        tab_login, tab_register = st.tabs(["Sign in", "Create account"])

        with tab_login:
            _render_login_form()

        with tab_register:
            _render_register_form()

        st.markdown(
            '<p style="text-align:center; font-size:0.78rem; color:#8a94a6; '
            'margin-top:18px;">Your analyses stay private to your account unless '
            'shared by an administrator.</p>',
            unsafe_allow_html=True,
        )


def _render_login_form():
    
    with st.form("login_form", clear_on_submit=False):
        st.markdown(
            '<div style="font-family:Sora, Inter, sans-serif; font-size:1.25rem; '
            'font-weight:600; color:#101828; margin-bottom:2px;">Welcome back</div>'
            '<p style="font-size:0.86rem; color:#8a94a6; margin-bottom:14px;">'
            'Sign in to continue your verification work.</p>',
            unsafe_allow_html=True,
        )
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

        submit = st.form_submit_button("Sign in", use_container_width=True, type="primary")

        if submit:
            if not username or not password:
                st.error("Please fill in all fields.")
                return

            result = authenticate_user(username, password)

            if result["success"]:
                user = result["user"]
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user.id
                st.session_state["username"] = user.username
                st.session_state["user_role"] = user.role
                st.success(f"Welcome back, {user.username}!")
                st.rerun()
            else:
                st.error(f"Login failed: {result['message']}")


def _render_register_form():
    
    with st.form("register_form", clear_on_submit=True):
        st.markdown(
            '<div style="font-family:Sora, Inter, sans-serif; font-size:1.25rem; '
            'font-weight:600; color:#101828; margin-bottom:2px;">Create your account</div>'
            '<p style="font-size:0.86rem; color:#8a94a6; margin-bottom:14px;">'
            'Choose a role to tailor the tools you see.</p>',
            unsafe_allow_html=True,
        )
        username = st.text_input("Username", placeholder="Choose a username (min 3 chars)", key="reg_user")
        email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pass")
        password_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_pass2")
        role = st.selectbox(
            "Role",
            options=["reporter", "researcher"],
            format_func=lambda r: {"reporter": "Reporter", "researcher": "Researcher"}.get(r, r),
            key="reg_role",
        )

        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")

        if submit:
            if password != password_confirm:
                st.error("Passwords do not match.")
                return

            result = register_user(username, email, password, role)

            if result["success"]:
                st.success("Account created. Please log in.")
            else:
                st.error(result["message"])
