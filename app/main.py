"""
Main FastAPI application for real-time translation service
"""
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import uvicorn
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import api_router
from app.services.translation_service import TranslationService
from app.services.audio_service import AudioService
from app.services.discord_service import DiscordService
from app.services.zoom_service import ZoomService
from app.services.meet_service import MeetService

load_dotenv()

# Global services
translation_service = None
audio_service = None
discord_service = None
zoom_service = None
meet_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global translation_service, audio_service, discord_service, zoom_service, meet_service
    
    # Initialize database
    await init_db()
    
    # Initialize services
    translation_service = TranslationService()
    audio_service = AudioService()
    discord_service = DiscordService()
    zoom_service = ZoomService()
    meet_service = MeetService()
    
    # Start background tasks
    asyncio.create_task(discord_service.start())
    
    yield
    
    # Cleanup
    if discord_service:
        await discord_service.stop()

app = FastAPI(
    title="Real-time Translation Service",
    description="Multilingual real-time translation for Discord, Zoom, and Google Meet",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/translation")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time translation"""
    await websocket.accept()
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Process audio and get translation
            if translation_service and audio_service:
                # Convert audio to text
                text = await audio_service.speech_to_text(data)
                
                if text:
                    # Translate text
                    translated_text = await translation_service.translate(text)
                    
                    # Send translation back
                    await websocket.send_json({
                        "original": text,
                        "translated": translated_text,
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )