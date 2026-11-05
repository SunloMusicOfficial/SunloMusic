import os, time
import asyncio
import edge_tts
from groq import Groq
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.config import config
from SunloMusic.ytdlp import extract_audio
from SunloMusic.calls import play_stream, call
from SunloMusic.queues import get_queue, Track
from SunloMusic.logger import LOGGER
from SunloMusic.database import get_group_setting
from pytgcalls.types import MediaStream, AudioQuality

groq_client = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None
TTS_DIR = "cache/tts"
os.makedirs(TTS_DIR, exist_ok=True)

async def speak_in_vc(chat_id: int, text: str):
    if not await get_group_setting(chat_id, "tts", False): return
    q = get_queue(chat_id)
    if not call: return
    try:
        voice = "hi-IN-SwaraNeural" 
        output_file = f"{TTS_DIR}/voice_{chat_id}_{int(time.time())}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            q.is_playing_tts = True
            await call.play(chat_id, MediaStream(media_path=output_file, audio_parameters=AudioQuality.HIGH))
            await asyncio.sleep(len(text) * 0.1 + 1.5) 
            q.is_playing_tts = False
    except Exception as e: LOGGER.error(f"TTS Error: {e}")

@bot.on_message(filters.voice & filters.group)
@catch_errors
async def voice_command_handler(_, m: Message):
    if not await get_group_setting(m.chat.id, "vsearch", False): return
    if not groq_client: return await m.reply_text("❌ GROQ_API_KEY missing!")
        
    status = await m.reply_text("🎤 <b>SunloMusic AI is listening...</b>")
    try:
        file_path = f"cache/downloads/voice_{m.id}.ogg"
        await m.download(file_name=file_path)
        with open(file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(file=(file_path, file.read()), model="whisper-large-v3", response_format="json", prompt="Hindi, Bollywood songs, Arijit Singh, Kesariya")
        text_query = transcription.text.strip()
        if os.path.exists(file_path): os.remove(file_path)
        if not text_query: return await status.edit_text("❌ Could not understand audio.")
            
        import re
        query = re.sub(r'\b(play|bajao|baja|song|music|please|kar|do|karo|sunao)\b', '', text_query, flags=re.IGNORECASE).strip()
        await status.edit_text(f"✨ <b>Heard:</b> <code>{text_query}</code>\n⏳ Searching: <code>{query}</code>...")
        
        info = await extract_audio(query)
        if not info: return await status.edit_text("❌ Song not found.")
            
        q = get_queue(m.chat.id)
        track = Track(info["title"], info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, False, video_id=info.get("video_id", ""))
        
        if q.now_playing:
            q.queue.append(track)
            await status.edit_text(f"📥 Added to Queue: {info['title']}")
            asyncio.create_task(speak_in_vc(m.chat.id, f"{info['title']} queue me add kar diya hai."))
        else:
            await status.edit_text("⚡ Connecting to VC...")
            await speak_in_vc(m.chat.id, f"Ab play ho raha hai, {info['title']}")
            q.now_playing = track; q.start_time = time.time(); q.paused = False; q.votes = set()
            await play_stream(m.chat.id, track.url, track.video, duration=track.duration)
            await status.edit_text(f"🎧 Now Playing: {info['title']}")
    except Exception as e:
        LOGGER.error(f"Voice Error: {e}")
        await status.edit_text("❌ Failed to process voice.")
