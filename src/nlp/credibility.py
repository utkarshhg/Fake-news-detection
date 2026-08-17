

from loguru import logger
from src.config import RISK_THRESHOLDS


def compute_credibility_score(
    ml_prediction: dict = None,
    sentiment_result: dict = None,
    classification_result: dict = None,
    entity_result: dict = None,
    verification_result: dict = None,
) -> dict:
    
    breakdown = {}
    all_flags = []

    
    ml_score = 50.0  
    ml_details = "No ML prediction available"

    if ml_prediction:
        real_prob = ml_prediction.get("real_probability", 0.5)
        ml_score = real_prob * 100
        ml_details = (
            f"Model '{ml_prediction.get('model_used', 'unknown')}' predicts "
            f"{ml_prediction.get('label', '?')} with {ml_prediction.get('confidence', 0):.1%} confidence"
        )
        if ml_prediction.get("label") == "FAKE":
            all_flags.append(f"ML model predicts FAKE ({ml_prediction.get('confidence', 0):.1%})")

    breakdown["ml_model"] = {
        "score": round(ml_score, 1),
        "weight": 0.50,
        "weighted_score": round(ml_score * 0.50, 1),
        "details": ml_details,
    }

    
    verify_score = 50.0  
    verify_details = "Not verified against external sources"

    if verification_result:
        if verification_result.get("matching_sources"):
            n_sources = len(verification_result["matching_sources"])
            verify_score = min(50 + n_sources * 15, 100)
            verify_details = f"Found {n_sources} matching trusted source(s)"
        elif verification_result.get("status") == "no_matches":
            verify_score = 30
            verify_details = "No matching sources found — could not verify"
            all_flags.append("Could not verify against trusted sources")
        elif verification_result.get("error"):
            verify_details = f"Verification failed: {verification_result['error']}"

    breakdown["source_verification"] = {
        "score": round(verify_score, 1),
        "weight": 0.10,
        "weighted_score": round(verify_score * 0.10, 1),
        "details": verify_details,
    }

    
    sentiment_score = 75.0  
    sentiment_details = "No sentiment analysis available"

    if sentiment_result:
        if sentiment_result.get("is_suspicious"):
            sentiment_score = 25.0
            sentiment_details = "Suspicious sentiment patterns detected"
            all_flags.extend(sentiment_result.get("flags", []))
        else:
            polarity = abs(sentiment_result.get("polarity", 0))
            subjectivity = sentiment_result.get("subjectivity", 0)

            
            if polarity < 0.3 and subjectivity < 0.4:
                sentiment_score = 90.0
                sentiment_details = "Neutral, objective tone — typical of credible reporting"
            elif polarity < 0.5 and subjectivity < 0.6:
                sentiment_score = 65.0
                sentiment_details = "Moderate bias/subjectivity detected"
            else:
                sentiment_score = 40.0
                sentiment_details = "High emotional charge or subjectivity"
                all_flags.append("Emotionally charged or highly subjective language")

    breakdown["sentiment"] = {
        "score": round(sentiment_score, 1),
        "weight": 0.15,
        "weighted_score": round(sentiment_score * 0.15, 1),
        "details": sentiment_details,
    }

    
    content_score = 75.0  
    content_details = "No content type issues detected"

    if classification_result:
        primary = classification_result.get("primary_type", "")
        risk_types = {"Propaganda", "Clickbait", "Hate Speech", "AI-Generated", "Fake News"}

        if primary in risk_types:
            content_score = 15.0
            content_details = f"Content classified as: {primary}"
            all_flags.append(f"Content type: {primary}")
        elif primary == "Satire":
            content_score = 50.0
            content_details = "Content may be satirical"
            all_flags.append("Possible satire — may not be intended as factual")

        
        risk_indicators = classification_result.get("risk_indicators", [])
        if len(risk_indicators) > 3:
            content_score = max(content_score - 20, 0)
            all_flags.extend(risk_indicators[:3])

    breakdown["content_type"] = {
        "score": round(content_score, 1),
        "weight": 0.15,
        "weighted_score": round(content_score * 0.15, 1),
        "details": content_details,
    }

    
    entity_score = 70.0  
    entity_details = "No entity analysis available"

    if entity_result:
        suspicious = entity_result.get("suspicious_patterns", [])
        if suspicious:
            penalty = len(suspicious) * 15
            entity_score = max(70 - penalty, 10)
            entity_details = f"{len(suspicious)} suspicious pattern(s) found"
            all_flags.extend(suspicious[:3])
        else:
            entity_score = 85.0
            entity_details = "No suspicious patterns in entity usage"

    breakdown["entity_patterns"] = {
        "score": round(entity_score, 1),
        "weight": 0.10,
        "weighted_score": round(entity_score * 0.10, 1),
        "details": entity_details,
    }

    
    final_score = sum(comp["weighted_score"] for comp in breakdown.values())
    final_score = max(0, min(100, round(final_score)))

    
    risk_level, risk_color = _get_risk_level(final_score)

    
    summary = _generate_summary(final_score, risk_level, all_flags)

    return {
        "score": final_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "breakdown": breakdown,
        "flags": all_flags,
        "summary": summary,
    }


def _get_risk_level(score: int) -> tuple[str, str]:
    
    if score <= RISK_THRESHOLDS["critical"]:
        return "Critical", "#FF1744"
    elif score <= RISK_THRESHOLDS["high"]:
        return "High", "#FF6D00"
    elif score <= RISK_THRESHOLDS["medium"]:
        return "Medium", "#FFD600"
    else:
        return "Low", "#00C853"


def _generate_summary(score: int, risk_level: str, flags: list) -> str:
    
    if risk_level == "Critical":
        base = "⛔ This content shows strong indicators of misinformation."
    elif risk_level == "High":
        base = "⚠️ This content has significant credibility concerns."
    elif risk_level == "Medium":
        base = "🔶 This content has some credibility concerns worth noting."
    else:
        base = "✅ This content appears largely credible."

    if flags:
        flag_str = " Key concerns: " + "; ".join(flags[:3])
        if len(flags) > 3:
            flag_str += f" (+{len(flags) - 3} more)"
        return base + flag_str

    return base
