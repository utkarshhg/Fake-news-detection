

import re
import requests
from loguru import logger

from src.config import NEWS_API_KEY



TRUSTED_SOURCES = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    "aljazeera.com", "npr.org", "pbs.org",
    "thehindu.com", "ndtv.com", "hindustantimes.com",
    "indianexpress.com", "timesofindia.indiatimes.com",
}


def verify_against_sources(
    text: str,
    keywords: list[dict] = None,
    max_results: int = 5,
) -> dict:
    
    if not text or not text.strip():
        return _error_result("Empty text provided")

    
    query = _build_query(text, keywords)
    if not query:
        return _error_result("Could not extract meaningful search query")

    
    if NEWS_API_KEY:
        result = _search_newsapi(query, max_results)
        if result["status"] != "error":
            return result

    
    result = _search_google_news_rss(query, max_results)
    return result


def _build_query(text: str, keywords: list[dict] = None) -> str:
    
    if keywords and len(keywords) >= 3:
        
        top_words = [kw["word"] for kw in keywords[:5]]
        return " ".join(top_words)

    
    snippet = text[:500]

    
    words = re.findall(r'\b[a-zA-Z]{4,}\b', snippet.lower())

    
    common_words = {
        "that", "this", "with", "from", "have", "been", "were", "they",
        "their", "about", "would", "could", "should", "also", "which",
        "when", "what", "there", "these", "those", "more", "than",
        "said", "just", "like", "over", "after", "before", "very",
        "some", "many", "much", "most", "other", "into", "only",
    }
    significant = [w for w in words if w not in common_words]

    if not significant:
        return ""

    
    seen = set()
    unique = []
    for w in significant:
        if w not in seen:
            seen.add(w)
            unique.append(w)
        if len(unique) >= 5:
            break

    return " ".join(unique)


def _search_newsapi(query: str, max_results: int) -> dict:
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "pageSize": max_results * 2,  
            "sortBy": "relevancy",
            "language": "en",
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 401:
            logger.warning("NewsAPI key is invalid or expired")
            return _error_result("Invalid NewsAPI key")

        if response.status_code != 200:
            logger.warning(f"NewsAPI returned status {response.status_code}")
            return _error_result(f"NewsAPI error: HTTP {response.status_code}")

        data = response.json()
        articles = data.get("articles", [])

        return _process_articles(articles, query, max_results)

    except requests.exceptions.Timeout:
        return _error_result("NewsAPI request timed out")
    except Exception as e:
        logger.warning(f"NewsAPI search failed: {e}")
        return _error_result(str(e))


def _search_google_news_rss(query: str, max_results: int) -> dict:
    
    try:
        import xml.etree.ElementTree as ET

        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en"

        response = requests.get(url, timeout=10, headers={
            "User-Agent": "FakeNewsDetector/1.0"
        })

        if response.status_code != 200:
            return _error_result(f"Google News RSS error: HTTP {response.status_code}")

        root = ET.fromstring(response.content)
        items = root.findall(".//item")

        articles = []
        for item in items[:max_results * 2]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            source_elem = item.findtext("source", "")
            description = item.findtext("description", "")

            articles.append({
                "title": title,
                "source": {"name": source_elem},
                "url": link,
                "description": description,
            })

        return _process_articles(articles, query, max_results)

    except Exception as e:
        logger.warning(f"Google News RSS search failed: {e}")
        return _error_result(str(e))


def _process_articles(articles: list, query: str, max_results: int) -> dict:
    
    matching_sources = []

    for article in articles:
        source_name = ""
        url = article.get("url", "")

        if isinstance(article.get("source"), dict):
            source_name = article["source"].get("name", "")
        elif isinstance(article.get("source"), str):
            source_name = article["source"]

        
        is_trusted = any(domain in url.lower() for domain in TRUSTED_SOURCES)

        matching_sources.append({
            "title": article.get("title", ""),
            "source": source_name,
            "url": url,
            "description": (article.get("description") or "")[:200],
            "is_trusted": is_trusted,
        })

        if len(matching_sources) >= max_results:
            break

    
    trusted_count = sum(1 for s in matching_sources if s.get("is_trusted"))

    if trusted_count >= 2:
        status = "verified"
        confidence = min(0.5 + trusted_count * 0.15, 0.95)
    elif trusted_count == 1:
        status = "partially_verified"
        confidence = 0.5
    elif matching_sources:
        status = "partially_verified"
        confidence = 0.3
    else:
        status = "no_matches"
        confidence = 0.1

    return {
        "status": status,
        "matching_sources": matching_sources,
        "query_used": query,
        "confidence": round(confidence, 4),
        "error": None,
    }


def _error_result(message: str) -> dict:
    
    return {
        "status": "error",
        "matching_sources": [],
        "query_used": "",
        "confidence": 0.0,
        "error": message,
    }
