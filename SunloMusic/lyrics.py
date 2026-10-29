import aiohttp
from urllib.parse import quote
from SunloMusic.logger import LOGGER

async def fetch_lyrics_text(query: str) -> str | None:
    # ✅ Clean title perfectly
    clean_query = query.split("(")[0].split("|")[0].split("[")[0].replace("Lyrics", "").replace("Audio", "").replace("Official", "").strip()
    LOGGER.info(f"🔎 Searching lyrics for: {clean_query}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # ✅ 1. Textyl API (Best for Hindi/Bollywood Songs)
    try:
        encoded_query = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://api.textyl.co/api/lyrics?q={encoded_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if isinstance(data, list) and len(data) > 0:
                        full_lyrics = "\n".join([item.get("lyrics", "") for item in data if "lyrics" in item])
                        if full_lyrics:
                            LOGGER.info("✅ Found on Textyl API")
                            return f"🎤 <b>{clean_query}</b>\n━━━━━━━━━━━━━\n<blockquote>{full_lyrics[:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Textyl API failed: {e}")

    # ✅ 2. Lyrics.ovh API (General Fallback)
    try:
        if " - " in clean_query:
            artist, title = clean_query.split(" - ", 1)
        else:
            artist, title = "", clean_query
            
        encoded_artist = quote(artist.strip())
        encoded_title = quote(title.strip())
        
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://api.lyrics.ovh/v1/{encoded_artist}/{encoded_title}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Lyrics.ovh API")
                        return f"🎤 <b>{title.strip()} - {artist.strip()}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Lyrics.ovh API failed: {e}")

    # ✅ 3. Popcat API (Fallback 2)
    try:
        encoded_query = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://api.popcat.xyz/lyrics?song={encoded_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Popcat API")
                        return f"🎤 <b>{data.get('title', clean_query)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Popcat API failed: {e}")
    
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
