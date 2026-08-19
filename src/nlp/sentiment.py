

from textblob import TextBlob
from loguru import logger


def analyze_sentiment(text: str) -> dict:
    
    if not text or not text.strip():
        return _empty_result()

    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        return _empty_result()

    
    if polarity > 0.1:
        sentiment_label = "Positive"
    elif polarity < -0.1:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    
    if subjectivity < 0.3:
        subjectivity_label = "Objective"
    elif subjectivity < 0.6:
        subjectivity_label = "Somewhat Subjective"
    else:
        subjectivity_label = "Highly Subjective"

    
    flags = []
    is_suspicious = False

    
    if abs(polarity) > 0.6:
        flags.append("Extremely emotionally charged language detected")
        is_suspicious = True

    
    if subjectivity > 0.7:
        flags.append("Highly subjective — may be opinion disguised as news")
        is_suspicious = True

    
    if polarity < -0.3 and subjectivity > 0.5:
        flags.append("Negative + subjective: common propaganda pattern")
        is_suspicious = True

    return {
        "polarity": round(polarity, 4),
        "subjectivity": round(subjectivity, 4),
        "sentiment_label": sentiment_label,
        "subjectivity_label": subjectivity_label,
        "is_suspicious": is_suspicious,
        "flags": flags,
    }


def _empty_result() -> dict:
    
    return {
        "polarity": 0.0,
        "subjectivity": 0.0,
        "sentiment_label": "Neutral",
        "subjectivity_label": "Objective",
        "is_suspicious": False,
        "flags": [],
    }
