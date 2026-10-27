import aiohttp
import asyncio
import yt_dlp
import os
from urllib.parse import urlparse
from SunloMusic.config import config
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

API_HEADERS = {
    "X-API-Key": config.ONEGRAB_API_KEY,
    "Accept": "application/json"
}

DOWNLOAD_DIR = "cache/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

YDL_SEARCH_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "extract_flat": True,
    "nocheckcertificate": True,
}

def _search_ytdlp_sync(query: str):
    """Uses yt-dlp to find the most relevant YouTube link (like Aliya Robot)"""
    try:
        with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                return info["entries"][0]
    except Exception as e:
        LOGGER.error(f"yt-dlp search error: {e}")
    return None

async def _api_request(endpoint: str, params: dict) -> dict | None:
    url = f"{config.ONEGRAB_API_URL.rstrip('/')}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=API_HEADERS, params=params, timeout=25) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    LOGGER.error(f"❌ OneGrab API {resp.status}: {text[:300]}")
                    return None
                return await resp.json()
    except Exception as e:
        LOGGER.error(f"❌ OneGrab API Exception: {e}")
        return None

async def _download_telegram_cdn(cdnurl: str) -> str | None:
    if not bot_module.assistant:
        return None
    link = urlparse(cdnurl)
    parts = link.path.strip("/").split("/")
    if len(parts) != 2 or not parts[1].isdigit():
        return None
    channel, message_id = parts[0], int(parts[1])
    try:
        message = await bot_module.assistant.get_messages(channel, message_id)
        if not message or not message.media:
            return None
        file_path = await bot_module.assistant.download_media(message, file_name=DOWNLOAD_DIR + "/")
        return file_path
    except Exception as e:
        LOGGER.error(f"❌ Telegram CDN download error: {e}")
        return None

async def extract_audio(query: str) -> dict | None:
    if not config.ONEGRAB_API_KEY:
        return None

    # Direct URL check
    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {"title": "Direct Link", "url": query, "duration": 0, "thumbnail": "", "webpage_url": query}

    webpage_url = query
    fallback_meta = {}

    # ✅ STEP 1: Search using yt-dlp (Fixes the wrong song issue)
    if not query.startswith("http"):
        LOGGER.info(f"🔎 Searching via yt-dlp for: {query}")
        loop = asyncio.get_running_loop()
        ytdlp_info = await loop.run_in_executor(None, _search_ytdlp_sync, query)
        
        if ytdlp_info and ytdlp_info.get("url"):
            webpage_url = ytdlp_info.get("url")
            fallback_meta = {
                "title": ytdlp_info.get("title", "Unknown"),
                "duration": ytdlp_info.get("duration", 0),
                "thumbnail": ytdlp_info.get("thumbnails", [{}])[-1].get("url", "") if ytdlp_info.get("thumbnails") else ""
            }
            LOGGER.info(f"✅ Found correct URL: {webpage_url}")
        else:
            # Fallback to OneGrab search if yt-dlp fails
            LOGGER.warning("⚠️ yt-dlp search failed, falling back to OneGrab search")
            search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
            if search_data and search_data.get("results"):
                track = search_data["results"][0]
                webpage_url = track.get("webpage_url") or track.get("url")
                fallback_meta = track

    if not webpage_url:
        return None

    # ✅ STEP 2: Get stream link from OneGrab API
    track_data = await _api_request("/api/track", {"url": webpage_url})
    
    if track_data:
        result = track_data
        if "results" in track_data and isinstance(track_data["results"], list) and len(track_data["results"]) > 0:
            result = track_data["results"][0]

        cdnurl = result.get("cdnurl") or result.get("download_url") or result.get("audio_url")

        if cdnurl:
            if "t.me" in cdnurl or "telegram.me" in cdnurl:
                local_path = await _download_telegram_cdn(cdnurl)
                if local_path:
                    return {
                        "title": result.get("title", fallback_meta.get("title", "Unknown")),
                        "url": local_path,
                        "duration": int(result.get("duration") or fallback_meta.get("duration") or 0),
                        "thumbnail": result.get("thumbnail", fallback_meta.get("thumbnail", "")),
                        "webpage_url": webpage_url
                    }
            else:
                return {
                    "title": result.get("title", fallback_meta.get("title", "Unknown")),
                    "url": cdnurl,
                    "duration": int(result.get("duration") or fallback_meta.get("duration") or 0),
                    "thumbnail": result.get("thumbnail", fallback_meta.get("thumbnail", "")),
                    "webpage_url": webpage_url
                }

    # STEP 3: Final fallback (yt-dlp direct stream if API fails)
    LOGGER.warning("⚠️ OneGrab failed, using yt-dlp direct fallback")
    return {
        "title": fallback_meta.get("title", "Unknown Track"),
        "url": webpage_url,
        "duration": int(fallback_meta.get("duration") or 0),
        "thumbnail": fallback_meta.get("thumbnail", ""),
        "webpage_url": webpage_url
    }
