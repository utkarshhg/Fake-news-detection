

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from src.streamlit.components.ui_components import (
    render_metric_card,
    render_page_header,
    render_section_label,
)


def render_dashboard_page():
    
    render_page_header(
        "Analytics Dashboard",
        "Aggregate insights across every article analyzed on the platform.",
        eyebrow="Overview",
    )

    
    from src.database.db import get_analysis_stats, get_analysis_history
    stats = get_analysis_stats()

    if stats["total_analyses"] == 0:
        st.info("No analyses yet. Head to the Article Analyzer to get started.")
        return

    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Analyzed", stats["total_analyses"])
    with c2:
        render_metric_card("Avg Credibility", f"{stats['avg_credibility']:.0f}/100")
    with c3:
        fake_count = stats["label_distribution"].get("FAKE", 0)
        render_metric_card("Fake Detected", fake_count)
    with c4:
        critical = stats["risk_distribution"].get("Critical", 0)
        high = stats["risk_distribution"].get("High", 0)
        render_metric_card("High Risk", critical + high)

    st.markdown("<br>", unsafe_allow_html=True)

    
    col1, col2 = st.columns(2)

    with col1:
        render_section_label("Risk level distribution")
        risk_data = stats["risk_distribution"]
        if risk_data:
            colors = {
                "Critical": "#dc2626",
                "High": "#ea580c",
                "Medium": "#d97706",
                "Low": "#16a34a",
            }
            labels = list(risk_data.keys())
            values = list(risk_data.values())
            marker_colors = [colors.get(l, "#6b7280") for l in labels]

            fig = go.Figure(go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=marker_colors),
                hole=0.45,
                textinfo="label+percent",
                textfont_size=13,
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#374151"),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data available.")

    with col2:
        render_section_label("Fake vs real distribution")
        label_data = stats["label_distribution"]
        if label_data:
            labels = list(label_data.keys())
            values = list(label_data.values())
            colors_map = {"FAKE": "#dc2626", "REAL": "#16a34a"}
            marker_colors = [colors_map.get(l, "#6b7280") for l in labels]

            fig = go.Figure(go.Bar(
                x=labels,
                y=values,
                marker_color=marker_colors,
                text=values,
                textposition="auto",
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#374151"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data available.")

    
    col3, col4 = st.columns(2)

    with col3:
        render_section_label("Content type breakdown")
        type_data = stats["content_type_distribution"]
        if type_data:
            fig = go.Figure(go.Bar(
                x=list(type_data.values()),
                y=list(type_data.keys()),
                orientation="h",
                marker_color="#2563eb",
                text=list(type_data.values()),
                textposition="auto",
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#374151"),
                xaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
                yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data available.")

    with col4:
        render_section_label("Language distribution")
        lang_data = stats["language_distribution"]
        if lang_data:
            from src.config import SUPPORTED_LANGUAGES
            labels = [SUPPORTED_LANGUAGES.get(k, k) for k in lang_data.keys()]
            values = list(lang_data.values())

            fig = go.Figure(go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                textinfo="label+percent",
                textfont_size=13,
                marker=dict(colors=px.colors.qualitative.Set2),
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#374151"),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data available.")

    
    render_section_label("Credibility score distribution")
    history = get_analysis_history(limit=200)
    if history:
        scores = [h.credibility_score for h in history if h.credibility_score is not None]
        if scores:
            fig = go.Figure(go.Histogram(
                x=scores,
                nbinsx=20,
                marker_color="#2563eb",
                opacity=0.8,
            ))
            fig.add_vline(
                x=sum(scores) / len(scores),
                line_dash="dash",
                line_color="#ea580c",
                annotation_text=f"Avg: {sum(scores)/len(scores):.0f}",
                annotation_font_color="#ea580c",
            )
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=20, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#374151"),
                xaxis_title="Credibility Score",
                yaxis_title="Count",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Not enough data for distribution chart.")
