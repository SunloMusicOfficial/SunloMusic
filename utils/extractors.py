import asyncio
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
                    search_query = f"ytsearch:{query}"
                    info = ydl.extract_info(search_query, download=False)
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
            "thumbnail": data.get("thumbnail")
        }
    return None
