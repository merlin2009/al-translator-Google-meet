"""
Zoom SDK integration for real-time translation
"""
import asyncio
import logging
import httpx
import json
from typing import Dict, List, Optional
from app.core.config import settings
from app.services.translation_service import TranslationService
from app.services.audio_service import AudioService

logger = logging.getLogger(__name__)

class ZoomService:
    """Zoom SDK integration for translation"""
    
    def __init__(self):
        self.api_key = settings.ZOOM_API_KEY
        self.api_secret = settings.ZOOM_API_SECRET
        self.base_url = "https://api.zoom.us/v2"
        self.translation_service = TranslationService()
        self.audio_service = AudioService()
        self.active_meetings = {}
        
    async def create_meeting(self, topic: str, duration: int = 60) -> Dict:
        """Create a Zoom meeting with translation capabilities"""
        try:
            headers = {
                "Authorization": f"Bearer {await self.get_access_token()}",
                "Content-Type": "application/json"
            }
            
            meeting_data = {
                "topic": f"{topic} - Real-time Translation",
                "type": 2,  # Scheduled meeting
                "duration": duration,
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "audio": "both",
                    "auto_recording": "cloud",
                    "waiting_room": False,
                    "join_before_host": True
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/users/me/meetings",
                    headers=headers,
                    json=meeting_data
                )
                
                if response.status_code == 201:
                    meeting_info = response.json()
                    meeting_id = meeting_info["id"]
                    
                    # Store meeting info
                    self.active_meetings[meeting_id] = {
                        "meeting_info": meeting_info,
                        "participants": [],
                        "translation_enabled": True,
                        "source_language": "en",
                        "target_language": "ru"
                    }
                    
                    return meeting_info
                else:
                    logger.error(f"Failed to create meeting: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating Zoom meeting: {e}")
            return None
    
    async def get_access_token(self) -> str:
        """Get Zoom API access token"""
        try:
            # In production, implement proper OAuth2 flow
            # For now, return a placeholder
            return "your_access_token_here"
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return ""
    
    async def join_meeting(self, meeting_id: str, user_id: str) -> Dict:
        """Join a Zoom meeting"""
        try:
            if meeting_id not in self.active_meetings:
                return {"error": "Meeting not found"}
            
            meeting = self.active_meetings[meeting_id]
            
            # Add participant
            participant = {
                "user_id": user_id,
                "joined_at": asyncio.get_event_loop().time(),
                "translation_preferences": {
                    "source_language": "en",
                    "target_language": "ru"
                }
            }
            
            meeting["participants"].append(participant)
            
            return {
                "meeting_id": meeting_id,
                "join_url": meeting["meeting_info"]["join_url"],
                "translation_enabled": True
            }
            
        except Exception as e:
            logger.error(f"Error joining meeting: {e}")
            return {"error": str(e)}
    
    async def process_audio(self, meeting_id: str, audio_data: bytes, user_id: str) -> Dict:
        """Process audio from Zoom meeting for translation"""
        try:
            if meeting_id not in self.active_meetings:
                return {"error": "Meeting not found"}
            
            meeting = self.active_meetings[meeting_id]
            
            # Find participant
            participant = next(
                (p for p in meeting["participants"] if p["user_id"] == user_id),
                None
            )
            
            if not participant:
                return {"error": "Participant not found"}
            
            # Convert speech to text
            text = await self.audio_service.speech_to_text(
                audio_data,
                participant["translation_preferences"]["source_language"]
            )
            
            if not text:
                return {"error": "No speech detected"}
            
            # Translate text
            translated = await self.translation_service.translate(
                text,
                participant["translation_preferences"]["source_language"],
                participant["translation_preferences"]["target_language"]
            )
            
            # Generate audio for translation
            translated_audio = await self.audio_service.text_to_speech(
                translated,
                participant["translation_preferences"]["target_language"]
            )
            
            return {
                "original_text": text,
                "translated_text": translated,
                "translated_audio": translated_audio,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return {"error": str(e)}
    
    async def set_translation_language(self, meeting_id: str, user_id: str, source_lang: str, target_lang: str) -> Dict:
        """Set translation language for a participant"""
        try:
            if meeting_id not in self.active_meetings:
                return {"error": "Meeting not found"}
            
            meeting = self.active_meetings[meeting_id]
            
            # Find participant
            participant = next(
                (p for p in meeting["participants"] if p["user_id"] == user_id),
                None
            )
            
            if not participant:
                return {"error": "Participant not found"}
            
            # Update translation preferences
            participant["translation_preferences"]["source_language"] = source_lang
            participant["translation_preferences"]["target_language"] = target_lang
            
            return {
                "success": True,
                "source_language": source_lang,
                "target_language": target_lang
            }
            
        except Exception as e:
            logger.error(f"Error setting translation language: {e}")
            return {"error": str(e)}
    
    async def get_meeting_participants(self, meeting_id: str) -> List[Dict]:
        """Get list of meeting participants"""
        try:
            if meeting_id not in self.active_meetings:
                return []
            
            meeting = self.active_meetings[meeting_id]
            return meeting["participants"]
            
        except Exception as e:
            logger.error(f"Error getting participants: {e}")
            return []
    
    async def end_meeting(self, meeting_id: str) -> Dict:
        """End a Zoom meeting"""
        try:
            if meeting_id in self.active_meetings:
                del self.active_meetings[meeting_id]
                return {"success": True, "message": "Meeting ended"}
            else:
                return {"error": "Meeting not found"}
                
        except Exception as e:
            logger.error(f"Error ending meeting: {e}")
            return {"error": str(e)}
    
    async def get_meeting_info(self, meeting_id: str) -> Dict:
        """Get meeting information"""
        try:
            if meeting_id not in self.active_meetings:
                return {"error": "Meeting not found"}
            
            meeting = self.active_meetings[meeting_id]
            return {
                "meeting_info": meeting["meeting_info"],
                "participants": meeting["participants"],
                "translation_enabled": meeting["translation_enabled"]
            }
            
        except Exception as e:
            logger.error(f"Error getting meeting info: {e}")
            return {"error": str(e)}