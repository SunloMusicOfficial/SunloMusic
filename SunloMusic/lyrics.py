import aiohttp
import re
from urllib.parse import quote
from SunloMusic.logger import LOGGER

async def fetch_lyrics_text(query: str) -> str | None:
    # Clean title perfectly
    clean_query = query.split("(")[0].split("|")[0].split("[")[0].replace("Lyrics", "").replace("Audio", "").replace("Official", "").replace("Full Song", "").strip()
    
    # ✅ Smart Logic: Split Artist and Title
    artist, title = "", clean_query
    if " - " in clean_query:
        parts = clean_query.split(" - ")
        artist = parts[0].strip()
        title = parts[1].strip()
    elif " by " in clean_query.lower():
        parts = re.split(r' by ', clean_query, flags=re.IGNORECASE)
        title = parts[0].strip()
        artist = parts[1].strip()
        
    # Clean artist name (remove &, ft., etc.)
    clean_artist = re.split(r'&|,|ft\.|feat\.', artist)[0].strip()
    LOGGER.info(f"🔎 Searching lyrics for Title: '{title}', Artist: '{clean_artist}'")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # ✅ 1. Lyrics.ovh API (Best for Bollywood & Pop)
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
        except Exception as e:
            LOGGER.error(f"Lyrics.ovh failed: {e}")

    # ✅ 2. Lyrist API (Fallback)
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://lyrist.vercel.app/api/{encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Lyrist")
                        return f"🎤 <b>{data.get('title', clean_query)} - {data.get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Lyrist failed: {e}")

    # ✅ 3. Some-Random-API (Fallback)
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://some-random-api.com/lyrics?title={encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Some-Random")
                        return f"🎤 <b>{data.get('title', clean_query)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Some-Random failed: {e}")

    # ✅ 4. Textyl API (Fallback)
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://api.textyl.co/api/lyrics?q={encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if isinstance(data, list) and len(data) > 0:
                        full_lyrics = "\n".join([item.get("lyrics", "") for item in data if "lyrics" in item])
                        if full_lyrics:
                            LOGGER.info("✅ Found on Textyl")
                            return f"🎤 <b>{clean_query}</b>\n━━━━━━━━━━━━━\n<blockquote>{full_lyrics[:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Textyl failed: {e}")
    
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
