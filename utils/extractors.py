import asyncio
import yt_dlp
from utils.logger import LOGGER
from utils.cache import get_cache, set_cache
from concurrent.futures import ThreadPoolExecutor

# Dedicated CPU thread pool for heavy extraction
executor = ThreadPoolExecutor(max_workers=5)

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
}

async def fetch_audio_url(query: str):
    # Check Cache First (Boosts speed by 10x)
    cached_data = get_cache(query)
    if cached_data:
        return cached_data

    def extract():
        try:
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                if not query.startswith("http"):
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                    if "entries" in info and len(info["entries"]) > 0:
                        return info["entries"][0]
                else:
                    return ydl.extract_info(query, download=False)
        except Exception as e:
            LOGGER.error(f"yt-dlp Error: {e}")
            return None
            
    loop = asyncio.get_event_loop()
    # Offload to background thread so Bot doesn't freeze
    data = await loop.run_in_executor(executor, extract)
    
    if data:
        result = {
            "title": data.get("title", "Unknown Title"),
            "duration": data.get("duration", 0),
            "stream_url": data.get("url"),
            "thumbnail": data.get("thumbnail"),
            "original_url": data.get("webpage_url", query)
        }
        set_cache(query, result) # Save to cache for next time
        return result
    return None

async def fetch_playlist(url: str):
    def extract():
        try:
            with yt_dlp.YoutubeDL({"extract_flat": True, "quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                if "entries" in info:
                    return [{"title": entry.get("title"), "original_url": entry.get("url")} for entry in info["entries"][:50]]
        except Exception as e:
            LOGGER.error(f"Playlist Fetch Error: {e}")
        return None
        
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, extract)
