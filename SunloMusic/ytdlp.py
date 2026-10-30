import aiohttp, asyncio, yt_dlp, os
from urllib.parse import urlparse
from SunloMusic.config import config
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

API_HEADERS = {"X-API-Key": config.ONEGRAB_API_KEY, "Accept": "application/json"}
DOWNLOAD_DIR = "cache/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def _search_ytdlp_sync(query: str):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "extract_flat": True, "nocheckcertificate": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} song audio", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                entry = info["entries"][0]
                thumb = entry.get("thumbnails", [{}])[-1].get("url") if entry.get("thumbnails") else f"https://i.ytimg.com/vi/{entry['id']}/hqdefault.jpg"
                return {
                    "title": entry.get("title", query),
                    "url": f"https://www.youtube.com/watch?v={entry['id']}",
                    "duration": int(entry.get("duration") or 0),
                    "thumbnail": thumb
                }
    except Exception as e: LOGGER.error(f"yt-dlp search error: {e}")
    return None

def _search_ytdlp_multi_sync(query: str, limit: int = 10):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "extract_flat": True, "nocheckcertificate": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            results = []
            if info and "entries" in info:
                for e in info["entries"]:
                    if e:
                        thumb = f"https://i.ytimg.com/vi/{e.get('id')}/hqdefault.jpg" if e.get("id") else ""
                        results.append({"title": e.get("title", "Unknown"), "url": f"https://www.youtube.com/watch?v={e.get('id')}" if e.get("id") else e.get("url"), "duration": int(e.get("duration") or 0), "thumbnail": thumb})
            return results
    except Exception as e:
        LOGGER.error(f"yt-dlp multi search error: {e}")
        return []

async def _api_request(endpoint: str, params: dict) -> dict | None:
    url = f"{config.ONEGRAB_API_URL.rstrip('/')}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=API_HEADERS, params=params, timeout=10) as resp: # Timeout 10s
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
    loop = asyncio.get_running_loop()

    if query.startswith("http"):
        try:
            def _get_info(url):
                with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True, "extract_flat": True, "nocheckcertificate": True}) as ydl:
                    return ydl.extract_info(url, download=False)
            info = await loop.run_in_executor(None, _get_info, query)
            if info:
                thumb = info.get("thumbnail") or (info.get("thumbnails", [{}])[-1].get("url") if info.get("thumbnails") else "")
                fallback_meta = {"title": info.get("title", "Unknown"), "duration": int(info.get("duration") or 0), "thumbnail": thumb}
                webpage_url = info.get("webpage_url", query)
        except Exception: pass
    else:
        try: ytdlp_info = await asyncio.wait_for(loop.run_in_executor(None, _search_ytdlp_sync, query), timeout=6.0) # 6 sec timeout
        except: ytdlp_info = None
            
        if ytdlp_info and ytdlp_info.get("url"):
            webpage_url = ytdlp_info["url"]
            fallback_meta = ytdlp_info
        else:
            search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
            if search_data and search_data.get("results"):
                track = search_data["results"][0]
                webpage_url = track.get("url")
                fallback_meta = {"title": track.get("title", query), "duration": int(track.get("duration") or 0), "thumbnail": track.get("thumbnail", "")}

    if not webpage_url: return None

    req_type = "video" if video else "audio"
    track_data = await _api_request("/api/track", {"url": webpage_url, "type": req_type})
    
    if track_data:
        result = track_data
        if "results" in track_data and isinstance(track_data["results"], list) and len(track_data["results"]) > 0:
            result = track_data["results"][0]

        cdnurl = result.get("cdnurl") or result.get("download_url") or result.get("audio_url") or result.get("video_url")
        
        if cdnurl:
            final_thumb = fallback_meta.get("thumbnail") or result.get("thumbnail", "")
            final_dur = fallback_meta.get("duration") or int(result.get("duration") or 0)
            final_title = fallback_meta.get("title") or result.get("title", "Unknown")
            
            if "t.me" in cdnurl or "telegram.me" in cdnurl:
                local_path = await _download_telegram_cdn(cdnurl)
                if local_path: return {"title": final_title, "url": local_path, "duration": final_dur, "thumbnail": final_thumb, "webpage_url": webpage_url}
            else:
                return {"title": final_title, "url": cdnurl, "duration": final_dur, "thumbnail": final_thumb, "webpage_url": webpage_url}
    
    if fallback_meta.get("title"):
        return {"title": fallback_meta.get("title"), "url": webpage_url, "duration": fallback_meta.get("duration", 0), "thumbnail": fallback_meta.get("thumbnail", ""), "webpage_url": webpage_url}
    return None

def _download_file_sync(url: str, video: bool = False, max_duration: int = 3600):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "nocheckcertificate": True, "match_filter": yt_dlp.utils.match_filter_func(f"duration < {max_duration}")}
        if video:
            ydl_opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best"
            ydl_opts["merge_output_format"] = "mp4"
        else:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        
        ydl_opts["outtmpl"] = f"{DOWNLOAD_DIR}/%(id)s.%(ext)s"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = ydl.prepare_filename(info)
            if not video:
                base = os.path.splitext(final_path)[0]
                if os.path.exists(base + ".mp3"): final_path = base + ".mp3"
            return {"path": final_path, "title": info.get("title", "Unknown"), "duration": int(info.get("duration") or 0), "thumbnail": info.get("thumbnail", "")}
    except Exception as e:
        LOGGER.error(f"File download error: {e}")
        return None

async def download_media_file(query: str, video: bool = False, max_duration: int = 3600):
    url = query
    if not query.startswith("http"):
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, _search_ytdlp_sync, query)
        if not info: return None
        url = info["url"]
    
    loop = asyncio.get_running_loop()
    try: return await asyncio.wait_for(loop.run_in_executor(None, _download_file_sync, url, video, max_duration), timeout=180.0)
    except asyncio.TimeoutError:
        LOGGER.error("Download timed out")
        return None

def cleanup_download(path: str):
    if path and os.path.exists(path):
        try: os.remove(path)
        except: pass
