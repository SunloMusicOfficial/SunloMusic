import aiohttp, asyncio, yt_dlp, os
from urllib.parse import urlparse
from SunloMusic.config import config
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

API_HEADERS = {"X-API-Key": config.ONEGRAB_API_KEY, "Accept": "application/json"}
DOWNLOAD_DIR = "cache/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ✅ Helper to fetch exact metadata (duration & thumbnail) from a URL
def _fetch_metadata_sync(url: str):
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info: return None
            
            thumb_url = ""
            if info.get("thumbnails"):
                thumb_url = info["thumbnails"][-1]["url"]
            elif info.get("id"):
                thumb_url = f"https://i.ytimg.com/vi/{info['id']}/hqdefault.jpg"
                
            return {
                "title": info.get("title", "Unknown"),
                "duration": int(info.get("duration") or 0),
                "thumbnail": thumb_url
            }
    except Exception as e:
        LOGGER.error(f"Metadata fetch error: {e}")
        return None

async def _api_request(endpoint: str, params: dict) -> dict | None:
    url = f"{config.ONEGRAB_API_URL.rstrip('/')}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=API_HEADERS, params=params, timeout=15) as resp:
                if resp.status != 200: return None
                return await resp.json()
    except: return None

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
    except: return None

async def extract_audio(query: str, video: bool = False) -> dict | None:
    if not config.ONEGRAB_API_KEY: return None
    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {"title": "Direct Link", "url": query, "duration": 0, "thumbnail": "", "webpage_url": query}

    webpage_url = query
    fallback_meta = {}

    if not query.startswith("http"):
        # ✅ Step 1: Use OneGrab Search FIRST (Accurate Song Name)
        LOGGER.info(f"🔎 Searching via OneGrab: {query}")
        search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
        
        if search_data and search_data.get("results"):
            track = search_data["results"][0]
            webpage_url = track.get("webpage_url") or track.get("url")
            fallback_meta = {
                "title": track.get("title", "Unknown"),
                "duration": int(track.get("duration") or 0),
                "thumbnail": track.get("thumbnail", "")
            }
        else:
            # Fallback to yt-dlp search if OneGrab fails
            LOGGER.warning("⚠️ OneGrab search failed, trying yt-dlp search...")
            loop = asyncio.get_running_loop()
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True, "extract_flat": True}) as ydl:
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch1:{query}", download=False))
                    if info and "entries" in info and len(info["entries"]) > 0:
                        webpage_url = info["entries"][0].get("url")
                        fallback_meta = {"title": info["entries"][0].get("title", "Unknown")}
            except Exception as e:
                LOGGER.error(f"yt-dlp search error: {e}")

        # ✅ Step 2: Fetch exact metadata (Duration & Thumbnail) using yt-dlp
        if webpage_url:
            loop = asyncio.get_running_loop()
            meta = await loop.run_in_executor(None, _fetch_metadata_sync, webpage_url)
            if meta:
                fallback_meta.update(meta)
                LOGGER.info(f"✅ Metadata fetched: {meta['duration']}s | {meta['thumbnail'][:50]}")

    if not webpage_url: 
        LOGGER.error("❌ No webpage URL found.")
        return None

    # ✅ Step 3: Fetch Stream Link via OneGrab
    req_type = "video" if video else "audio"
    LOGGER.info(f"🌐 Fetching {req_type} via OneGrab API: {webpage_url}")
    
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
            LOGGER.error(f"❌ API returned no cdnurl: {track_data}")
    
    return None
