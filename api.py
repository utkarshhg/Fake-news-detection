

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import jwt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from loguru import logger

from src.config import SECRET_KEY, PROJ_ROOT


app = FastAPI(title="Fake News Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


from src.database.db import init_db
init_db()






class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "reporter"

class AnalyzeRequest(BaseModel):
    text: str = ""
    url: str = ""
    model_name: str = "lightgbm"

class UpdateRoleRequest(BaseModel):
    role: str

class ReviewFlagRequest(BaseModel):
    status: str
    notes: str = ""

class TokenResponse(BaseModel):
    token: str
    user: dict






def create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(user: dict = Depends(decode_token)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user






@app.post("/api/auth/login")
def login(req: LoginRequest):
    from src.auth.auth import authenticate_user
    result = authenticate_user(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    user = result["user"]
    token = create_token(user.id, user.username, user.role)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }


@app.post("/api/auth/register")
def register(req: RegisterRequest):
    from src.auth.auth import register_user
    result = register_user(req.username, req.email, req.password, req.role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {"success": True, "message": result["message"]}






@app.post("/api/analyze")
def analyze_article(req: AnalyzeRequest, user: dict = Depends(decode_token)):
    text = req.text
    article_url = req.url or None
    article_title = None

    
    if not text and article_url:
        try:
            from newspaper import Article
            article = Article(article_url)
            article.download()
            article.parse()
            text = article.text
            article_title = article.title
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch article: {e}")

    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Article text is too short")

    results = {}

    
    from src.nlp.language import detect_language, translate_to_english
    lang_result = detect_language(text)
    results["language"] = lang_result

    analysis_text = text
    if lang_result["code"] != "en" and lang_result["is_supported"]:
        trans_result = translate_to_english(text, lang_result["code"])
        if trans_result["was_translated"]:
            analysis_text = trans_result["translated_text"]
            results["language"]["was_translated"] = True

    
    try:
        from src.modeling.predict import predict_text
        ml_result = predict_text(analysis_text, model_name=req.model_name)
    except FileNotFoundError:
        ml_result = {
            "label": "UNAVAILABLE",
            "confidence": 0.0,
            "fake_probability": 0.5,
            "real_probability": 0.5,
            "model_used": req.model_name,
        }
    results["ml_prediction"] = ml_result

    
    from src.nlp.sentiment import analyze_sentiment
    results["sentiment"] = analyze_sentiment(analysis_text)

    
    from src.nlp.entities import extract_entities, extract_keywords
    results["entities"] = extract_entities(analysis_text)
    results["keywords"] = extract_keywords(analysis_text)

    
    from src.nlp.classifier import classify_content_type
    results["classification"] = classify_content_type(analysis_text, ml_prediction=ml_result)

    
    from src.nlp.verification import verify_against_sources
    results["verification"] = verify_against_sources(analysis_text, results["keywords"])

    
    from src.nlp.credibility import compute_credibility_score
    results["credibility"] = compute_credibility_score(
        ml_prediction=ml_result,
        sentiment_result=results["sentiment"],
        classification_result=results["classification"],
        entity_result=results["entities"],
        verification_result=results["verification"],
    )

    
    analysis_id = None
    try:
        from src.database.db import save_analysis
        record = save_analysis(
            article_text=text,
            results=results,
            user_id=user.get("user_id"),
            article_url=article_url,
            article_title=article_title,
        )
        analysis_id = record.id
    except Exception as e:
        logger.warning(f"Failed to save analysis: {e}")

    results["analysis_id"] = analysis_id
    return results






@app.get("/api/dashboard/stats")
def get_dashboard_stats(user: dict = Depends(decode_token)):
    from src.database.db import get_analysis_stats, get_analysis_history
    stats = get_analysis_stats()

    
    history = get_analysis_history(limit=200)
    scores = [h.credibility_score for h in history if h.credibility_score is not None]
    stats["score_distribution"] = scores

    return stats






@app.get("/api/history")
def get_history(
    limit: int = 50,
    risk_level: Optional[str] = None,
    language: Optional[str] = None,
    user: dict = Depends(decode_token),
):
    from src.database.db import get_analysis_history
    from src.auth.auth import has_permission

    user_id = None
    if not has_permission(user.get("role", "reporter"), "researcher"):
        user_id = user.get("user_id")

    records = get_analysis_history(
        user_id=user_id,
        limit=limit,
        risk_level=risk_level if risk_level != "All" else None,
        language=language if language != "All" else None,
    )

    return [
        {
            "id": h.id,
            "date": h.created_at.isoformat() if h.created_at else None,
            "prediction": h.prediction_label,
            "confidence": h.prediction_confidence,
            "credibility": h.credibility_score,
            "risk": h.risk_level,
            "content_type": h.content_type,
            "language": h.language_detected,
            "sentiment": h.sentiment_label,
            "text_preview": (h.article_text or "")[:100],
        }
        for h in records
    ]


@app.get("/api/history/{analysis_id}")
def get_history_detail(analysis_id: int, user: dict = Depends(decode_token)):
    from src.database.db import get_analysis_by_id
    record = get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": record.id,
        "date": record.created_at.isoformat() if record.created_at else None,
        "prediction": record.prediction_label,
        "confidence": record.prediction_confidence,
        "credibility": record.credibility_score,
        "risk": record.risk_level,
        "content_type": record.content_type,
        "language": record.language_detected,
        "sentiment": record.sentiment_label,
        "article_text": record.article_text,
        "article_url": record.article_url,
        "flags": record.flags_json,
    }






@app.get("/api/admin/users")
def admin_get_users(user: dict = Depends(require_admin)):
    from src.database.db import get_all_users
    users = get_all_users()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login": u.last_login.isoformat() if u.last_login else None,
        }
        for u in users
    ]


@app.put("/api/admin/users/{user_id}/role")
def admin_update_role(user_id: int, req: UpdateRoleRequest, user: dict = Depends(require_admin)):
    from src.database.db import update_user_role
    if not update_user_role(user_id, req.role):
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}


@app.put("/api/admin/users/{user_id}/toggle")
def admin_toggle_active(user_id: int, user: dict = Depends(require_admin)):
    from src.database.db import toggle_user_active
    if not toggle_user_active(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}


@app.get("/api/admin/metrics")
def admin_get_metrics(user: dict = Depends(require_admin)):
    metrics_path = PROJ_ROOT / "metrics.json"
    if not metrics_path.exists():
        return {"metrics": None, "roc_curves": []}

    with open(metrics_path) as f:
        metrics = json.load(f)

    
    figures_dir = PROJ_ROOT / "reports" / "figures"
    roc_curves = []
    if figures_dir.exists():
        for roc_path in figures_dir.glob("*_roc.png"):
            roc_curves.append(roc_path.stem)

    return {"metrics": metrics, "roc_curves": roc_curves}


@app.get("/api/admin/flagged")
def admin_get_flagged(status_filter: Optional[str] = None, user: dict = Depends(require_admin)):
    from src.database.db import get_flagged_articles
    flagged = get_flagged_articles(status=status_filter if status_filter != "All" else None)
    return [
        {
            "id": f.id,
            "analysis_id": f.analysis_id,
            "reason": f.reason,
            "status": f.status,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in flagged
    ]


@app.put("/api/admin/flagged/{flag_id}")
def admin_review_flag(flag_id: int, req: ReviewFlagRequest, user: dict = Depends(require_admin)):
    from src.database.db import review_flagged_article
    review_flagged_article(flag_id, req.status, user.get("user_id"), req.notes)
    return {"success": True}






frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
