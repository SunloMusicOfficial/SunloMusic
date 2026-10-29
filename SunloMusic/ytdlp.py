import aiohttp, asyncio, yt_dlp, os
from urllib.parse import urlparse
from SunloMusic.config import config
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

API_HEADERS = {"X-API-Key": config.ONEGRAB_API_KEY, "Accept": "application/json"}
DOWNLOAD_DIR = "cache/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ✅ Removed "extract_flat": True so yt-dlp fetches duration & thumbnail
YDL_SEARCH_OPTS = {
    "quiet": True, 
    "no_warnings": True, 
    "noplaylist": True, 
    "nocheckcertificate": True
}

def _search_ytdlp_sync(query: str):
    try:
        with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} song audio", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                return info["entries"][0]
    except Exception as e: LOGGER.error(f"yt-dlp search error: {e}")
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
        loop = asyncio.get_running_loop()
        try: ytdlp_info = await asyncio.wait_for(loop.run_in_executor(None, _search_ytdlp_sync, query), timeout=20.0)
        except: ytdlp_info = None
            
        if ytdlp_info and ytdlp_info.get("url"):
            webpage_url = ytdlp_info.get("url")
            
            thumb_url = ""
            if ytdlp_info.get("thumbnails"):
                thumb_url = ytdlp_info["thumbnails"][-1]["url"]
            elif ytdlp_info.get("id"):
                thumb_url = f"https://i.ytimg.com/vi/{ytdlp_info['id']}/hqdefault.jpg"
                
            fallback_meta = {
                "title": ytdlp_info.get("title", "Unknown"), 
                "duration": int(ytdlp_info.get("duration") or 0),
                "thumbnail": thumb_url
            }
        else:
            search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
            if search_data and search_data.get("results"):
                track = search_data["results"][0]
                webpage_url = track.get("webpage_url") or track.get("url")
                fallback_meta = {
                    "title": track.get("title", "Unknown"),
                    "duration": int(track.get("duration") or 0),
                    "thumbnail": track.get("thumbnail", "")
                }

    if not webpage_url: 
        LOGGER.error("❌ No webpage URL found.")
        return None

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
