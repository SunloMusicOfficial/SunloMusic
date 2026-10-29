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
    if len(query.split()) <= 3: real_title = _get_real_title(query)
    
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
        except Exception as e: LOGGER.error(f"Lyrics.ovh error: {e}")

    # Lyrist
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://lyrist.vercel.app/api/{encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]: return data["lyrics"]
    except Exception as e: LOGGER.error(f"Lyrist error: {e}")

    return None

async def start_live_karaoke(bot, chat_id, title, duration, q):
    try:
        if q.karaoke_task:
            q.karaoke_task.cancel()
            q.karaoke_task = None

        lyrics = await fetch_lyrics_text(title)

        # ✅ Agar lyrics nahi mile toh chat me batao
        if not lyrics:
            await bot.send_message(chat_id, f"🎤 <b>Karaoke:</b> Lyrics not found for <i>{title}</i> in database.")
            return

        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        if not lines: return

        total_lines = len(lines)
        delay = (duration / total_lines) if duration > 0 else 5.0
        delay = max(4.0, min(delay, 8.0)) # 4 se 8 second ka gap

        # ✅ Pehli line turant bhejo
        msg = await bot.send_message(chat_id, f"🎤 <b>Live Karaoke</b>\n\n<blockquote>{lines[0]}</blockquote>")
        q.karaoke_msg_id = msg.id

        for i in range(1, len(lines)):
            if not q.now_playing or q.now_playing.title != title or q.paused:
                break

            await asyncio.sleep(delay)

            text = f"🎤 <b>Live Karaoke</b>\n\n<blockquote>{lines[i]}</blockquote>"
            try: await bot.edit_message_text(chat_id, msg.id, text)
            except: pass

    except asyncio.CancelledError:
        pass
    except Exception as e:
        LOGGER.error(f"Karaoke error: {e}")
        try: await bot.send_message(chat_id, f"❌ <b>Karaoke Error:</b> <code>{e}</code>")
        except: pass
