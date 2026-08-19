

import streamlit as st
from loguru import logger

from src.streamlit.components.ui_components import (
    render_credibility_gauge,
    render_risk_badge,
    render_entity_tags,
    render_sentiment_bar,
    render_source_list,
    render_flags_list,
    render_breakdown_table,
    render_metric_card,
    render_page_header,
    render_section_label,
)


def render_analyzer_page():
    
    render_page_header(
        "Article Analyzer",
        "Paste an article or enter a URL to run a full credibility analysis.",
        eyebrow="Analysis",
    )

    
    input_tab, url_tab = st.tabs(["Paste Text", "Enter URL"])

    article_text = ""
    article_url = None
    article_title = None

    with input_tab:
        render_section_label("Article text")
        article_text = st.text_area(
            "Article Text",
            height=220,
            placeholder="Paste the full article text here...",
            label_visibility="collapsed",
        )

    with url_tab:
        render_section_label("Article URL")
        url_input = st.text_input(
            "Article URL",
            placeholder="https://example.com/article",
            label_visibility="collapsed",
        )
        if url_input:
            article_url = url_input
            with st.spinner("Fetching article..."):
                article_text, article_title = _fetch_article(url_input)
                if article_text:
                    st.success(f"Fetched: {article_title or 'Article loaded'}")
                    with st.expander("Preview fetched text"):
                        st.text(article_text[:1000] + ("..." if len(article_text) > 1000 else ""))

    
    col_model, col_button = st.columns([2, 1])
    with col_model:
        from src.config import AVAILABLE_MODELS, DEFAULT_MODEL
        model_name = st.selectbox(
            "ML Model",
            options=AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(DEFAULT_MODEL),
            format_func=lambda m: {
                "lightgbm": "LightGBM (Best)",
                "randomforest": "Random Forest",
                "bernoullinb": "Bernoulli NB",
                "multinomialnb": "Multinomial NB",
            }.get(m, m),
        )
    with col_button:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_clicked = st.button(
            "Analyze Article",
            use_container_width=True,
            type="primary",
            disabled=not article_text,
        )

    
    if analyze_clicked and article_text:
        _run_analysis(article_text, model_name, article_url, article_title)


def _run_analysis(text: str, model_name: str, article_url: str = None, article_title: str = None):
    
    results = {}

    with st.spinner("Analyzing article..."):
        progress = st.progress(0, text="Detecting language...")

        
        from src.nlp.language import detect_language, translate_to_english
        lang_result = detect_language(text)
        results["language"] = lang_result

        analysis_text = text
        was_translated = False
        if lang_result["code"] != "en" and lang_result["is_supported"]:
            progress.progress(10, text=f"Translating from {lang_result['name']}...")
            trans_result = translate_to_english(text, lang_result["code"])
            if trans_result["was_translated"]:
                analysis_text = trans_result["translated_text"]
                was_translated = True
                results["language"]["was_translated"] = True

        
        progress.progress(25, text="Running ML model...")
        try:
            from src.modeling.predict import predict_text
            ml_result = predict_text(analysis_text, model_name=model_name)
        except FileNotFoundError:
            ml_result = {
                "label": "UNAVAILABLE",
                "confidence": 0.0,
                "fake_probability": 0.5,
                "real_probability": 0.5,
                "model_used": model_name,
            }
            st.warning("Trained models not found. Run the training pipeline first.")
        results["ml_prediction"] = ml_result

        
        progress.progress(40, text="Analyzing sentiment...")
        from src.nlp.sentiment import analyze_sentiment
        sentiment_result = analyze_sentiment(analysis_text)
        results["sentiment"] = sentiment_result

        
        progress.progress(55, text="Extracting entities and keywords...")
        from src.nlp.entities import extract_entities, extract_keywords
        entity_result = extract_entities(analysis_text)
        keyword_result = extract_keywords(analysis_text)
        results["entities"] = entity_result
        results["keywords"] = keyword_result

        
        progress.progress(70, text="Classifying content type...")
        from src.nlp.classifier import classify_content_type
        class_result = classify_content_type(analysis_text, ml_prediction=ml_result)
        results["classification"] = class_result

        
        progress.progress(85, text="Verifying against trusted sources...")
        from src.nlp.verification import verify_against_sources
        verify_result = verify_against_sources(analysis_text, keyword_result)
        results["verification"] = verify_result

        
        progress.progress(95, text="Computing credibility score...")
        from src.nlp.credibility import compute_credibility_score
        cred_result = compute_credibility_score(
            ml_prediction=ml_result,
            sentiment_result=sentiment_result,
            classification_result=class_result,
            entity_result=entity_result,
            verification_result=verify_result,
        )
        results["credibility"] = cred_result

        progress.progress(100, text="Analysis complete.")

    
    analysis_id = None
    try:
        from src.database.db import save_analysis
        user_id = st.session_state.get("user_id")
        record = save_analysis(
            article_text=text,
            results=results,
            user_id=user_id,
            article_url=article_url,
            article_title=article_title,
        )
        analysis_id = record.id
    except Exception as e:
        logger.warning(f"Failed to save analysis: {e}")

    
    st.divider()
    _display_results(results, analysis_id, was_translated, lang_result)


