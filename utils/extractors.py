import asyncio
import random
import yt_dlp
from utils.logger import LOGGER

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
}

async def fetch_audio_url(query: str):
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
    data = await loop.run_in_executor(None, extract)
    
    if data:
        return {
            "title": data.get("title", "Unknown Title"),
            "duration": data.get("duration", 0),
            "stream_url": data.get("url"),
            "thumbnail": data.get("thumbnail"),
            "original_url": data.get("webpage_url", query)
        }
    return None

async def fetch_related_track(last_title: str):
    # Auto-play ke liye similar gaane search karega
    def extract_related():
        try:
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                # Top 5 similar results fetch karenge
                info = ydl.extract_info(f"ytsearch5:{last_title} song", download=False)
                if "entries" in info and len(info["entries"]) > 1:
                    # Pehla result original gaana hi hota hai, isliye baaki me se ek choose karenge
                    choices = info["entries"][1:]
                    return random.choice(choices)
        except Exception as e:
            LOGGER.error(f"AutoPlay Fetch Error: {e}")
            return None
            
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, extract_related)
    
    if data:
        return {
            "title": data.get("title", "Unknown Title"),
            "duration": data.get("duration", 0),
            "stream_url": data.get("url"),
            "thumbnail": data.get("thumbnail"),
            "original_url": data.get("webpage_url")
        }
    return None
