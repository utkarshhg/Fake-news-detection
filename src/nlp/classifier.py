

import re
from loguru import logger




CLICKBAIT_PATTERNS = [
    r'\b(you won\'?t believe|what happens next|this will shock|mind-?blowing)\b',
    r'\b(number \d+ will|top \d+ |the \d+ best|the \d+ worst)\b',
    r'\b(one weird trick|doctors hate|they don\'?t want you to know)\b',
    r'\b(is this the end|exposed|revealed|secrets? of)\b',
    r'^(how to|why you should|what you need to know)\b',
    r'[!?]{2,}',  
    r'\b(jaw-?dropping|game-?changer|life-?changing|insane|crazy)\b',
]

PROPAGANDA_PATTERNS = [
    r'\b(enemy of the people|deep state|controlled media|fake mainstream)\b',
    r'\b(they are lying|cover-?up|conspiracy|wake up|sheep|sheeple)\b',
    r'\b(evil|destroy|attack on|threat to|agenda|puppet|traitor)\b',
    r'\b(patriot|true american|real citizen|fighting for)\b',
    r'\b(banned|censored|they removed|they don\'?t want)\b',
    r'\b(globalist|puppet master|new world order|illuminati)\b',
]

HATE_SPEECH_PATTERNS = [
    r'\b(go back to|all \w+ are|these people|those people)\b',
    r'\b(invasion|infest|plague|vermin|parasite|scum|filth)\b',
    r'\b(sub-?human|inferior|primitive|savage|barbaric)\b',
    r'\b(not welcome|take over|breeding|replacement|purge)\b',
]

SATIRE_PATTERNS = [
    r'\b(satirical|satire|parody|humor|comedic|joke|onion)\b',
    r'\b(area man|local man|local woman|sources say|reportedly)\b',
    r'\b(definitely|totally|absolutely|clearly)\b.*\b(not|never|no)\b',
]

AI_GENERATED_PATTERNS = [
    r'\b(as an ai|i am an ai|language model|as a language model)\b',
    r'\b(in conclusion|it is important to note|it\'?s worth noting)\b',
    
    r'\b(furthermore|moreover|additionally|consequently)\b',
]


def classify_content_type(
    text: str,
    ml_prediction: dict = None,
) -> dict:
    
    if not text or not text.strip():
        return _empty_result()

    text_lower = text.lower()
    results = {}

    
    results["clickbait"] = _score_patterns(text_lower, CLICKBAIT_PATTERNS, "Clickbait")
    results["propaganda"] = _score_patterns(text_lower, PROPAGANDA_PATTERNS, "Propaganda")
    results["hate_speech"] = _score_patterns(text_lower, HATE_SPEECH_PATTERNS, "Hate Speech")
    results["satire"] = _score_patterns(text_lower, SATIRE_PATTERNS, "Satire")
    results["ai_generated"] = _score_ai_generated(text_lower)

    
    if ml_prediction:
        fake_prob = ml_prediction.get("fake_probability", 0.5)
        results["fake_news"] = {
            "score": round(fake_prob, 4),
            "label": "Fake News",
            "evidence": [f"ML model confidence: {fake_prob:.1%}"],
        }
        results["real_news"] = {
            "score": round(1 - fake_prob, 4),
            "label": "Real News",
            "evidence": [f"ML model confidence: {1 - fake_prob:.1%}"],
        }
    else:
        results["fake_news"] = {"score": 0.0, "label": "Fake News", "evidence": []}
        results["real_news"] = {"score": 0.0, "label": "Real News", "evidence": []}

    
    
    THRESHOLD = 0.3
    detected = [
        {"type": key, "score": val["score"], "label": val["label"]}
        for key, val in results.items()
        if val["score"] >= THRESHOLD
    ]
    detected.sort(key=lambda x: x["score"], reverse=True)

    if detected:
        primary_type = detected[0]["label"]
    else:
        primary_type = "Undetermined"

    
    risk_indicators = []
    for key, val in results.items():
        if val["score"] >= THRESHOLD and key not in ("real_news",):
            risk_indicators.extend(val["evidence"])

    return {
        "primary_type": primary_type,
        "types_detected": detected,
        "details": results,
        "risk_indicators": risk_indicators,
    }


def _score_patterns(text: str, patterns: list, label: str) -> dict:
    
    total_matches = 0
    evidence = []

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            total_matches += len(matches)
            
            sample = matches[0] if isinstance(matches[0], str) else str(matches[0])
            evidence.append(f'Pattern match: "{sample}"')

    
    score = min(total_matches / 5.0, 1.0)

    return {
        "score": round(score, 4),
        "label": label,
        "evidence": evidence[:5],  
    }


def _score_ai_generated(text: str) -> dict:
    
    evidence = []
    score = 0.0

    
    pattern_result = _score_patterns(text, AI_GENERATED_PATTERNS, "AI-Generated")
    score += pattern_result["score"] * 0.5
    evidence.extend(pattern_result["evidence"])

    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if len(sentences) >= 5:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)

        
        if variance < 15 and avg_len > 10:
            score += 0.3
            evidence.append(
                f"Very uniform sentence length (avg={avg_len:.0f} words, var={variance:.1f})"
            )

    
    transitions = re.findall(
        r'\b(furthermore|moreover|additionally|consequently|nevertheless|'
        r'in addition|on the other hand|in conclusion|it is worth)\b',
        text
    )
    if len(transitions) > 5:
        score += 0.2
        evidence.append(f"Excessive formal transitions ({len(transitions)} found)")

    return {
        "score": round(min(score, 1.0), 4),
        "label": "AI-Generated",
        "evidence": evidence[:5],
    }


def _empty_result() -> dict:
    return {
        "primary_type": "Unknown",
        "types_detected": [],
        "details": {},
        "risk_indicators": [],
    }
