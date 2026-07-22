

from src.nlp.sentiment import analyze_sentiment
from src.nlp.entities import extract_entities, extract_keywords
from src.nlp.language import detect_language, translate_to_english
from src.nlp.credibility import compute_credibility_score
from src.nlp.classifier import classify_content_type
from src.nlp.verification import verify_against_sources

__all__ = [
    "analyze_sentiment",
    "extract_entities",
    "extract_keywords",
    "detect_language",
    "translate_to_english",
    "compute_credibility_score",
    "classify_content_type",
    "verify_against_sources",
]
