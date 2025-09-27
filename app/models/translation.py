"""
Translation models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class TranslationSession(Base):
    """Translation session model"""
    __tablename__ = "translation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    source_language = Column(String, default="en")
    target_language = Column(String, default="ru")
    platform = Column(String)  # discord, zoom, meet
    user_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TranslationHistory(Base):
    """Translation history model"""
    __tablename__ = "translation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    original_text = Column(Text)
    translated_text = Column(Text)
    source_language = Column(String)
    target_language = Column(String)
    confidence = Column(Integer)  # Translation confidence score
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class UserSettings(Base):
    """User settings model"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    preferred_languages = Column(Text)  # JSON string
    auto_translate = Column(Boolean, default=True)
    voice_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())