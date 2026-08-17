

import re
from loguru import logger

from src.config import SUPPORTED_LANGUAGES


def detect_language(text: str) -> dict:
    
    if not text or not text.strip():
        return {"code": "unknown", "name": "Unknown", "confidence": 0.0, "is_supported": False}

    
    if _is_hinglish(text):
        return {
            "code": "hinglish",
            "name": "Hinglish",
            "confidence": 0.75,
            "is_supported": True,
        }

    
    try:
        from langdetect import detect_langs

        results = detect_langs(text)
        if results:
            top = results[0]
            code = str(top.lang)
            confidence = round(top.prob, 4)

            
            name = SUPPORTED_LANGUAGES.get(code, code.upper())
            is_supported = code in SUPPORTED_LANGUAGES

            return {
                "code": code,
                "name": name,
                "confidence": confidence,
                "is_supported": is_supported,
            }
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")

    return {"code": "unknown", "name": "Unknown", "confidence": 0.0, "is_supported": False}


def translate_to_english(text: str, source_lang: str = "auto") -> dict:
    
    if not text or not text.strip():
        return {
            "translated_text": text,
            "source_language": source_lang,
            "was_translated": False,
            "error": None,
        }

    
    if source_lang == "en":
        return {
            "translated_text": text,
            "source_language": "en",
            "was_translated": False,
            "error": None,
        }

    
    if source_lang == "hinglish":
        translated = _translate_hinglish(text)
        return {
            "translated_text": translated,
            "source_language": "hinglish",
            "was_translated": True,
            "error": None,
        }

    try:
        from deep_translator import GoogleTranslator

        src = source_lang if source_lang != "auto" else "auto"
        translator = GoogleTranslator(source=src, target='en')
        translated = translator.translate(text)

        return {
            "translated_text": translated,
            "source_language": source_lang,
            "was_translated": True,
            "error": None,
        }
    except Exception as e:
        logger.warning(f"Translation failed: {e}. Returning original text.")
        return {
            "translated_text": text,
            "source_language": source_lang,
            "was_translated": False,
            "error": str(e),
        }


def _is_hinglish(text: str) -> bool:
    
    
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    total_alpha = len(re.findall(r'[a-zA-Z\u0900-\u097F]', text))
    if total_alpha == 0:
        return False
    if latin_chars / total_alpha < 0.8:
        return False

    
    hinglish_markers = [
        r'\b(hai|hain|tha|thi|nahi|nhi|kya|kaise|kyun|kyunki)\b',
        r'\b(yeh|woh|koi|sabhi|bahut|bohot|zyada|accha|acha)\b',
        r'\b(karna|karo|karke|kar|raha|rahi|rahe|hua|huya)\b',
        r'\b(sab|log|aur|par|mein|ko|se|ka|ki|ke|ne|ho)\b',
        r'\b(jhootha|jhooth|khabar|samachar|sach|galat)\b',
        r'\b(padho|dekho|suno|batao|bolo|chalo|jao)\b',
    ]

    matches = 0
    text_lower = text.lower()
    for pattern in hinglish_markers:
        matches += len(re.findall(pattern, text_lower))

    
    word_count = len(text.split())
    if word_count == 0:
        return False

    return matches / word_count > 0.1  


def _translate_hinglish(text: str) -> str:
    
    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source='hi', target='en')
        return translator.translate(text)
    except Exception as e:
        logger.warning(f"Hinglish translation failed: {e}")
        return text
