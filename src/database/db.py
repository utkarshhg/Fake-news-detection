

import os
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, Session

from src.config import DATABASE_URL, DB_DIR
from src.database.models import Base, User, AnalysisHistory, FlaggedArticle


_engine = None
_SessionFactory = None


def get_engine():
    
    global _engine
    if _engine is None:
        
        DB_DIR.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(DATABASE_URL, echo=False)
        logger.info(f"Database engine created: {DATABASE_URL}")
    return _engine


def get_session() -> Session:
    
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory()


def init_db():
    
    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("Database tables created/verified.")

    
    session = get_session()
    try:
        user_count = session.query(User).count()
        if user_count == 0:
            _seed_admin(session)
    finally:
        session.close()


def _seed_admin(session: Session):
    
    from src.auth.auth import hash_password

    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    email = os.getenv("ADMIN_EMAIL", "admin@fakenews.local")

    admin = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role="admin",
    )
    session.add(admin)
    session.commit()
    logger.info(f"Admin user '{username}' created.")




def create_user(username: str, email: str, password_hash: str, role: str = "reporter") -> User:
    
    session = get_session()
    try:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"User '{username}' created with role '{role}'.")
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create user: {e}")
        raise
    finally:
        session.close()


def get_user_by_username(username: str) -> Optional[User]:
    
    session = get_session()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    
    session = get_session()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()


def get_all_users() -> list[User]:
    
    session = get_session()
    try:
        return session.query(User).order_by(User.created_at.desc()).all()
    finally:
        session.close()


def update_user_role(user_id: int, new_role: str) -> bool:
    
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.role = new_role
            session.commit()
            return True
        return False
    finally:
        session.close()


def update_last_login(user_id: int):
    
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.now(timezone.utc)
            session.commit()
    finally:
        session.close()


def toggle_user_active(user_id: int) -> bool:
    
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = not user.is_active
            session.commit()
            return True
        return False
    finally:
        session.close()




def save_analysis(
    article_text: str,
    results: dict,
    user_id: int = None,
    article_url: str = None,
    article_title: str = None,
) -> AnalysisHistory:
    
    session = get_session()
    try:
        ml = results.get("ml_prediction", {})
        sentiment = results.get("sentiment", {})
        credibility = results.get("credibility", {})
        language = results.get("language", {})

        record = AnalysisHistory(
            user_id=user_id,
            article_text=article_text[:10000],  
            article_url=article_url,
            article_title=article_title,
            language_detected=language.get("code", "en"),
            was_translated=language.get("was_translated", False),
            prediction_label=ml.get("label"),
            prediction_confidence=ml.get("confidence"),
            model_used=ml.get("model_used"),
            credibility_score=credibility.get("score"),
            risk_level=credibility.get("risk_level"),
            content_type=results.get("classification", {}).get("primary_type"),
            sentiment_polarity=sentiment.get("polarity"),
            sentiment_subjectivity=sentiment.get("subjectivity"),
            sentiment_label=sentiment.get("sentiment_label"),
            entities_json=results.get("entities"),
            keywords_json=results.get("keywords"),
            verification_json=results.get("verification"),
            classification_json=results.get("classification"),
            credibility_breakdown_json=credibility.get("breakdown"),
            flags_json=credibility.get("flags"),
        )

        session.add(record)
        session.commit()
        session.refresh(record)
        logger.info(f"Analysis saved (id={record.id})")
        return record
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save analysis: {e}")
        raise
    finally:
        session.close()


def get_analysis_history(
    user_id: int = None,
    limit: int = 50,
    offset: int = 0,
    risk_level: str = None,
    language: str = None,
) -> list[AnalysisHistory]:
    
    session = get_session()
    try:
        query = session.query(AnalysisHistory)

        if user_id:
            query = query.filter(AnalysisHistory.user_id == user_id)
        if risk_level:
            query = query.filter(AnalysisHistory.risk_level == risk_level)
        if language:
            query = query.filter(AnalysisHistory.language_detected == language)

        return (
            query.order_by(desc(AnalysisHistory.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
    finally:
        session.close()


def get_analysis_by_id(analysis_id: int) -> Optional[AnalysisHistory]:
    
    session = get_session()
    try:
        return session.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    finally:
        session.close()


def get_analysis_stats() -> dict:
    
    session = get_session()
    try:
        total = session.query(AnalysisHistory).count()
        if total == 0:
            return {
                "total_analyses": 0,
                "avg_credibility": 0,
                "risk_distribution": {},
                "label_distribution": {},
                "language_distribution": {},
                "content_type_distribution": {},
            }

        avg_score = session.query(func.avg(AnalysisHistory.credibility_score)).scalar() or 0

        
        risk_counts = (
            session.query(AnalysisHistory.risk_level, func.count())
            .group_by(AnalysisHistory.risk_level)
            .all()
        )

        
        label_counts = (
            session.query(AnalysisHistory.prediction_label, func.count())
            .group_by(AnalysisHistory.prediction_label)
            .all()
        )

        
        lang_counts = (
            session.query(AnalysisHistory.language_detected, func.count())
            .group_by(AnalysisHistory.language_detected)
            .all()
        )

        
        type_counts = (
            session.query(AnalysisHistory.content_type, func.count())
            .group_by(AnalysisHistory.content_type)
            .all()
        )

        return {
            "total_analyses": total,
            "avg_credibility": round(float(avg_score), 1),
            "risk_distribution": {r: c for r, c in risk_counts if r},
            "label_distribution": {l: c for l, c in label_counts if l},
            "language_distribution": {la: c for la, c in lang_counts if la},
            "content_type_distribution": {t: c for t, c in type_counts if t},
        }
    finally:
        session.close()




def flag_article(analysis_id: int, user_id: int = None, reason: str = None) -> FlaggedArticle:
    
    session = get_session()
    try:
        flag = FlaggedArticle(
            analysis_id=analysis_id,
            flagged_by=user_id,
            reason=reason,
        )
        session.add(flag)
        session.commit()
        session.refresh(flag)
        return flag
    finally:
        session.close()


def get_flagged_articles(status: str = None) -> list[FlaggedArticle]:
    
    session = get_session()
    try:
        query = session.query(FlaggedArticle)
        if status:
            query = query.filter(FlaggedArticle.status == status)
        return query.order_by(desc(FlaggedArticle.created_at)).all()
    finally:
        session.close()


def review_flagged_article(flag_id: int, status: str, reviewer_id: int, notes: str = None):
    
    session = get_session()
    try:
        flag = session.query(FlaggedArticle).filter(FlaggedArticle.id == flag_id).first()
        if flag:
            flag.status = status
            flag.reviewed_by = reviewer_id
            flag.review_notes = notes
            flag.reviewed_at = datetime.now(timezone.utc)
            session.commit()
    finally:
        session.close()
