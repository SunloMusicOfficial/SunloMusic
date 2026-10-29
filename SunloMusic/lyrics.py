import aiohttp
from SunloMusic.logger import LOGGER

async def fetch_lyrics_text(query: str) -> str | None:
    clean_query = query.split("(")[0].split("|")[0].split("[")[0].strip()
    
    # API 1: Lyrist
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://lyrist.vercel.app/api/{clean_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        return f"🎤 <b>{data.get('title', clean_query)} - {data.get('artist', '')}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass

    # API 2: Some-Random-API
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://some-random-api.com/lyrics?title={clean_query}", timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    if "lyrics" in data and data["lyrics"]:
                        return f"🎤 <b>{data.get('title', clean_query)}</b>\n━━━━━━━━━━━━━\n<blockquote>{data['lyrics'][:4000]}</blockquote>"
    except: pass
    
    return None

async def send_karaoke(bot, chat_id: int, title: str):
    lyrics = await fetch_lyrics_text(title)
    if lyrics:
        try: await bot.send_message(chat_id, lyrics)
        except Exception as e: LOGGER.error(f"Karaoke send error: {e}")
