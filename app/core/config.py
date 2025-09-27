"""
Application configuration
"""
import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/translation_service"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_CLOUD_PROJECT_ID: str = ""
    
    # Discord
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: str = ""
    
    # Zoom
    ZOOM_API_KEY: str = ""
    ZOOM_API_SECRET: str = ""
    
    # Google Meet
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Application
    SECRET_KEY: str = "your-secret-key-here"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Translation
    DEFAULT_SOURCE_LANGUAGE: str = "en"
    DEFAULT_TARGET_LANGUAGE: str = "ru"
    SUPPORTED_LANGUAGES: List[str] = ["en", "ru", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"]
    
    # Audio
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_SIZE: int = 1024
    MAX_AUDIO_DURATION: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()