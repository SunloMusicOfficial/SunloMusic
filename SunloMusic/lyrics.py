import aiohttp
import re
import yt_dlp
import asyncio
from urllib.parse import quote
from SunloMusic.logger import LOGGER

def _get_real_title(query):
    try:
        ydl_opts = {"quiet": True, "noplaylist": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} song lyrics", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                return info["entries"][0].get("title", query)
    except: pass
    return query

async def fetch_lyrics_text(query: str) -> str | None:
    real_title = query
    if len(query.split()) <= 3:
        real_title = _get_real_title(query)
    
    clean_query = real_title.split("(")[0].split("|")[0].split("[")[0].replace("Lyrics", "").replace("Audio", "").replace("Official", "").strip()
    
    artist, title = "", clean_query
    if " - " in clean_query:
        parts = clean_query.split(" - ")
        artist = parts[0].strip()
        title = parts[1].strip()
        
    clean_artist = re.split(r'&|,|ft\.|feat\.|X|x', artist)[0].strip()
    headers = {"User-Agent": "Mozilla/5.0"}

    # Lyrics.ovh
    if clean_artist and title:
        try:
            url = f"https://api.lyrics.ovh/v1/{quote(clean_artist)}/{quote(title)}"
            async with aiohttp.ClientSession(headers=headers) as s:
                async with s.get(url, timeout=10) as r:
                    if r.status == 200:
                        data = await r.json()
                        if "lyrics" in data and data["lyrics"]: return data["lyrics"]
        except: pass

    # Lyrist
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://lyrist.vercel.app/api/{encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]: return data["lyrics"]
    except: pass

    return None

# ✅ LIVE KARAOKE ENGINE
async def start_live_karaoke(bot, chat_id, title, duration, q):
    if q.karaoke_task: q.karaoke_task.cancel()
    
    lyrics = await fetch_lyrics_text(title)
    if not lyrics:
        return
    
    # Split into lines and remove empty ones
    lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
    if not lines: return
    
    # Calculate delay (duration / total_lines)
    # We add a small buffer so it doesn't finish too early
    total_lines = len(lines)
    delay = (duration / total_lines) if duration > 0 else 4.0
    delay = max(3.0, min(delay, 6.0)) # Keep between 3 to 6 seconds to avoid Telegram flood limits
    
    msg = await bot.send_message(chat_id, f"🎤 <b>Live Karaoke: {title}</b>\n\n<blockquote>🎵 ...</blockquote>")
    q.karaoke_msg_id = msg.id
    
    try:
        for line in lines:
            if not q.now_playing or q.now_playing.title != title or q.paused:
                break
            
            text = f"🎤 <b>Live Karaoke</b>\n\n<blockquote>{line}</blockquote>"
            try:
                await bot.edit_message_text(chat_id, msg.id, text)
            except: pass
            
            await asyncio.sleep(delay)
    except asyncio.CancelledError:
        pass
    finally:
        try: await bot.delete_message(chat_id, msg.id)
        except: pass
