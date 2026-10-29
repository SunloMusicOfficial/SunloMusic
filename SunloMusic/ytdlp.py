import aiohttp
import os
from urllib.parse import urlparse
from SunloMusic.config import config
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

API_HEADERS = {"X-API-Key": config.ONEGRAB_API_KEY, "Accept": "application/json"}
DOWNLOAD_DIR = "cache/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def _api_request(endpoint: str, params: dict) -> dict | None:
    url = f"{config.ONEGRAB_API_URL.rstrip('/')}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=API_HEADERS, params=params, timeout=15) as resp:
                if resp.status != 200: return None
                return await resp.json()
    except Exception as e: 
        LOGGER.error(f"API Error: {e}")
        return None

async def _download_telegram_cdn(cdnurl: str) -> str | None:
    if not bot_module.assistant: return None
    link = urlparse(cdnurl)
    parts = link.path.strip("/").split("/")
    if len(parts) != 2 or not parts[1].isdigit(): return None
    channel, message_id = parts[0], int(parts[1])
    try:
        message = await bot_module.assistant.get_messages(channel, message_id)
        if not message or not message.media: return None
        return await bot_module.assistant.download_media(message, file_name=DOWNLOAD_DIR + "/")
    except Exception as e: 
        LOGGER.error(f"Telegram CDN error: {e}")
        return None

async def extract_audio(query: str, video: bool = False) -> dict | None:
    if not config.ONEGRAB_API_KEY: return None
    
    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {"title": "Direct Link", "url": query, "duration": 0, "thumbnail": "", "webpage_url": query}

    webpage_url = query
    fallback_meta = {}

    if not query.startswith("http"):
        # ✅ STEP 1: Fast & Accurate Search via OneGrab
        LOGGER.info(f"🔎 Searching via OneGrab: {query}")
        search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
        
        if search_data and search_data.get("results"):
            track = search_data["results"][0]
            webpage_url = track.get("url")
            # OneGrab search response gives exact duration and thumbnail
            fallback_meta = {
                "title": track.get("title", "Unknown"),
                "duration": int(track.get("duration") or 0),
                "thumbnail": track.get("thumbnail", "")
            }
            LOGGER.info(f"✅ Found: {fallback_meta['title']} ({fallback_meta['duration']}s)")
        else:
            LOGGER.error("❌ OneGrab search failed or returned no results.")
            return None

    if not webpage_url: return None

    # ✅ STEP 2: Fetch Stream Link
    req_type = "video" if video else "audio"
    LOGGER.info(f"🌐 Fetching {req_type} via OneGrab Track API...")
    
    track_data = await _api_request("/api/track", {"url": webpage_url, "type": req_type})
    
    if track_data:
        result = track_data
        if "results" in track_data and isinstance(track_data["results"], list) and len(track_data["results"]) > 0:
            result = track_data["results"][0]

        cdnurl = result.get("cdnurl") or result.get("download_url") or result.get("audio_url") or result.get("video_url")
        
        if cdnurl:
            final_thumb = result.get("thumbnail") or fallback_meta.get("thumbnail", "")
            final_dur = int(result.get("duration") or fallback_meta.get("duration") or 0)
            final_title = result.get("title") or fallback_meta.get("title", "Unknown")
            
            if "t.me" in cdnurl or "telegram.me" in cdnurl:
                local_path = await _download_telegram_cdn(cdnurl)
                if local_path:
                    return {"title": final_title, "url": local_path, "duration": final_dur, "thumbnail": final_thumb, "webpage_url": webpage_url}
            else:
                return {"title": final_title, "url": cdnurl, "duration": final_dur, "thumbnail": final_thumb, "webpage_url": webpage_url}
        else:
            LOGGER.error(f"❌ Track API returned no cdnurl.")
    
    return None