def _display_results(results: dict, analysis_id: int, was_translated: bool, lang_result: dict):
    
    cred = results.get("credibility", {})
    ml = results.get("ml_prediction", {})
    sentiment = results.get("sentiment", {})
    entities = results.get("entities", {})
    keywords = results.get("keywords", [])
    classification = results.get("classification", {})
    verification = results.get("verification", {})

    
    if was_translated:
        st.info(f"Language detected: **{lang_result.get('name', 'Unknown')}** — Translated to English for analysis")
    elif lang_result.get("code") != "en":
        st.info(f"Language: **{lang_result.get('name', 'Unknown')}** (Confidence: {lang_result.get('confidence', 0):.0%})")

    
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        render_section_label("Credibility score")
        render_credibility_gauge(
            cred.get("score", 50),
            cred.get("risk_level", "Medium"),
            cred.get("risk_color", "#d97706"),
        )

    with col2:
        render_section_label("Risk level")
        render_risk_badge(cred.get("risk_level", "Medium"), cred.get("risk_color", "#d97706"))
        st.markdown("<br>", unsafe_allow_html=True)
        render_section_label("Model prediction")
        label = ml.get("label", "?")
        conf = ml.get("confidence", 0)
        label_color = "#dc2626" if label == "FAKE" else "#16a34a" if label == "REAL" else "#d97706"
        st.markdown(
            f'<div style="text-align:center; padding:12px; border-radius:8px; '
            f'background:{label_color}08; border:1px solid {label_color}30;">'
            f'<span style="font-size:1.3rem; font-weight:700; color:{label_color};">{label}</span><br>'
            f'<span style="font-size:0.78rem; color:#6b7280;">{conf:.1%} confidence</span></div>',
            unsafe_allow_html=True,
        )

    with col3:
        render_section_label("Content type")
        primary = classification.get("primary_type", "Unknown")
        st.markdown(
            f'<div style="text-align:center; padding:12px; border-radius:8px; '
            f'background:#eff6ff; border:1px solid #bfdbfe;">'
            f'<span style="font-size:1rem; font-weight:700; color:#2563eb;">{primary}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        render_section_label("Sentiment")
        label_s = sentiment.get("sentiment_label", "Neutral")
        polarity = sentiment.get("polarity", 0)
        st.markdown(
            f'<div style="text-align:center; padding:12px; border-radius:8px; '
            f'background:#f9fafb; border:1px solid #e5e7eb;">'
            f'<span style="font-weight:600; color:#374151;">{label_s}</span><br>'
            f'<span style="font-size:0.78rem; color:#6b7280;">Polarity: {polarity:+.2f}</span></div>',
            unsafe_allow_html=True,
        )

    
    st.markdown("---")
    summary = cred.get("summary", "")
    if summary:
        
        clean_summary = summary.lstrip("⛔⚠️🔶✅ ")
        st.markdown(
            f'<div class="surface-card" style="border-left:4px solid #3538cd; '
            f'font-size:0.95rem; font-weight:600; color:#101828; line-height:1.55;">'
            f'{clean_summary}</div>',
            unsafe_allow_html=True,
        )

    
    tab_breakdown, tab_sentiment, tab_entities, tab_verify, tab_flags = st.tabs([
        "Score Breakdown",
        "Sentiment Details",
        "Entities and Keywords",
        "Source Verification",
        "Warning Flags",
    ])

    with tab_breakdown:
        render_section_label("Credibility score breakdown")
        render_breakdown_table(cred.get("breakdown", {}))

    with tab_sentiment:
        render_section_label("Sentiment analysis")
        render_sentiment_bar(
            sentiment.get("polarity", 0),
            sentiment.get("subjectivity", 0),
        )
        st.markdown(f"**Subjectivity:** {sentiment.get('subjectivity_label', 'Unknown')}")
        if sentiment.get("flags"):
            st.markdown("**Sentiment flags:**")
            for f in sentiment["flags"]:
                st.warning(f)

    with tab_entities:
        col_e, col_k = st.columns(2)
        with col_e:
            render_section_label("Named entities")
            render_entity_tags(entities.get("entities", []))
        with col_k:
            render_section_label("Top keywords")
            for kw in keywords[:10]:
                freq_bar = "=" * int(kw.get("frequency", 0) * 50)
                st.markdown(
                    f'`{kw["word"]}` — {kw["count"]} occurrences '
                    f'<span style="color:#2563eb; font-family:monospace; font-size:0.75rem;">'
                    f'{freq_bar}</span>',
                    unsafe_allow_html=True,
                )

    with tab_verify:
        render_section_label("Real-time source verification")
        status = verification.get("status", "error")
        status_display = {
            "verified": ("Verified", "#16a34a"),
            "partially_verified": ("Partially Verified", "#d97706"),
            "no_matches": ("Unverified", "#dc2626"),
            "error": ("Verification Unavailable", "#6b7280"),
        }
        label, color = status_display.get(status, ("Unknown", "#6b7280"))
        st.markdown(
            f'<span style="font-size:1rem; font-weight:700; color:{color};">{label}</span>',
            unsafe_allow_html=True,
        )
        if verification.get("query_used"):
            st.caption(f'Search query: "{verification["query_used"]}"')
        render_source_list(verification.get("matching_sources", []))

    with tab_flags:
        render_section_label("Misinformation indicators")
        render_flags_list(cred.get("flags", []))

    
    if analysis_id:
        st.caption(f"Analysis ID: #{analysis_id} — Saved to database")


def _fetch_article(url: str) -> tuple[str, str]:
    
    try:
        from newspaper import Article

        article = Article(url)
        article.download()
        article.parse()
        return article.text, article.title
    except Exception as e:
        st.error(f"Failed to fetch article: {e}")
        return "", ""
