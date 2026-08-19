

import streamlit as st
import plotly.graph_objects as go


INK = "#101828"
INK_SOFT = "#475467"
INK_MUTED = "#8a94a6"
SURFACE = "#ffffff"
SURFACE_2 = "#f7f8fb"
LINE = "#e3e8ef"
BRAND = "#3538cd"
SUCCESS = "#067647"
WARNING = "#b54708"
DANGER = "#b42318"

FONT_DISPLAY = "'Sora', 'Inter', sans-serif"


def render_page_header(title: str, subtitle: str = "", eyebrow: str = ""):
    
    eyebrow_html = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="page-head">{eyebrow_html}'
        f"<h2>{title}</h2>{subtitle_html}</div>",
        unsafe_allow_html=True,
    )


def render_section_label(text: str):
    
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def render_credibility_gauge(score: int, risk_level: str, risk_color: str):
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"size": 38, "color": INK, "family": "Sora, Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cfd6e4"},
            "bar": {"color": risk_color, "thickness": 0.32},
            "bgcolor": SURFACE_2,
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25], "color": "#fef3f2"},
                {"range": [25, 50], "color": "#fff6ed"},
                {"range": [50, 75], "color": "#fefbe8"},
                {"range": [75, 100], "color": "#edfcf2"},
            ],
            "threshold": {
                "line": {"color": INK, "width": 2},
                "thickness": 0.82,
                "value": score,
            },
        },
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=30, r=30, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": INK, "family": "Inter"},
    )

    st.plotly_chart(fig, use_container_width=True)


def render_risk_badge(risk_level: str, risk_color: str):
    
    st.markdown(
        f'<div style="text-align:center; padding:16px 14px; background:{risk_color}0f; '
        f'border:1px solid {risk_color}33; border-radius:12px; margin:8px 0; '
        f'box-shadow:0 1px 2px rgba(16,24,40,0.05);">'
        f'<div style="font-size:0.66rem; letter-spacing:0.14em; text-transform:uppercase; '
        f'color:{INK_MUTED}; font-weight:600; margin-bottom:4px;">Assessment</div>'
        f'<div style="font-family:{FONT_DISPLAY}; font-size:1.15rem; font-weight:700; '
        f'color:{risk_color};">{risk_level} Risk</div></div>',
        unsafe_allow_html=True,
    )


def render_entity_tags(entities: list):
    
    if not entities:
        st.caption("No entities extracted.")
        return

    color_map = {
        "PERSON": "#3538cd",
        "ORG": SUCCESS,
        "GPE": WARNING,
        "LOC": WARNING,
        "DATE": "#6938ef",
        "EVENT": DANGER,
        "MONEY": "#0e7090",
        "NORP": "#1570ef",
    }

    tags_html = '<div style="display:flex; flex-wrap:wrap; gap:6px;">'
    for ent in entities[:20]:
        color = color_map.get(ent.get("label", ""), INK_SOFT)
        label = ent.get("description", ent.get("label", ""))
        text = ent.get("text", "")
        tags_html += (
            f'<span style="display:inline-flex; align-items:center; gap:6px; '
            f'padding:5px 11px; border-radius:999px; font-size:0.8rem; font-weight:600; '
            f'background:{color}0f; color:{color}; border:1px solid {color}2e;">'
            f'{text}<span style="opacity:0.65; font-size:0.68rem; font-weight:500;">'
            f'{label}</span></span>'
        )
    tags_html += "</div>"

    st.markdown(tags_html, unsafe_allow_html=True)


def render_metric_card(label: str, value, icon: str = "", delta: str = None):
    
    delta_html = ""
    if delta:
        color = SUCCESS if "+" in str(delta) else DANGER
        delta_html = (
            f'<div style="margin-top:6px; font-size:0.76rem; font-weight:600; '
            f'color:{color};">{delta}</div>'
        )

    st.markdown(
        f'<div class="surface-card" style="text-align:left; padding:18px 20px;">'
        f'<div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; '
        f'color:{INK_MUTED}; font-weight:600; margin-bottom:10px;">{label}</div>'
        f'<div style="font-family:{FONT_DISPLAY}; font-size:1.7rem; font-weight:700; '
        f'line-height:1.1; color:{INK};">{value}</div>'
        f'{delta_html}</div>',
        unsafe_allow_html=True,
    )


