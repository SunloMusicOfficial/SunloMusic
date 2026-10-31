import aiohttp, asyncio, yt_dlp, os, time, subprocess
from urllib.parse import urlparse
from SunloMusic.config import config
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

API_HEADERS = {"X-API-Key": config.ONEGRAB_API_KEY, "Accept": "application/json"}
DOWNLOAD_DIR = "cache/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_SEARCH_CACHE = {}
_CACHE_TTL = 3600

def _search_ytdlp_sync(query: str):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "extract_flat": True, "nocheckcertificate": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} song audio", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                entry = info["entries"][0]
                vid_id = entry.get("id")
                thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else ""
                return {
                    "title": entry.get("title", query),
                    "url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else entry.get("url"),
                    "duration": int(entry.get("duration") or 0),
                    "thumbnail": thumb
                }
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

def _convert_to_mp4(input_path):
    output_path = os.path.splitext(input_path)[0] + ".mp4"
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0: 
        return output_path
    try:
        LOGGER.info(f"🎬 Converting {input_path} to MP4...")
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-c:a", "aac", output_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        if os.path.exists(output_path):
            os.remove(input_path)
            return output_path
    except Exception as e:
        LOGGER.error(f"FFmpeg conversion error: {e}")
    return input_path

async def _download_file(url: str, video: bool) -> str | None:
    # Determine extension from URL
    ext = ".mp4" if video else ".m4a"
    if url.endswith(".webm"): ext = ".webm"
    elif url.endswith(".mp3"): ext = ".mp3"
    elif url.endswith(".m4a"): ext = ".m4a"
    
    file_path = f"{DOWNLOAD_DIR}/{abs(hash(url))}{ext}"
    if os.path.exists(file_path): return file_path
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as resp:
                if resp.status == 200:
                    with open(file_path, "wb") as f: f.write(await resp.read())
                    return file_path
    except Exception as e:
        LOGGER.error(f"Download error: {e}")
    return None

async def extract_audio(query: str, video: bool = False) -> dict | None:
    if not config.ONEGRAB_API_KEY: 
        LOGGER.error("❌ ONEGRAB_API_KEY missing in Render!")
        return None
        
    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {"title": "Direct Link", "url": query, "duration": 0, "thumbnail": "", "webpage_url": query}

    cache_key = f"{query}_{video}"
    if cache_key in _SEARCH_CACHE:
        data, t = _SEARCH_CACHE[cache_key]
        if time.time() - t < _CACHE_TTL:
            # Check if it's a local file that still exists
            if not data["url"].startswith("http") and not os.path.exists(data["url"]):
                pass # Bypass cache if file deleted
            else:
                return data

    webpage_url = query
    meta = {}
    loop = asyncio.get_running_loop()

    if not query.startswith("http"):
        try: ytdlp_info = await asyncio.wait_for(loop.run_in_executor(None, _search_ytdlp_sync, query), timeout=8.0)
        except: ytdlp_info = None
            
        if ytdlp_info and ytdlp_info.get("url"):
            webpage_url = ytdlp_info["url"]
            meta = ytdlp_info
        else:
            search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
            if search_data and search_data.get("results"):
                track = search_data["results"][0]
                webpage_url = track.get("url")
                vid_id = ""
                if "v=" in webpage_url:
                    vid_id = webpage_url.split("v=")[1].split("&")[0]
                thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else track.get("thumbnail", "")
                meta = {"title": track.get("title", query), "duration": int(track.get("duration") or 0), "thumbnail": thumb}

    if not webpage_url: return None

    req_type = "video" if video else "audio"
    track_data = await _api_request("/api/track", {"url": webpage_url, "type": req_type})
    
    if track_data:
        result = track_data
        if "results" in track_data and isinstance(track_data["results"], list) and len(track_data["results"]) > 0:
            result = track_data["results"][0]

        cdnurl = result.get("cdnurl") or result.get("download_url") or result.get("audio_url") or result.get("video_url")
        
        if cdnurl:
            final_thumb = meta.get("thumbnail") or result.get("thumbnail", "")
            final_dur = meta.get("duration") or int(result.get("duration") or 0)
            final_title = meta.get("title") or result.get("title", "Unknown")
            
            if "t.me" in cdnurl or "telegram.me" in cdnurl:
                local_path = await _download_telegram_cdn(cdnurl)
                if local_path: 
                    res = {"title": final_title, "url": local_path, "duration": final_dur, "thumbnail": final_thumb, "webpage_url": webpage_url}
                    _SEARCH_CACHE[cache_key] = (res, time.time())
                    return res
            else:
                res = {"title": final_title, "url": cdnurl, "duration": final_dur, "thumbnail": final_thumb, "webpage_url": webpage_url}
                _SEARCH_CACHE[cache_key] = (res, time.time())
                return res
    
    return None

async def download_media_file(query: str, video: bool = False, max_duration: int = 3600):
    res = await extract_audio(query, video)
    if res and res.get("url"):
        if res["url"].startswith("http"):
            path = await _download_file(res["url"], video)
            if path:
                # ✅ FORCE MP4 CONVERSION HERE
                if video and path.endswith(".webm"):
                    path = _convert_to_mp4(path)
                return {"path": path, "title": res["title"], "duration": res["duration"], "thumbnail": res["thumbnail"]}
        else:
            # Already local
            path = res["url"]
            if video and path.endswith(".webm"):
                path = _convert_to_mp4(path)
            return {"path": path, "title": res["title"], "duration": res["duration"], "thumbnail": res["thumbnail"]}
    return None

def cleanup_download(path: str):
    if path and os.path.exists(path):
        try: os.remove(path)
        except: pass
