import asyncio, yt_dlp
from SunloMusic.logger import LOGGER

YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "geo_bypass": True,
    "extract_flat": False,
}

def _extract_sync(query: str):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            search_query = query if query.startswith("http") else f"ytsearch1:{query}"
            info = ydl.extract_info(search_query, download=False)
            if not info: return None
            if "entries" in info: 
                if not info["entries"]: return None
                info = info["entries"][0]
            return {
                "title": info.get("title", "Unknown"),
                "url": info.get("url"),
                "duration": int(info.get("duration") or 0),
                "thumbnail": info.get("thumbnail", ""),
                "webpage_url": info.get("webpage_url", "")
            }
    except Exception as e:
        LOGGER.error(f"yt-dlp error: {e}")
        return None

async def extract_audio(query: str):
    return await asyncio.get_event_loop().run_in_executor(None, _extract_sync, query)
