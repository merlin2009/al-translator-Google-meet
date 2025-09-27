"""
Discord bot service for real-time translation
"""
import asyncio
import logging
import discord
from discord.ext import commands
from discord import Intents
from app.core.config import settings
from app.services.translation_service import TranslationService
from app.services.audio_service import AudioService

logger = logging.getLogger(__name__)

class DiscordService:
    """Discord bot service for translation"""
    
    def __init__(self):
        self.bot = None
        self.translation_service = TranslationService()
        self.audio_service = AudioService()
        self.active_sessions = {}
        
    async def start(self):
        """Start Discord bot"""
        try:
            intents = Intents.default()
            intents.message_content = True
            intents.voice_states = True
            
            self.bot = commands.Bot(command_prefix='!', intents=intents)
            
            # Register event handlers
            self.bot.add_listener(self.on_ready)
            self.bot.add_listener(self.on_message)
            self.bot.add_listener(self.on_voice_state_update)
            
            # Register commands
            self.bot.add_command(self.start_translation)
            self.bot.add_command(self.stop_translation)
            self.bot.add_command(self.set_language)
            self.bot.add_command(self.translate_text)
            self.bot.add_command(self.help_translation)
            
            # Start bot
            await self.bot.start(settings.DISCORD_BOT_TOKEN)
            
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
    
    async def stop(self):
        """Stop Discord bot"""
        if self.bot:
            await self.bot.close()
    
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f'{self.bot.user} has connected to Discord!')
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="for translation requests"))
    
    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author == self.bot.user:
            return
        
        # Check if user has active translation session
        user_id = str(message.author.id)
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            
            # Translate message
            translated = await self.translation_service.translate(
                message.content,
                session['source_language'],
                session['target_language']
            )
            
            # Send translation
            embed = discord.Embed(
                title="Translation",
                description=f"**Original:** {message.content}\n**Translated:** {translated}",
                color=0x00ff00
            )
            embed.set_footer(text=f"From {session['source_language']} to {session['target_language']}")
            
            await message.channel.send(embed=embed)
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates"""
        if member == self.bot.user:
            return
        
        # Check if bot should join/leave voice channel
        if after.channel and not before.channel:
            # User joined voice channel
            if str(member.id) in self.active_sessions:
                await self.join_voice_channel(after.channel)
        elif before.channel and not after.channel:
            # User left voice channel
            if str(member.id) in self.active_sessions:
                await self.leave_voice_channel(before.channel)
    
    async def join_voice_channel(self, channel):
        """Join voice channel for audio translation"""
        try:
            voice_client = await channel.connect()
            # Start listening to audio
            asyncio.create_task(self.listen_to_voice(voice_client))
        except Exception as e:
            logger.error(f"Error joining voice channel: {e}")
    
    async def leave_voice_channel(self, channel):
        """Leave voice channel"""
        try:
            voice_client = channel.guild.voice_client
            if voice_client:
                await voice_client.disconnect()
        except Exception as e:
            logger.error(f"Error leaving voice channel: {e}")
    
    async def listen_to_voice(self, voice_client):
        """Listen to voice channel for translation"""
        try:
            while voice_client.is_connected():
                # Get audio data
                audio_data = await voice_client.receive()
                
                # Convert to text
                text = await self.audio_service.speech_to_text(audio_data.raw)
                
                if text:
                    # Translate text
                    translated = await self.translation_service.translate(text)
                    
                    # Send translation to text channel
                    channel = voice_client.channel
                    embed = discord.Embed(
                        title="Voice Translation",
                        description=f"**Heard:** {text}\n**Translated:** {translated}",
                        color=0x0099ff
                    )
                    await channel.send(embed=embed)
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error listening to voice: {e}")
    
    @commands.command(name='start_translation')
    async def start_translation(self, ctx, source_lang='en', target_lang='ru'):
        """Start translation session"""
        user_id = str(ctx.author.id)
        
        # Validate languages
        if not await self.translation_service.is_supported_language(source_lang):
            await ctx.send(f"❌ Unsupported source language: {source_lang}")
            return
        
        if not await self.translation_service.is_supported_language(target_lang):
            await ctx.send(f"❌ Unsupported target language: {target_lang}")
            return
        
        # Start session
        self.active_sessions[user_id] = {
            'source_language': source_lang,
            'target_language': target_lang,
            'channel_id': ctx.channel.id
        }
        
        embed = discord.Embed(
            title="Translation Started",
            description=f"Translating from {source_lang} to {target_lang}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='stop_translation')
    async def stop_translation(self, ctx):
        """Stop translation session"""
        user_id = str(ctx.author.id)
        
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            await ctx.send("✅ Translation stopped")
        else:
            await ctx.send("❌ No active translation session")
    
    @commands.command(name='set_language')
    async def set_language(self, ctx, source_lang=None, target_lang=None):
        """Set translation languages"""
        user_id = str(ctx.author.id)
        
        if user_id not in self.active_sessions:
            await ctx.send("❌ No active translation session. Use !start_translation first")
            return
        
        if source_lang:
            if await self.translation_service.is_supported_language(source_lang):
                self.active_sessions[user_id]['source_language'] = source_lang
            else:
                await ctx.send(f"❌ Unsupported source language: {source_lang}")
                return
        
        if target_lang:
            if await self.translation_service.is_supported_language(target_lang):
                self.active_sessions[user_id]['target_language'] = target_lang
            else:
                await ctx.send(f"❌ Unsupported target language: {target_lang}")
                return
        
        session = self.active_sessions[user_id]
        embed = discord.Embed(
            title="Language Updated",
            description=f"Now translating from {session['source_language']} to {session['target_language']}",
            color=0x0099ff
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='translate')
    async def translate_text(self, ctx, *, text):
        """Translate specific text"""
        user_id = str(ctx.author.id)
        
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            translated = await self.translation_service.translate(
                text,
                session['source_language'],
                session['target_language']
            )
        else:
            # Use default languages
            translated = await self.translation_service.translate(text)
        
        embed = discord.Embed(
            title="Translation",
            description=f"**Original:** {text}\n**Translated:** {translated}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='help_translation')
    async def help_translation(self, ctx):
        """Show help for translation commands"""
        embed = discord.Embed(
            title="Translation Bot Commands",
            description="Available commands for real-time translation",
            color=0x0099ff
        )
        
        embed.add_field(
            name="!start_translation [source] [target]",
            value="Start translation session (default: en to ru)",
            inline=False
        )
        embed.add_field(
            name="!stop_translation",
            value="Stop current translation session",
            inline=False
        )
        embed.add_field(
            name="!set_language [source] [target]",
            value="Change translation languages",
            inline=False
        )
        embed.add_field(
            name="!translate [text]",
            value="Translate specific text",
            inline=False
        )
        embed.add_field(
            name="!help_translation",
            value="Show this help message",
            inline=False
        )
        
        await ctx.send(embed=embed)