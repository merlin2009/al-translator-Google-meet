"""
Translation service using Google Cloud Translate
"""
import asyncio
import logging
from typing import Dict, List, Optional
from google.cloud import translate_v2 as translate
from app.core.config import settings

logger = logging.getLogger(__name__)

class TranslationService:
    """Translation service using Google Cloud Translate"""
    
    def __init__(self):
        self.translate_client = translate.Client()
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.default_source = settings.DEFAULT_SOURCE_LANGUAGE
        self.default_target = settings.DEFAULT_TARGET_LANGUAGE
        
    async def translate(self, text: str, source_language: str = None, target_language: str = None) -> str:
        """Translate text from source to target language"""
        try:
            if not source_language:
                source_language = self.default_source
            if not target_language:
                target_language = self.default_target
                
            # Detect language if source is not specified
            if source_language == "auto":
                detected_language = await self.detect_language(text)
                source_language = detected_language
            
            # Skip translation if source and target are the same
            if source_language == target_language:
                return text
            
            # Perform translation
            result = self.translate_client.translate(
                text,
                source_language=source_language,
                target_language=target_language
            )
            
            return result['translatedText']
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    async def detect_language(self, text: str) -> str:
        """Detect language of the text"""
        try:
            result = self.translate_client.detect_language(text)
            return result['language']
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return self.default_source
    
    async def translate_batch(self, texts: List[str], source_language: str = None, target_language: str = None) -> List[str]:
        """Translate multiple texts"""
        try:
            if not source_language:
                source_language = self.default_source
            if not target_language:
                target_language = self.default_target
            
            # Skip translation if source and target are the same
            if source_language == target_language:
                return texts
            
            # Perform batch translation
            results = self.translate_client.translate(
                texts,
                source_language=source_language,
                target_language=target_language
            )
            
            return [result['translatedText'] for result in results]
            
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            return texts
    
    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        try:
            results = self.translate_client.get_languages()
            return [
                {
                    "code": lang["language"],
                    "name": lang["name"]
                }
                for lang in results
            ]
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            return []
    
    async def get_language_name(self, language_code: str) -> str:
        """Get language name from code"""
        try:
            languages = await self.get_supported_languages()
            for lang in languages:
                if lang["code"] == language_code:
                    return lang["name"]
            return language_code
        except Exception as e:
            logger.error(f"Error getting language name: {e}")
            return language_code
    
    async def translate_with_confidence(self, text: str, source_language: str = None, target_language: str = None) -> Dict[str, any]:
        """Translate text with confidence score"""
        try:
            if not source_language:
                source_language = self.default_source
            if not target_language:
                target_language = self.default_target
            
            # Detect language if source is not specified
            if source_language == "auto":
                detected = await self.detect_language(text)
                source_language = detected
            
            # Skip translation if source and target are the same
            if source_language == target_language:
                return {
                    "original": text,
                    "translated": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": 1.0
                }
            
            # Perform translation
            result = self.translate_client.translate(
                text,
                source_language=source_language,
                target_language=target_language
            )
            
            return {
                "original": text,
                "translated": result['translatedText'],
                "source_language": result['detectedSourceLanguage'] if 'detectedSourceLanguage' in result else source_language,
                "target_language": target_language,
                "confidence": result.get('confidence', 0.8)
            }
            
        except Exception as e:
            logger.error(f"Translation with confidence error: {e}")
            return {
                "original": text,
                "translated": text,
                "source_language": source_language or self.default_source,
                "target_language": target_language or self.default_target,
                "confidence": 0.0
            }
    
    async def is_supported_language(self, language_code: str) -> bool:
        """Check if language is supported"""
        try:
            languages = await self.get_supported_languages()
            return any(lang["code"] == language_code for lang in languages)
        except Exception as e:
            logger.error(f"Error checking supported language: {e}")
            return False