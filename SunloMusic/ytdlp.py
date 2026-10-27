import aiohttp
import asyncio
import yt_dlp
import os
import re
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

# ✅ Step 1: Search using yt-dlp with multiple results
YDL_SEARCH_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "extract_flat": True,
    "nocheckcertificate": True,
}

# ✅ Step 2: Filter and rank results
def _filter_and_rank_results(entries: list, query: str):
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    
    # Keywords that indicate a music video
    music_keywords = {"song", "audio", "lyrics", "official", "music", "video"}
    
    scored_entries = []
    for entry in entries:
        if not entry:
            continue
            
        title = entry.get("title", "").lower()
        duration = entry.get("duration", 0)
        view_count = entry.get("view_count", 0) or 0
        
        score = 0
        
        # 1. Title word match (most important)
        title_words = set(re.findall(r'\w+', title))
        match_count = len(query_words.intersection(title_words))
        if match_count > 0:
            score += match_count * 10
            
        # 2. Music keywords boost
        if any(kw in title for kw in music_keywords):
            score += 5
            
        # 3. Duration filter (songs are usually 1-10 mins, avoid 2-hour podcasts)
        if 60 <= duration <= 600:  # 1 min to 10 mins
            score += 10
        elif duration > 1200:  # Longer than 20 mins (likely podcast/lecture)
            score -= 20
            
        # 4. View count (popularity)
        if view_count > 10_000_000:
            score += 10
        elif view_count > 1_000_000:
            score += 5
            
        scored_entries.append((score, entry))
        
    # Sort by score descending
    scored_entries.sort(key=lambda x: x[0], reverse=True)
    return [entry for score, entry in scored_entries]

def _search_ytdlp_sync(query: str):
    """Uses yt-dlp to find the most relevant YouTube link"""
    try:
        # Enhance query for music
        search_query = query
        if not any(kw in query.lower() for kw in ["official", "lyrics", "audio", "video"]):
            search_query = f"{query} official audio"
            
        LOGGER.info(f"🔎 Searching yt-dlp: {search_query}")
        
        # Get top 5 results
        with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch5:{search_query}", download=False)
            if not info or "entries" not in info or len(info["entries"]) == 0:
                # Fallback to plain search
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                
            if info and "entries" in info and len(info["entries"]) > 0:
                # Filter and rank
                ranked = _filter_and_rank_results(info["entries"], query)
                if ranked:
                    best = ranked[0]
                    LOGGER.info(f"✅ Best match: {best.get('title')} (score: {ranked[0]})")
                    return best
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

    # ✅ STEP 1: Smart Search using yt-dlp (Fixes wrong song issue)
    if not query.startswith("http"):
        loop = asyncio.get_running_loop()
        ytdlp_info = await loop.run_in_executor(None, _search_ytdlp_sync, query)
        
        if ytdlp_info and ytdlp_info.get("url"):
            webpage_url = ytdlp_info.get("url")
            fallback_meta = {
                "title": ytdlp_info.get("title", "Unknown"),
                "duration": ytdlp_info.get("duration", 0),
                "thumbnail": ytdlp_info.get("thumbnails", [{}])[-1].get("url", "") if ytdlp_info.get("thumbnails") else ""
            }
            LOGGER.info(f"✅ Selected URL: {webpage_url}")
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
