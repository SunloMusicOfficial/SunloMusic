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

    # ✅ 1. Lyrist API (Best for exact matches)
    try:
        encoded_query = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://lyrist.vercel.app/api/{encoded_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Lyrist API")
                        return f"🎤 <b>{data.get('title', clean_query)} - {data.get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Lyrist API failed: {e}")

    # ✅ 2. Popcat API (Fallback 1)
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

    # ✅ 3. Some-Random-API (Fallback 2)
    try:
        encoded_query = quote(clean_query)
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(f"https://some-random-api.com/lyrics?title={encoded_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Found on Some-Random API")
                        return f"🎤 <b>{data.get('title', clean_query)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Some-Random API failed: {e}")
    
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