def render_sentiment_bar(polarity: float, subjectivity: float):
    
    col1, col2 = st.columns(2)

    with col1:
        st.caption("Polarity")
        norm_polarity = (polarity + 1) / 2
        color = SUCCESS if polarity > 0.1 else DANGER if polarity < -0.1 else WARNING
        st.progress(norm_polarity)
        st.markdown(
            f'<div style="text-align:center; color:{color}; font-weight:700; '
            f'font-family:{FONT_DISPLAY};">{polarity:+.2f}</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.caption("Subjectivity")
        st.progress(subjectivity)
        label = "Objective" if subjectivity < 0.4 else "Subjective" if subjectivity < 0.7 else "Very Subjective"
        st.markdown(
            f'<div style="text-align:center; font-weight:700; color:{INK_SOFT}; '
            f'font-family:{FONT_DISPLAY};">{subjectivity:.2f} ({label})</div>',
            unsafe_allow_html=True,
        )


def render_source_list(sources: list):
    
    if not sources:
        st.info("No matching sources found for verification.")
        return

    for src in sources:
        trust_badge = "Trusted" if src.get("is_trusted") else "Source"
        badge_color = SUCCESS if src.get("is_trusted") else INK_MUTED

        st.markdown(
            f'<div style="background:{SURFACE}; border:1px solid {LINE}; '
            f'border-radius:12px; padding:13px 16px; margin:6px 0; '
            f'box-shadow:0 1px 2px rgba(16,24,40,0.05);">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">'
            f'<span style="font-weight:600; font-size:0.9rem; color:{INK};">'
            f'{src.get("title", "")[:80]}</span>'
            f'<span style="flex-shrink:0; font-size:0.68rem; font-weight:600; letter-spacing:0.06em; '
            f'text-transform:uppercase; padding:3px 9px; border-radius:999px; '
            f'background:{badge_color}12; color:{badge_color}; border:1px solid {badge_color}30;">'
            f'{trust_badge}</span></div>'
            f'<div style="font-size:0.78rem; color:{INK_MUTED}; margin-top:6px;">'
            f'{src.get("source", "")} &middot; '
            f'<a href="{src.get("url", "#")}" target="_blank" '
            f'style="color:{BRAND}; font-weight:600; text-decoration:none;">Read article &rarr;</a>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def render_flags_list(flags: list):
    
    if not flags:
        st.success("No warning flags detected.")
        return

    for flag in flags:
        st.markdown(
            f'<div style="background:#fffaf5; border:1px solid #fedf89; '
            f'border-left:4px solid {WARNING}; padding:11px 16px; '
            f'border-radius:0 10px 10px 0; margin:6px 0; '
            f'font-size:0.87rem; font-weight:500; color:#93370d;">'
            f'{flag}</div>',
            unsafe_allow_html=True,
        )


def render_breakdown_table(breakdown: dict):
    
    for component, data in breakdown.items():
        label = component.replace("_", " ").title()
        score = data.get("score", 0)
        weight = data.get("weight", 0) * 100
        weighted = data.get("weighted_score", 0)
        details = data.get("details", "")

        if score >= 75:
            color = SUCCESS
        elif score >= 50:
            color = WARNING
        elif score >= 25:
            color = "#c4320a"
        else:
            color = DANGER

        st.markdown(
            f'<div style="background:{SURFACE}; border:1px solid {LINE}; border-radius:12px; '
            f'padding:12px 16px; margin:6px 0; display:flex; align-items:center; gap:14px; '
            f'box-shadow:0 1px 2px rgba(16,24,40,0.04);">'
            f'<div style="min-width:140px; font-weight:600; font-size:0.85rem; color:{INK};">'
            f'{label}</div>'
            f'<div style="flex:1; background:#eef1f7; border-radius:999px; height:8px; overflow:hidden;">'
            f'<div style="width:{score}%; height:100%; background:{color}; border-radius:999px;">'
            f'</div></div>'
            f'<div style="min-width:44px; text-align:right; font-weight:700; color:{color}; '
            f'font-family:{FONT_DISPLAY}; font-size:0.95rem;">{score:.0f}</div>'
            f'<div style="min-width:82px; text-align:right; font-size:0.72rem; color:{INK_MUTED};">'
            f'x{weight:.0f}% = {weighted:.1f}</div></div>',
            unsafe_allow_html=True,
        )
        if details:
            st.caption(f"   {details}")
