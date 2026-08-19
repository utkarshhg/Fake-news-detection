

import streamlit as st
from pathlib import Path



st.set_page_config(
    page_title="Fake News Detector",
    page_icon="FN",
    layout="wide",
    initial_sidebar_state="expanded",
)


css_path = Path(__file__).parent / "src" / "streamlit" / "styles" / "theme.css"
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


from src.database.db import init_db
init_db()


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None


if not st.session_state["authenticated"]:
    from src.streamlit.pages.login import render_login_page
    render_login_page()
    st.stop()


with st.sidebar:
    _username = st.session_state["username"] or ""
    _role = st.session_state["user_role"] or "member"
    _initials = "".join(part[0] for part in _username.split()[:2]).upper() or _username[:2].upper()

    st.markdown(
        '<div class="sb-brand">'
        '<div class="sb-brand-mark">FN</div>'
        '<div class="sb-brand-text">'
        '<div class="sb-brand-title">Fake News Detector</div>'
        '<div class="sb-brand-sub">Credibility intelligence</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="sb-user">'
        f'<div class="sb-avatar">{_initials}</div>'
        f'<div class="sb-user-meta">'
        f'<div class="sb-user-name">{_username}</div>'
        f'<div class="sb-user-role">{_role}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-label">Navigation</div>', unsafe_allow_html=True)

    pages = {
        "Article Analyzer": "analyzer",
        "Dashboard": "dashboard",
        "History": "history",
    }

    if st.session_state["user_role"] == "admin":
        pages["Admin Panel"] = "admin"

    selected = st.radio(
        "Go to",
        options=list(pages.keys()),
        label_visibility="collapsed",
    )

    current_page = pages[selected]

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True):
        for key in ["authenticated", "user_id", "username", "user_role"]:
            st.session_state[key] = None if key != "authenticated" else False
        st.rerun()

    st.markdown(
        '<div class="sb-footer">'
        '<span class="sb-footer-dot"></span>'
        'Fake News Detector v1.0.0<br>Built for Devkriti'
        '</div>',
        unsafe_allow_html=True,
    )


if current_page == "analyzer":
    from src.streamlit.pages.analyzer import render_analyzer_page
    render_analyzer_page()

elif current_page == "dashboard":
    from src.streamlit.pages.dashboard import render_dashboard_page
    render_dashboard_page()

elif current_page == "history":
    from src.streamlit.pages.history import render_history_page
    render_history_page()

elif current_page == "admin":
    from src.streamlit.pages.admin import render_admin_page
    render_admin_page()
