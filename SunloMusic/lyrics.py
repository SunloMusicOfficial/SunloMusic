import aiohttp
import re
import asyncio
from urllib.parse import quote
from SunloMusic.logger import LOGGER

# ✅ Helper for safe API calls with IPv4 & Timeout
async def _api_get(url, headers, timeout=5):
    try:
        # Force IPv4 to prevent Render hanging
        conn = aiohttp.TCPConnector(family=2) 
        async with aiohttp.ClientSession(headers=headers, connector=conn) as s:
            async with s.get(url, timeout=timeout) as r:
                if r.status == 200:
                    return await r.json()
    except Exception as e:
        LOGGER.error(f"API Error: {e}")
    return None

async def fetch_lyrics_text(query: str) -> str | None:
    try:
        clean_query = query.split("(")[0].split("|")[0].split("[")[0].replace("Lyrics", "").replace("Audio", "").replace("Official", "").strip()
        
        artist, title = "", clean_query
        if " - " in clean_query:
            parts = clean_query.split(" - ")
            artist = parts[0].strip()
            title = parts[1].strip()
            
        clean_artist = re.split(r'&|,|ft\.|feat\.|X|x', artist)[0].strip()
        headers = {"User-Agent": "Mozilla/5.0"}

        # 1. Lyrics.ovh (Exact match)
        if clean_artist and title:
            data = await _api_get(f"https://api.lyrics.ovh/v1/{quote(clean_artist)}/{quote(title)}", headers)
            if data and "lyrics" in data and data["lyrics"]:
                return data["lyrics"]

        # 2. Lyrist (Fuzzy match)
        encoded = quote(clean_query)
        data = await _api_get(f"https://lyrist.vercel.app/api/{encoded}", headers)
        if data and "lyrics" in data and data["lyrics"]:
            return data["lyrics"]

        return None
    except Exception as e:
        LOGGER.error(f"Fetch lyrics error: {e}")
        return None

async def start_live_karaoke(bot, chat_id, title, duration, q):
    if q.karaoke_task:
        q.karaoke_task.cancel()
        
    # ✅ Turant message bhejo taaki user ko pata chale bot kaam kar raha hai
    msg = await bot.send_message(chat_id, f"🎤 <b>Fetching live lyrics for:</b> <i>{title}</i>...")
    
    try:
        # 15 sec global timeout
        lyrics = await asyncio.wait_for(fetch_lyrics_text(title), timeout=15.0)
        
        if not lyrics:
            await msg.edit_text(f"🎤 <b>Karaoke:</b> Lyrics not found for <i>{title}</i> in database.")
            return

        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        if not lines:
            await msg.edit_text(f"🎤 <b>Karaoke:</b> Lyrics content is empty.")
            return

        total_lines = len(lines)
        delay = (duration / total_lines) if duration > 0 else 4.0
        delay = max(3.0, min(delay, 6.0))

        # ✅ Pehli line turant bhejo
        await msg.edit_text(f"🎤 <b>Live Karaoke</b>\n\n<blockquote>{lines[0]}</blockquote>")
        q.karaoke_msg_id = msg.id

        for i in range(1, len(lines)):
            if not q.now_playing or q.now_playing.title != title or q.paused:
                break
            await asyncio.sleep(delay)
            text = f"🎤 <b>Live Karaoke</b>\n\n<blockquote>{lines[i]}</blockquote>"
            try: await msg.edit_text(text)
            except: pass

    except asyncio.TimeoutError:
        LOGGER.error("Karaoke fetch timed out")
        await msg.edit_text("❌ <b>Karaoke Error:</b> Timed out while fetching lyrics from API.")
    except asyncio.CancelledError:
        try: await msg.delete()
        except: pass
    except Exception as e:
        LOGGER.error(f"Karaoke error: {e}")
        await msg.edit_text(f"❌ <b>Karaoke Error:</b> <code>{e}</code>")
