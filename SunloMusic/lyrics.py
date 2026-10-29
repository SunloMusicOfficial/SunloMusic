import aiohttp
from SunloMusic.logger import LOGGER

async def fetch_lyrics_text(query: str) -> str | None:
    # Clean title (remove "(Lyrics)", "| Ek Tha Raja" etc.)
    clean_query = query.split("(")[0].split("|")[0].split("[")[0].replace("Lyrics", "").strip()
    LOGGER.info(f"🔎 Searching lyrics for: {clean_query}")
    
    # ✅ API 1: Popcat (Best for Hindi & Latest Songs)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://api.popcat.xyz/lyrics?song={clean_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Lyrics found on Popcat API")
                        return f"🎤 <b>{data.get('title', clean_query)} - {data.get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except Exception as e:
        LOGGER.error(f"Popcat API error: {e}")

    # ✅ API 2: Lyrist (Fallback)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://lyrist.vercel.app/api/{clean_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Lyrics found on Lyrist API")
                        return f"🎤 <b>{data.get('title', clean_query)} - {data.get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass

    # ✅ API 3: Some-Random-API (Fallback)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://some-random-api.com/lyrics?title={clean_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        LOGGER.info("✅ Lyrics found on Some-Random API")
                        return f"🎤 <b>{data.get('title', clean_query)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
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
