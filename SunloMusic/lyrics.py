import aiohttp
import re
import yt_dlp
from urllib.parse import quote
from SunloMusic.logger import LOGGER

def _get_real_title(query):
    """Uses yt-dlp to find the exact song title if the query is short"""
    try:
        ydl_opts = {"quiet": True, "noplaylist": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} song lyrics", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                return info["entries"][0].get("title", query)
    except Exception as e:
        LOGGER.error(f"yt-dlp lyrics search error: {e}")
    return query

async def fetch_lyrics_text(query: str) -> str | None:
    # ✅ 1. Agar query choti hai, toh pehle asli gaane ka naam dhoondho
    real_title = query
    if len(query.split()) <= 3:
        real_title = _get_real_title(query)
    
    # Clean title
    clean_query = real_title.split("(")[0].split("|")[0].split("[")[0].replace("Lyrics", "").replace("Audio", "").replace("Official", "").strip()
    
    # ✅ 2. Smart Logic: Split Artist and Title
    artist, title = "", clean_query
    if " - " in clean_query:
        parts = clean_query.split(" - ")
        artist = parts[0].strip()
        title = parts[1].strip()
    elif " by " in clean_query.lower():
        parts = re.split(r' by ', clean_query, flags=re.IGNORECASE)
        title = parts[0].strip()
        artist = parts[1].strip()
        
    clean_artist = re.split(r'&|,|ft\.|feat\.|X|x', artist)[0].strip()
    LOGGER.info(f"🔎 Searching lyrics for Title: '{title}', Artist: '{clean_artist}'")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # ✅ 3. Lyrics.ovh API (Best for Bollywood & Pop)
    if clean_artist and title:
        try:
            url = f"https://api.lyrics.ovh/v1/{quote(clean_artist)}/{quote(title)}"
            async with aiohttp.ClientSession(headers=headers) as s:
                async with s.get(url, timeout=10) as r:
                    if r.status == 200:
                        data = await r.json()
                        if "lyrics" in data and data["lyrics"]:
                            LOGGER.info("✅ Found on Lyrics.ovh")
                            return f"🎤 <b>{title} - {clean_artist}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
        except: pass

    # ✅ 4. Lyrist API (Fuzzy match)
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://lyrist.vercel.app/api/{encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Lyrist")
                        return f"🎤 <b>{data.get('title', title)} - {data.get('artist', artist)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass

    # ✅ 5. Popcat API (Fallback)
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://api.popcat.xyz/lyrics?song={encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Popcat")
                        return f"🎤 <b>{data.get('title', title)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass

    LOGGER.error(f"❌ Lyrics not found for {clean_query}")
    return None

async def send_karaoke(bot, chat_id: int, title: str):
    lyrics = await fetch_lyrics_text(title)
    if lyrics:
        try: await bot.send_message(chat_id, lyrics)
        except Exception as e: LOGGER.error(f"Karaoke send error: {e}")
    else:
        try: await bot.send_message(chat_id, f"🎤 <b>Karaoke Mode:</b> Lyrics not found for <i>{title}</i> in database.")
        except: pass
