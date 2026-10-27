import aiohttp
from urllib.parse import quote
from SunloMusic.config import config
from SunloMusic.logger import LOGGER

API_HEADERS = {
    "X-API-Key": config.ONEGRAB_API_KEY,
    "Accept": "application/json"
}

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

async def extract_audio(query: str) -> dict | None:
    if not config.ONEGRAB_API_KEY:
        LOGGER.error("❌ ONEGRAB_API_KEY is missing in .env")
        return None

    # Agar pehle se hi direct media URL hai
    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {"title": "Direct Link", "url": query, "duration": 0, "thumbnail": "", "webpage_url": query}

    webpage_url = query

    # 1. Search API
    if not query.startswith("http"):
        search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
        if not search_data or not search_data.get("results"):
            LOGGER.error(f"❌ Search failed for: {query}")
            return None
        track = search_data["results"][0]
        webpage_url = track.get("webpage_url") or track.get("url")
        if not webpage_url:
            return None

    # 2. Get Stream URL API
    # Type=audio parameter add kiya taaki API ko pata chale audio chahiye
    track_data = await _api_request("/api/get_url", {"url": webpage_url, "type": "audio"})
    
    if not track_data:
        LOGGER.error("❌ API returned empty response for get_url")
        return None

    # 🔍 DEBUG LOG: Render logs me pura JSON print karega
    LOGGER.info(f"🔍 OneGrab GetURL Response: {track_data}")

    if not track_data.get("results"):
        LOGGER.error("❌ API response has no 'results' key")
        return None

    result = track_data["results"][0]
    
    # 3. Smart Direct URL Extractor
    # API alag-alag keys use kar sakti hai, hum sab check kar rahe hain
    direct_url = None
    possible_keys = ["cdnurl", "audio_url", "video_url", "download_url", "audio", "video", "url"]
    
    for key in possible_keys:
        val = result.get(key)
        # Check karo ki link youtube.com toh nahi hai aur direct media lag raha hai
        if val and isinstance(val, str) and "youtube.com" not in val and "youtu.be" not in val:
            direct_url = val
            break

    if not direct_url:
        LOGGER.error(f"❌ API ne direct link nahi diya. Available keys: {list(result.keys())}")
        return None

    return {
        "title": result.get("title", "Unknown Track"),
        "url": direct_url,
        "duration": int(result.get("duration") or 0),
        "thumbnail": result.get("thumbnail", ""),
        "webpage_url": webpage_url
    }
