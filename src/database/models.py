

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    Boolean, ForeignKey, JSON, create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="reporter")  
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)

    
    analyses = relationship("AnalysisHistory", back_populates="user", lazy="dynamic")
    flagged_articles = relationship("FlaggedArticle", back_populates="flagged_by_user", lazy="dynamic")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class AnalysisHistory(Base):
    

    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    
    article_text = Column(Text, nullable=False)
    article_url = Column(String(500), nullable=True)
    article_title = Column(String(500), nullable=True)

    
    language_detected = Column(String(20), default="en")
    was_translated = Column(Boolean, default=False)

    
    prediction_label = Column(String(20), nullable=True)  
    prediction_confidence = Column(Float, nullable=True)
    model_used = Column(String(50), nullable=True)

    
    credibility_score = Column(Integer, nullable=True)  
    risk_level = Column(String(20), nullable=True)  

    
    content_type = Column(String(50), nullable=True)  

    
    sentiment_polarity = Column(Float, nullable=True)
    sentiment_subjectivity = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)

    
    entities_json = Column(JSON, nullable=True)
    keywords_json = Column(JSON, nullable=True)
    verification_json = Column(JSON, nullable=True)
    classification_json = Column(JSON, nullable=True)
    credibility_breakdown_json = Column(JSON, nullable=True)
    flags_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    
    user = relationship("User", back_populates="analyses")
    flags = relationship("FlaggedArticle", back_populates="analysis", lazy="dynamic")

    def __repr__(self):
        return (
            f"<AnalysisHistory(id={self.id}, label='{self.prediction_label}', "
            f"score={self.credibility_score})>"
        )


class FlaggedArticle(Base):
    

    __tablename__ = "flagged_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analysis_history.id"), nullable=False)
    flagged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  
    reviewed_by = Column(Integer, nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)

    
    analysis = relationship("AnalysisHistory", back_populates="flags")
    flagged_by_user = relationship("User", back_populates="flagged_articles")

    def __repr__(self):
        return f"<FlaggedArticle(id={self.id}, status='{self.status}')>"
