

import streamlit as st
import pandas as pd
from datetime import datetime

from src.streamlit.components.ui_components import (
    render_page_header,
    render_section_label,
)


def render_history_page():
    
    render_page_header(
        "Analysis History",
        "Browse, filter and export every past article analysis.",
        eyebrow="Records",
    )

    from src.database.db import get_analysis_history

    
    render_section_label("Filters")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        risk_filter = st.selectbox(
            "Risk Level",
            options=["All", "Critical", "High", "Medium", "Low"],
        )

    with col_f2:
        lang_filter = st.selectbox(
            "Language",
            options=["All", "en", "hi", "mr", "te", "hinglish"],
            format_func=lambda x: {
                "All": "All Languages",
                "en": "English",
                "hi": "Hindi",
                "mr": "Marathi",
                "te": "Telugu",
                "hinglish": "Hinglish",
            }.get(x, x),
        )

    with col_f3:
        limit = st.selectbox("Show", options=[25, 50, 100, 200], index=1)

    
    filters = {}
    if risk_filter != "All":
        filters["risk_level"] = risk_filter
    if lang_filter != "All":
        filters["language"] = lang_filter

    user_id = None
    role = st.session_state.get("user_role", "reporter")
    if role == "reporter":
        user_id = st.session_state.get("user_id")

    history = get_analysis_history(
        user_id=user_id,
        limit=limit,
        risk_level=filters.get("risk_level"),
        language=filters.get("language"),
    )

    if not history:
        st.info("No analyses found matching your filters.")
        return

    
    data = []
    for h in history:
        data.append({
            "ID": h.id,
            "Date": h.created_at.strftime("%Y-%m-%d %H:%M") if h.created_at else "",
            "Prediction": h.prediction_label or "—",
            "Confidence": f"{(h.prediction_confidence or 0):.1%}",
            "Credibility": h.credibility_score or 0,
            "Risk": h.risk_level or "—",
            "Content Type": h.content_type or "—",
            "Language": h.language_detected or "—",
            "Sentiment": h.sentiment_label or "—",
            "Text Preview": (h.article_text or "")[:80] + "...",
        })

    df = pd.DataFrame(data)

    
    st.markdown(
        f'<div class="section-label">Showing {len(data)} results</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Date": st.column_config.TextColumn("Date", width="medium"),
            "Prediction": st.column_config.TextColumn("Prediction", width="small"),
            "Credibility": st.column_config.ProgressColumn(
                "Credibility",
                min_value=0,
                max_value=100,
                format="%d/100",
            ),
            "Risk": st.column_config.TextColumn("Risk", width="small"),
            "Text Preview": st.column_config.TextColumn("Text Preview", width="large"),
        },
    )

    
    st.markdown("---")
    col_export, _ = st.columns([1, 3])
    with col_export:
        csv = df.to_csv(index=False)
        st.download_button(
            "Export to CSV",
            data=csv,
            file_name=f"analysis_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    
    st.markdown("---")
    render_section_label("View analysis detail")
    selected_id = st.number_input(
        "Enter Analysis ID to view details",
        min_value=1,
        step=1,
        value=None,
        placeholder="e.g. 1",
    )

    if selected_id:
        from src.database.db import get_analysis_by_id
        record = get_analysis_by_id(int(selected_id))
        if record:
            with st.expander(f"Analysis #{record.id} — {record.prediction_label}", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("Credibility", f"{record.credibility_score}/100")
                col2.metric("Risk Level", record.risk_level)
                col3.metric("Content Type", record.content_type)

                st.markdown("**Article Text (preview):**")
                st.text(record.article_text[:500] if record.article_text else "N/A")

                if record.flags_json:
                    st.markdown("**Flags:**")
                    for flag in record.flags_json:
                        st.warning(flag)
        else:
            st.warning(f"Analysis #{selected_id} not found.")
