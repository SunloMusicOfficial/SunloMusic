import aiohttp
import asyncio
import yt_dlp
from utils.cache import get_cache, set_cache
from config.vars import Config
from utils.logger import LOGGER
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

async def fetch_audio_url(query: str):
    cached_data = get_cache(query)
    if cached_data: return cached_data

    # Use External API if provided in .env (Bypasses YouTube IP Block)
    if Config.STREAM_API_URL:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{Config.STREAM_API_URL}/extract?query={query}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = {
                            "title": data.get("title", "Unknown"),
                            "duration": data.get("duration", 0),
                            "stream_url": data.get("stream_url"),
                            "thumbnail": data.get("thumbnail"),
                            "original_url": data.get("url", query)
                        }
                        set_cache(query, result)
                        return result
        except Exception as e:
            LOGGER.error(f"API Extraction Error: {e}")

    # Fallback to local yt-dlp if API fails or is missing
    def extract():
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}" if not query.startswith("http") else query, download=False)
                return info["entries"][0] if "entries" in info else info
        except Exception:
            return None
            
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(executor, extract)
    
    if data:
        result = {
            "title": data.get("title"),
            "duration": data.get("duration"),
            "stream_url": data.get("url"),
            "thumbnail": data.get("thumbnail"),
            "original_url": data.get("webpage_url", query)
        }
        set_cache(query, result)
        return result
    return None

async def fetch_playlist(url: str):
    # Same logic can be applied here for playlist API
    pass
