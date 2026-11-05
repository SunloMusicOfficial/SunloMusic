import aiohttp, asyncio, yt_dlp, os, time
from urllib.parse import urlparse
from SunloMusic.config import config
from SunloMusic.logger import LOGGER
import SunloMusic.bot as bot_module

DOWNLOAD_DIR = "cache/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_SEARCH_CACHE = {}
_CACHE_TTL = 3600
EXTRACTOR_ARGS = {"youtube": {"player_client": ["android", "ios", "web_safari"]}}

def _search_ytdlp_sync(query: str):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "extract_flat": True, "nocheckcertificate": True, "extractor_args": EXTRACTOR_ARGS, "match_filter": yt_dlp.utils.match_filter_func("duration < 1800")}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} song audio", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                entry = info["entries"][0]
                vid_id = entry.get("id")
                thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else ""
                return {"title": entry.get("title", query), "video_id": vid_id, "duration": int(entry.get("duration") or 0), "thumbnail": thumb}
    except Exception as e: LOGGER.error(f"yt-dlp search error: {e}")
    return None

def _search_ytdlp_multi_sync(query: str, limit: int = 10):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "extract_flat": True, "nocheckcertificate": True, "extractor_args": EXTRACTOR_ARGS}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            results = []
            if info and "entries" in info:
                for e in info["entries"]:
                    if e:
                        vid_id = e.get("id")
                        thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else ""
                        results.append({"title": e.get("title", "Unknown"), "video_id": vid_id, "url": f"https://youtube.com/watch?v={vid_id}", "duration": int(e.get("duration") or 0), "thumbnail": thumb})
            return results
    except Exception as e: LOGGER.error(f"yt-dlp multi search error: {e}")
    return []

async def _download_shruti(video_id: str, is_video: bool) -> str | None:
    if not video_id: return None
    ext = ".mp4" if is_video else ".mp3"
    file_path = f"{DOWNLOAD_DIR}/{video_id}{ext}"
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
    if not config.SHRUTI_API_KEY: return None

    url = f"{config.SHRUTI_API_URL.rstrip('/')}/download"
    params = {"url": video_id, "type": "video" if is_video else "audio", "api_key": config.SHRUTI_API_KEY}
    try:
        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=600 if is_video else 300)
            async with session.get(url, params=params, timeout=timeout) as resp:
                if resp.status == 200:
                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(131072): f.write(chunk)
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
    except Exception as e:
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass
    return None

async def get_autoplay(video_id: str, seed_id: str = None) -> list:
    if not config.SHRUTI_API_KEY: return []
    url = f"{config.SHRUTI_API_URL.rstrip('/')}/autoplay"
    params = {"video_id": video_id, "api_key": config.SHRUTI_API_KEY}
    if seed_id: params["seed_id"] = seed_id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as resp:
                if resp.status == 200: return (await resp.json()).get("tracks", [])
    except: pass
    return []

def _get_spotify_title(url: str):
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if info: return info.get("title", "")
    except: pass
    return ""

async def extract_audio(query: str, video: bool = False) -> dict | None:
    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {"title": "Direct Link", "url": query, "duration": 0, "thumbnail": "", "webpage_url": query}

    if "open.spotify.com" in query or "spotify.link" in query:
        loop = asyncio.get_running_loop()
        spotify_title = await loop.run_in_executor(None, _get_spotify_title, query)
        if spotify_title: query = spotify_title

    cache_key = f"{query}_{video}"
    if cache_key in _SEARCH_CACHE:
        data, t = _SEARCH_CACHE[cache_key]
        if time.time() - t < _CACHE_TTL:
            if not data["url"].startswith("http") and not os.path.exists(data["url"]): pass
            else: return data

    webpage_url = query
    meta = {}
    loop = asyncio.get_running_loop()

    if not query.startswith("http"):
        try: ytdlp_info = await asyncio.wait_for(loop.run_in_executor(None, _search_ytdlp_sync, query), timeout=10.0)
        except: ytdlp_info = None
        if ytdlp_info and ytdlp_info.get("video_id"):
            webpage_url = f"https://youtube.com/watch?v={ytdlp_info['video_id']}"
            meta = ytdlp_info
    else:
        try:
            def _get_info(url):
                with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "nocheckcertificate": True, "extractor_args": EXTRACTOR_ARGS}) as ydl:
                    return ydl.extract_info(url, download=False)
            info = await loop.run_in_executor(None, _get_info, query)
            if info:
                vid_id = info.get("id")
                meta = {"title": info.get("title", "Unknown"), "video_id": vid_id, "duration": int(info.get("duration") or 0), "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"}
                webpage_url = info.get("webpage_url", query)
        except: pass

    if not meta.get("video_id"): return None
    local_path = await _download_shruti(meta["video_id"], video)
    if not local_path: return None

    res = {"title": meta.get("title", "Unknown"), "url": local_path, "duration": meta.get("duration", 0), "thumbnail": meta.get("thumbnail", ""), "webpage_url": webpage_url, "video_id": meta["video_id"]}
    _SEARCH_CACHE[cache_key] = (res, time.time())
    return res

async def download_media_file(query: str, video: bool = False, max_duration: int = 3600):
    res = await extract_audio(query, video)
    if res and res.get("url"): return {"path": res["url"], "title": res["title"], "duration": res["duration"], "thumbnail": res["thumbnail"]}
    return None

def cleanup_download(path: str):
    if path and os.path.exists(path):
        try: os.remove(path)
        except: pass
