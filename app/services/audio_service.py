"""
Audio processing service for speech-to-text and text-to-speech
"""
import asyncio
import io
import numpy as np
import pyaudio
import speech_recognition as sr
from pydub import AudioSegment
from pydub.effects import normalize
from google.cloud import speech
from google.cloud import texttospeech
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AudioService:
    """Audio processing service"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Google Cloud Speech client
        self.speech_client = speech.SpeechClient()
        
        # Google Cloud Text-to-Speech client
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # Audio configuration
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.chunk_size = settings.AUDIO_CHUNK_SIZE
        
    async def speech_to_text(self, audio_data: bytes, language: str = "en-US") -> str:
        """Convert speech to text using Google Cloud Speech-to-Text"""
        try:
            # Convert bytes to audio segment
            audio_segment = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Normalize audio
            audio_segment = normalize(audio_segment)
            
            # Convert to the required format
            audio_segment = audio_segment.set_frame_rate(self.sample_rate)
            audio_segment = audio_segment.set_channels(1)  # Mono
            
            # Convert to bytes
            audio_bytes = audio_segment.raw_data
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code=language,
                enable_automatic_punctuation=True,
                model="latest_long"
            )
            
            audio = speech.RecognitionAudio(content=audio_bytes)
            
            # Perform recognition
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                return response.results[0].alternatives[0].transcript
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return ""
    
    async def text_to_speech(self, text: str, language: str = "en-US", voice_name: str = None) -> bytes:
        """Convert text to speech using Google Cloud Text-to-Speech"""
        try:
            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            if voice_name:
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language,
                    name=voice_name
                )
            else:
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language,
                    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                )
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate
            )
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return b""
    
    async def get_available_voices(self, language: str = "en-US") -> list:
        """Get available voices for a language"""
        try:
            voices = self.tts_client.list_voices()
            
            available_voices = []
            for voice in voices.voices:
                if language in voice.language_codes:
                    available_voices.append({
                        "name": voice.name,
                        "language": voice.language_codes[0],
                        "gender": voice.ssml_gender.name
                    })
            
            return available_voices
            
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    async def process_audio_stream(self, audio_stream, language: str = "en-US"):
        """Process continuous audio stream"""
        try:
            # Configure streaming recognition
            config = speech.StreamingRecognitionConfig(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate,
                    language_code=language,
                    enable_automatic_punctuation=True
                ),
                interim_results=True
            )
            
            # Create streaming request
            requests = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in audio_stream)
            responses = self.speech_client.streaming_recognize(config, requests)
            
            # Process responses
            for response in responses:
                if response.results:
                    result = response.results[0]
                    if result.is_final:
                        yield result.alternatives[0].transcript
                        
        except Exception as e:
            logger.error(f"Streaming recognition error: {e}")
            yield ""
    
    def get_audio_format(self) -> dict:
        """Get audio format configuration"""
        return {
            "sample_rate": self.sample_rate,
            "channels": 1,
            "format": "int16",
            "chunk_size": self.chunk_size
        }