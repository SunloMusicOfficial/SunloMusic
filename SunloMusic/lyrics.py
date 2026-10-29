import aiohttp
import re
from urllib.parse import quote
from SunloMusic.logger import LOGGER

async def fetch_lyrics_text(query: str) -> str | None:
    clean_query = query.split("(")[0].split("|")[0].split("[")[0].replace("Lyrics", "").replace("Audio", "").replace("Official", "").strip()
    LOGGER.info(f"🔎 Searching lyrics for: {clean_query}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # ✅ 1. Genius Scraper (Most accurate for all languages)
    try:
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://genius.com/api/search/multi?q={quote(clean_query)}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    hits = data.get("response", {}).get("sections", [{}])[0].get("hits", [])
                    if hits:
                        song_url = hits[0]["result"]["url"]
                        async with s.get(song_url, timeout=10) as sr:
                            if sr.status == 200:
                                html = await sr.text()
                                # Extract lyrics from Genius HTML
                                matches = re.findall(r'<div data-lyrics-container="true".*?>(.*?)</div>', html, re.DOTALL)
                                if matches:
                                    lyrics = "\n".join(matches)
                                    lyrics = re.sub(r'<br/?>', '\n', lyrics)
                                    lyrics = re.sub(r'<.*?>', '', lyrics)
                                    lyrics = lyrics.replace("&#x27;", "'").replace("&amp;", "&").strip()
                                    LOGGER.info("✅ Found on Genius")
                                    return f"🎤 <b>{clean_query}</b>\n━━━━━━━━━━━━━\n<blockquote>{lyrics[:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Genius API failed: {e}")

    # ✅ 2. Paxsenix API (Best for Bollywood/Hindi)
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://api.paxsenix.biz.id/lyrics?q={encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if data.get("status") and data.get("result"):
                        lyrics = data["result"].get("lyrics", "")
                        if lyrics:
                            LOGGER.info("✅ Found on Paxsenix")
                            return f"🎤 <b>{data['result'].get('title', clean_query)} - {data['result'].get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{lyrics[:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Paxsenix API failed: {e}")

    # ✅ 3. Textyl API (Good for Hindi)
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
    except: pass

    # ✅ 4. Lyrist API
    try:
        encoded = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://lyrist.vercel.app/api/{encoded}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Lyrist")
                        return f"🎤 <b>{data.get('title', clean_query)} - {data.get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass
    
    LOGGER.error(f"❌ Lyrics not found for {clean_query} in any API")
    return None

async def send_karaoke(bot, chat_id: int, title: str):
    lyrics = await fetch_lyrics_text(title)
    if lyrics:
        try: await bot.send_message(chat_id, lyrics)
        except Exception as e: LOGGER.error(f"Karaoke send error: {e}")
    else:
        try: await bot.send_message(chat_id, f"🎤 <b>Karaoke Mode:</b> Lyrics not found for <i>{title}</i> in database.")
        except: pass
