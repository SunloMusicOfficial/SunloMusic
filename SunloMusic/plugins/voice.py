import os, time
import asyncio
import edge_tts
from groq import Groq
from pyrogram import filters, enums
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.config import config
from SunloMusic.ytdlp import extract_audio
from SunloMusic.calls import play_stream, call
from SunloMusic.queues import get_queue, Track, TTS_CHATS, VOICE_CMD_CHATS
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

from pytgcalls.types import MediaStream, AudioQuality

groq_client = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None

TTS_DIR = "cache/tts"
os.makedirs(TTS_DIR, exist_ok=True)

async def speak_in_vc(chat_id: int, text: str):
    # ✅ Check if TTS is enabled for this chat
    if chat_id not in TTS_CHATS: return
    
    q = get_queue(chat_id)
    if not call: return
    try:
        voice = "en-US-JennyNeural" 
        output_file = f"{TTS_DIR}/voice_{chat_id}_{int(time.time())}.mp3"
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            q.is_playing_tts = True
            stream = MediaStream(media_path=output_file, audio_parameters=AudioQuality.HIGH)
            await call.play(chat_id, stream)
            
            await asyncio.sleep(len(text) * 0.08 + 1.5) 
            q.is_playing_tts = False
    except Exception as e:
        LOGGER.error(f"TTS Error: {e}")

@bot.on_message(filters.voice & filters.group)
@catch_errors
async def voice_command_handler(_, m: Message):
    # ✅ Check if Voice Search is enabled for this chat
    if m.chat.id not in VOICE_CMD_CHATS: return
    
    if not groq_client or not config.GROQ_API_KEY:
        return await m.reply_text("❌ <b>GROQ_API_KEY is missing!</b>\nPlease add it in Render Environment.")
        
    status = await m.reply_text("🎤 <b>Listening...</b>\n<i>Converting your voice to text...</i>")
    
    try:
        file_path = f"cache/downloads/voice_{m.id}.ogg"
        await m.download(file_name=file_path)
        
        with open(file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                response_format="json",
            )
            
        text_query = transcription.text.strip()
        if os.path.exists(file_path): os.remove(file_path)
        
        if not text_query:
            return await status.edit_text("❌ <b>Could not understand the audio.</b>")
            
        query = text_query.lower().replace("play", "").replace("bajao", "").replace("song", "").strip()
        
        if not query:
            return await status.edit_text("❌ <b>Please say a song name clearly.</b>")
            
        await status.edit_text(f"✨ <b>Heard:</b> <code>{text_query}</code>\n\n⏳ <b>Searching & Downloading...</b>")
        
        info = await extract_audio(query)
        if not info:
            return await status.edit_text("❌ <b>Song not found.</b>")
            
        q = get_queue(m.chat.id)
        track = Track(info["title"], info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, False)
        
        if q.now_playing:
            q.queue.append(track)
            await status.edit_text(f"📥 <b>Added to Queue:</b> {info['title']}")
            asyncio.create_task(speak_in_vc(m.chat.id, f"Added {info['title']} to the queue."))
        else:
            await status.edit_text("⚡ <b>Connecting to VC...</b>")
            await speak_in_vc(m.chat.id, f"Now playing, {info['title']}")
            q.now_playing = track
            q.start_time = time.time()
            q.paused = False
            q.votes = set()
            await play_stream(m.chat.id, track.url, track.video)
            await status.edit_text(f"🎧 <b>Now Playing:</b> {info['title']}")
            
    except Exception as e:
        LOGGER.error(f"Voice Command Error: {e}")
        await status.edit_text("❌ <b>Failed to process voice command.</b>")
