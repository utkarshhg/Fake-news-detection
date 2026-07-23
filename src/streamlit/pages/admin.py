

import streamlit as st
import pandas as pd
import json
from pathlib import Path

from src.auth.auth import has_permission
from src.streamlit.components.ui_components import (
    render_metric_card,
    render_page_header,
    render_section_label,
)


def render_admin_page():
    
    
    user_role = st.session_state.get("user_role", "reporter")
    if not has_permission(user_role, "admin"):
        st.error("Access Denied. Admin privileges required.")
        return

    render_page_header(
        "Admin Panel",
        "Manage users, monitor system health and review flagged articles.",
        eyebrow="Administration",
    )

    tab_users, tab_system, tab_models, tab_flagged = st.tabs([
        "Users",
        "System Stats",
        "Model Performance",
        "Flagged Articles",
    ])

    with tab_users:
        _render_user_management()

    with tab_system:
        _render_system_stats()

    with tab_models:
        _render_model_metrics()

    with tab_flagged:
        _render_flagged_articles()


def _render_user_management():
    
    from src.database.db import get_all_users, update_user_role, toggle_user_active

    render_section_label("User management")
    users = get_all_users()

    if not users:
        st.info("No users found.")
        return

    data = []
    for u in users:
        data.append({
            "ID": u.id,
            "Username": u.username,
            "Email": u.email,
            "Role": u.role,
            "Active": "Yes" if u.is_active else "No",
            "Created": u.created_at.strftime("%Y-%m-%d") if u.created_at else "—",
            "Last Login": u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "Never",
        })

    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        user_id = st.number_input("User ID", min_value=1, step=1, key="admin_user_id")
    with col2:
        new_role = st.selectbox("New Role", options=["reporter", "researcher", "admin"], key="admin_new_role")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Update Role", use_container_width=True):
            if update_user_role(int(user_id), new_role):
                st.success(f"User #{user_id} role updated to '{new_role}'")
                st.rerun()
            else:
                st.error("User not found.")

    col4, col5 = st.columns(2)
    with col4:
        toggle_id = st.number_input("Toggle Active — User ID", min_value=1, step=1, key="toggle_id")
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Toggle Active/Inactive", use_container_width=True):
            if toggle_user_active(int(toggle_id)):
                st.success(f"User #{toggle_id} active status toggled.")
                st.rerun()


def _render_system_stats():
    
    from src.database.db import get_analysis_stats, get_all_users

    stats = get_analysis_stats()
    users = get_all_users()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Users", len(users))
    with c2:
        render_metric_card("Total Analyses", stats["total_analyses"])
    with c3:
        render_metric_card("Avg Credibility", f"{stats['avg_credibility']:.0f}")
    with c4:
        active = sum(1 for u in users if u.is_active)
        render_metric_card("Active Users", active)

    st.markdown("<br>", unsafe_allow_html=True)

    
    col1, col2 = st.columns(2)
    with col1:
        render_section_label("User role distribution")
        role_counts = {}
        for u in users:
            role_counts[u.role] = role_counts.get(u.role, 0) + 1
        if role_counts:
            df = pd.DataFrame(
                {"Role": list(role_counts.keys()), "Count": list(role_counts.values())}
            )
            st.bar_chart(df, x="Role", y="Count")

    with col2:
        render_section_label("Risk level distribution")
        risk = stats.get("risk_distribution", {})
        if risk:
            df = pd.DataFrame(
                {"Risk": list(risk.keys()), "Count": list(risk.values())}
            )
            st.bar_chart(df, x="Risk", y="Count")


def _render_model_metrics():
    
    from src.config import PROJ_ROOT

    metrics_path = PROJ_ROOT / "metrics.json"

    if not metrics_path.exists():
        st.warning("No metrics.json found. Run the evaluation pipeline first.")
        return

    with open(metrics_path) as f:
        metrics = json.load(f)

    render_section_label("Model performance comparison")

    
    rows = []
    for model, m in metrics.items():
        rows.append({
            "Model": model,
            "Accuracy": f"{m.get('accuracy', 0):.4f}",
            "Precision": f"{m.get('precision', 'N/A')}",
            "Recall": f"{m.get('recall', 'N/A')}",
            "F1": f"{m.get('f1', 0):.4f}",
            "ROC-AUC": f"{m.get('roc_auc', 0):.4f}",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    
    best = max(metrics.items(), key=lambda x: x[1].get("f1", 0))
    st.success(f"Best model: **{best[0]}** (F1: {best[1].get('f1', 0):.4f})")

    
    figures_dir = PROJ_ROOT / "reports" / "figures"
    if figures_dir.exists():
        roc_files = list(figures_dir.glob("*_roc.png"))
        if roc_files:
            render_section_label("ROC curves")
            cols = st.columns(min(len(roc_files), 2))
            for i, roc_path in enumerate(roc_files):
                with cols[i % 2]:
                    st.image(str(roc_path), caption=roc_path.stem)


def _render_flagged_articles():
    
    from src.database.db import get_flagged_articles, review_flagged_article

    render_section_label("Flagged articles review queue")

    status_filter = st.selectbox("Status", ["pending", "reviewed", "dismissed", "All"])
    status = status_filter if status_filter != "All" else None

    flagged = get_flagged_articles(status=status)

    if not flagged:
        st.info("No flagged articles found.")
        return

    for flag in flagged:
        with st.expander(f"Flag #{flag.id} — Analysis #{flag.analysis_id} ({flag.status})"):
            st.markdown(f"**Reason:** {flag.reason or 'No reason provided'}")
            st.markdown(f"**Status:** {flag.status}")
            st.markdown(f"**Flagged:** {flag.created_at}")

            if flag.status == "pending":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Mark Reviewed", key=f"review_{flag.id}"):
                        admin_id = st.session_state.get("user_id")
                        review_flagged_article(flag.id, "reviewed", admin_id)
                        st.rerun()
                with col2:
                    if st.button("Dismiss", key=f"dismiss_{flag.id}"):
                        admin_id = st.session_state.get("user_id")
                        review_flagged_article(flag.id, "dismissed", admin_id)
                        st.rerun()
