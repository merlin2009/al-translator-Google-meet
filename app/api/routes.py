"""
API routes for the translation service
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.services.translation_service import TranslationService
from app.services.audio_service import AudioService
from app.services.discord_service import DiscordService
from app.services.zoom_service import ZoomService
from app.services.meet_service import MeetService

router = APIRouter()

# Pydantic models
class TranslationRequest(BaseModel):
    text: str
    source_language: Optional[str] = "en"
    target_language: Optional[str] = "ru"

class TranslationResponse(BaseModel):
    original: str
    translated: str
    source_language: str
    target_language: str
    confidence: float

class MeetingRequest(BaseModel):
    topic: str
    duration: int = 60

class MeetingResponse(BaseModel):
    meeting_id: str
    join_url: str
    translation_enabled: bool

class LanguageRequest(BaseModel):
    source_language: str
    target_language: str

# Initialize services
translation_service = TranslationService()
audio_service = AudioService()
discord_service = DiscordService()
zoom_service = ZoomService()
meet_service = MeetService()

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text from source to target language"""
    try:
        result = await translation_service.translate_with_confidence(
            request.text,
            request.source_language,
            request.target_language
        )
        return TranslationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    try:
        languages = await translation_service.get_supported_languages()
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/discord/start")
async def start_discord_translation(request: LanguageRequest):
    """Start Discord translation session"""
    try:
        # This would integrate with Discord service
        return {"message": "Discord translation started", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/discord/stop")
async def stop_discord_translation():
    """Stop Discord translation session"""
    try:
        return {"message": "Discord translation stopped", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zoom/meeting", response_model=MeetingResponse)
async def create_zoom_meeting(request: MeetingRequest):
    """Create a Zoom meeting with translation"""
    try:
        meeting_info = await zoom_service.create_meeting(request.topic, request.duration)
        if meeting_info:
            return MeetingResponse(
                meeting_id=meeting_info["id"],
                join_url=meeting_info["join_url"],
                translation_enabled=True
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create meeting")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zoom/join/{meeting_id}")
async def join_zoom_meeting(meeting_id: str, user_id: str):
    """Join a Zoom meeting"""
    try:
        result = await zoom_service.join_meeting(meeting_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zoom/audio/{meeting_id}")
async def process_zoom_audio(meeting_id: str, user_id: str, audio_data: bytes):
    """Process audio from Zoom meeting"""
    try:
        result = await zoom_service.process_audio(meeting_id, audio_data, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zoom/language/{meeting_id}")
async def set_zoom_language(meeting_id: str, user_id: str, request: LanguageRequest):
    """Set translation language for Zoom meeting"""
    try:
        result = await zoom_service.set_translation_language(
            meeting_id, user_id, request.source_language, request.target_language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/zoom/participants/{meeting_id}")
async def get_zoom_participants(meeting_id: str):
    """Get Zoom meeting participants"""
    try:
        participants = await zoom_service.get_meeting_participants(meeting_id)
        return {"participants": participants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/meet/meeting", response_model=MeetingResponse)
async def create_meet_meeting(request: MeetingRequest):
    """Create a Google Meet with translation"""
    try:
        meeting_info = await meet_service.create_meeting(request.topic, request.duration)
        if meeting_info:
            return MeetingResponse(
                meeting_id=meeting_info["id"],
                join_url=meeting_info["hangoutLink"],
                translation_enabled=True
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create meeting")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/meet/join/{meeting_id}")
async def join_meet_meeting(meeting_id: str, user_id: str):
    """Join a Google Meet"""
    try:
        result = await meet_service.join_meeting(meeting_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/meet/audio/{meeting_id}")
async def process_meet_audio(meeting_id: str, user_id: str, audio_data: bytes):
    """Process audio from Google Meet"""
    try:
        result = await meet_service.process_audio(meeting_id, audio_data, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/meet/language/{meeting_id}")
async def set_meet_language(meeting_id: str, user_id: str, request: LanguageRequest):
    """Set translation language for Google Meet"""
    try:
        result = await meet_service.set_translation_language(
            meeting_id, user_id, request.source_language, request.target_language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meet/participants/{meeting_id}")
async def get_meet_participants(meeting_id: str):
    """Get Google Meet participants"""
    try:
        participants = await meet_service.get_meeting_participants(meeting_id)
        return {"participants": participants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_service_status():
    """Get service status"""
    try:
        return {
            "status": "online",
            "services": {
                "discord": "online",
                "zoom": "online",
                "meet": "online",
                "translation": "online",
                "audio": "online"
            },
            "supported_languages": len(await translation_service.get_supported_languages())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Service is running"}