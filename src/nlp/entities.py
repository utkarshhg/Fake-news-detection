

import re
from collections import Counter

from loguru import logger


_nlp_model = None


def _get_nlp():
    
    global _nlp_model
    if _nlp_model is None:
        try:
            import spacy
            _nlp_model = spacy.load("en_core_web_sm")
            logger.info("spaCy model 'en_core_web_sm' loaded.")
        except Exception as e:
            logger.warning(
                f"spaCy model unavailable ({e}). Falling back gracefully."
            )
            _nlp_model = False  
    return _nlp_model if _nlp_model is not False else None


def extract_entities(text: str, max_entities: int = 20) -> dict:
    
    nlp = _get_nlp()
    if nlp is None:
        return _empty_entity_result()

    
    if len(text) > 100_000:
        text = text[:100_000]

    try:
        doc = nlp(text)
    except Exception as e:
        logger.warning(f"Entity extraction failed: {e}")
        return _empty_entity_result()

    
    entities = []
    seen = set()
    label_counts = Counter()

    LABEL_DESCRIPTIONS = {
        "PERSON": "Person",
        "ORG": "Organization",
        "GPE": "Location/Country",
        "LOC": "Location",
        "DATE": "Date",
        "EVENT": "Event",
        "MONEY": "Monetary Value",
        "PERCENT": "Percentage",
        "NORP": "Nationality/Group",
        "FAC": "Facility",
        "PRODUCT": "Product",
        "WORK_OF_ART": "Creative Work",
    }

    for ent in doc.ents:
        key = (ent.text.strip(), ent.label_)
        if key not in seen and len(entities) < max_entities:
            seen.add(key)
            entities.append({
                "text": ent.text.strip(),
                "label": ent.label_,
                "description": LABEL_DESCRIPTIONS.get(ent.label_, ent.label_),
            })
        label_counts[ent.label_] += 1

    
    persons = [e["text"] for e in entities if e["label"] == "PERSON"]
    organizations = [e["text"] for e in entities if e["label"] == "ORG"]
    locations = [e["text"] for e in entities if e["label"] in ("GPE", "LOC")]

    
    suspicious = _detect_suspicious_patterns(text, entities, label_counts)

    return {
        "entities": entities,
        "entity_counts": dict(label_counts),
        "persons": persons,
        "organizations": organizations,
        "locations": locations,
        "suspicious_patterns": suspicious,
    }


def extract_keywords(text: str, top_n: int = 15) -> list[dict]:
    
    if not text or not text.strip():
        return []

    
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    
    stopwords = {
        "the", "and", "was", "for", "that", "with", "this", "from", "have",
        "has", "had", "are", "were", "been", "being", "not", "but", "they",
        "their", "them", "will", "would", "could", "should", "can", "may",
        "might", "shall", "its", "also", "than", "other", "into", "more",
        "some", "such", "only", "then", "about", "which", "when", "what",
        "there", "each", "all", "these", "those", "any", "who", "how",
        "said", "one", "two", "new", "just", "like", "over", "after",
        "before", "between", "through", "very", "most", "own", "same",
        "both", "during", "where", "does", "did", "get", "got", "his",
        "her", "she", "him", "you", "our", "out", "now", "way", "use",
    }

    filtered = [w for w in words if w not in stopwords]
    counter = Counter(filtered)
    total = len(filtered) if filtered else 1

    return [
        {
            "word": word,
            "count": count,
            "frequency": round(count / total, 4),
        }
        for word, count in counter.most_common(top_n)
    ]


def _detect_suspicious_patterns(text: str, entities: list, label_counts: dict) -> list[str]:
    
    flags = []

    
    caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
    if len(caps_words) > 5:
        flags.append(f"Excessive ALL-CAPS words detected ({len(caps_words)} instances)")

    
    excl_count = text.count("!") + text.count("?")
    if excl_count > 10:
        flags.append(f"Excessive punctuation ({excl_count} exclamation/question marks)")

    
    superlatives = re.findall(
        r'\b(always|never|everyone|nobody|worst|best|shocking|breaking|exclusive|urgent|'
        r'unbelievable|incredible|outrageous|horrifying|devastating|massive|huge)\b',
        text.lower()
    )
    if len(superlatives) > 5:
        flags.append(
            f"Excessive sensational language ({len(superlatives)} superlatives/absolutes)"
        )

    
    if not entities:
        flags.append("No named entities found — unusual for a news article")

    
    if label_counts.get("ORG", 0) == 0:
        flags.append("No organizations/sources mentioned")

    return flags


def _empty_entity_result() -> dict:
    
    return {
        "entities": [],
        "entity_counts": {},
        "persons": [],
        "organizations": [],
        "locations": [],
        "suspicious_patterns": ["Entity extraction unavailable (spaCy model not loaded)"],
    }
