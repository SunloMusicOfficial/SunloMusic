import aiohttp
import asyncio
import yt_dlp
import urllib.parse
from utils.cache import get_cache, set_cache
from config.vars import Config
from utils.logger import LOGGER
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

async def fetch_audio_url(query: str):
    cached_data = get_cache(query)
    if cached_data: return cached_data

    safe_query = urllib.parse.quote(query)
    
    # Universal API Logic (Works with any custom API provider)
    if Config.STREAM_API_URL:
        base_url = Config.STREAM_API_URL.rstrip('/')
        api_url = f"{base_url}/extract?query={safe_query}"
        
        headers = {}
        if Config.STREAM_API_KEY:
            # API key ko URL aur Headers dono me inject kar diya (Universal Support)
            api_url += f"&key={Config.STREAM_API_KEY}&apikey={Config.STREAM_API_KEY}"
            headers["Authorization"] = f"Bearer {Config.STREAM_API_KEY}"
            headers["x-api-key"] = Config.STREAM_API_KEY
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        stream_url = data.get("stream_url") or data.get("url") or (data.get("data", {}).get("url"))
                        
                        if stream_url:
                            result = {
                                "title": data.get("title") or data.get("data", {}).get("title") or "Unknown Title",
                                "duration": int(data.get("duration") or data.get("data", {}).get("duration") or 0),
                                "stream_url": stream_url,
                                "thumbnail": data.get("thumbnail") or data.get("thumb") or data.get("data", {}).get("thumbnail"),
                                "original_url": data.get("original_url") or query
                            }
                            set_cache(query, result)
                            return result
        except Exception as e:
            LOGGER.error(f"External API Error: {e}")

    # Fallback to local yt-dlp
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
    pass
