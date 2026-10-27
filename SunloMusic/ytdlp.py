import aiohttp
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
    """Download media from a Telegram CDN link using Pyrogram Assistant."""
    if not bot_module.assistant:
        LOGGER.error("❌ Assistant client not initialized, cannot download Telegram CDN.")
        return None

    link = urlparse(cdnurl)
    parts = link.path.strip("/").split("/")
    if len(parts) != 2 or not parts[1].isdigit():
        LOGGER.error(f"❌ Invalid Telegram CDN link: {cdnurl}")
        return None

    channel, message_id = parts[0], int(parts[1])
    try:
        LOGGER.info(f"📥 Downloading Telegram CDN: {cdnurl}")
        message = await bot_module.assistant.get_messages(channel, message_id)
        if not message or not message.media:
            LOGGER.error(f"❌ Telegram message has no media: {cdnurl}")
            return None

        file_path = await bot_module.assistant.download_media(message, file_name=DOWNLOAD_DIR + "/")
        if not file_path:
            LOGGER.error(f"❌ Failed to download media from Telegram CDN: {cdnurl}")
            return None
        return file_path
    except Exception as e:
        LOGGER.error(f"❌ Telegram CDN download error: {e}")
        return None

async def extract_audio(query: str) -> dict | None:
    if not config.ONEGRAB_API_KEY:
        LOGGER.error("❌ ONEGRAB_API_KEY is missing in .env")
        return None

    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {"title": "Direct Link", "url": query, "duration": 0, "thumbnail": "", "webpage_url": query}

    webpage_url = query
    fallback_meta = {}

    # 1. Search API (Agar text query hai)
    if not query.startswith("http"):
        search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
        if not search_data or not search_data.get("results"):
            LOGGER.error(f"❌ Search failed for: {query}")
            return None
        track = search_data["results"][0]
        webpage_url = track.get("webpage_url") or track.get("url")
        fallback_meta = track
        if not webpage_url:
            return None

    # 2. Official Docs: /api/track returns 'cdnurl'
    track_data = await _api_request("/api/track", {"url": webpage_url})
    
    if track_data:
        result = track_data
        if "results" in track_data and isinstance(track_data["results"], list) and len(track_data["results"]) > 0:
            result = track_data["results"][0]

        # Check for various possible direct link keys
        cdnurl = result.get("cdnurl") or result.get("download_url") or result.get("audio_url")

        if cdnurl:
            # Agar cdnurl Telegram link hai
            if "t.me" in cdnurl or "telegram.me" in cdnurl:
                local_path = await _download_telegram_cdn(cdnurl)
                if local_path:
                    return {
                        "title": result.get("title", fallback_meta.get("title", "Unknown")),
                        "url": local_path, # Local file path
                        "duration": int(result.get("duration") or fallback_meta.get("duration") or 0),
                        "thumbnail": result.get("thumbnail", fallback_meta.get("thumbnail", "")),
                        "webpage_url": webpage_url
                    }
            else:
                # Direct HTTP Link (e.g. .m4a file)
                return {
                    "title": result.get("title", fallback_meta.get("title", "Unknown")),
                    "url": cdnurl,
                    "duration": int(result.get("duration") or fallback_meta.get("duration") or 0),
                    "thumbnail": result.get("thumbnail", fallback_meta.get("thumbnail", "")),
                    "webpage_url": webpage_url
                }
        else:
            LOGGER.warning("⚠️ OneGrab /api/track did not return a cdnurl. Falling back to yt-dlp.")

    # 3. Fallback: Agar API fail ho jaye, toh yt-dlp ko normal YouTube link do
    # (Isliye humne yt-dlp ko requirements se nahi hataya)
    LOGGER.info(f"🔄 Using yt-dlp fallback for: {webpage_url}")
    return {
        "title": fallback_meta.get("title", "Unknown Track"),
        "url": webpage_url, # PyTgCalls will use internal yt-dlp for this
        "duration": int(fallback_meta.get("duration") or 0),
        "thumbnail": fallback_meta.get("thumbnail", ""),
        "webpage_url": webpage_url
    }
