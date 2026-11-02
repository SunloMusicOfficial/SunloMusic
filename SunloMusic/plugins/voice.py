import os
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
from SunloMusic.queues import get_queue, Track
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

# ✅ Initialize Groq Client using config
groq_client = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None

TTS_DIR = "cache/tts"
os.makedirs(TTS_DIR, exist_ok=True)

async def speak_in_vc(chat_id: int, text: str):
    if not call: return
    try:
        voice = "en-US-ChristopherNeural" 
        output_file = f"{TTS_DIR}/voice_{chat_id}.mp3"
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        if os.path.exists(output_file):
            from pytgcalls.types import MediaStream
            stream = MediaStream(media_path=output_file, audio_parameters=None)
            await call.play(chat_id, stream)
            await asyncio.sleep(len(text) * 0.08) 
            os.remove(output_file)
    except Exception as e:
        LOGGER.error(f"TTS Error: {e}")

@bot.on_message(filters.voice & filters.group)
@catch_errors
async def voice_command_handler(_, m: Message):
    # ✅ Check if API key is set
    if not groq_client or not config.GROQ_API_KEY:
        return await m.reply_text("❌ <b>GROQ_API_KEY is missing!</b>\nPlease add it in config or Render Environment.")
        
    status = await m.reply_text("🎤 <b>Listening...</b>\n<i>Converting your voice to text...</i>")
    
    try:
        file_path = await m.download()
        
        with open(file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                response_format="json",
            )
            
        text_query = transcription.text.strip()
        os.remove(file_path)
        
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
            await play_stream(m.chat.id, track.url, track.video)
            q.now_playing = track
            q.start_time = asyncio.get_event_loop().time()
            q.paused = False
            q.votes = set()
            
            await status.edit_text(f"🎧 <b>Now Playing:</b> {info['title']}")
            
    except Exception as e:
        LOGGER.error(f"Voice Command Error: {e}")
        await status.edit_text("❌ <b>Failed to process voice command.</b>")
