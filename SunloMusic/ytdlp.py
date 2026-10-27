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

    # Agar pehle se hi direct media URL hai (m4a/mp4/mp3)
    if any(query.lower().endswith(ext) for ext in (".m4a", ".mp4", ".mp3", ".webm")):
        return {
            "title": query.split("/")[-1] or "Unknown Track",
            "url": query, "duration": 0, "thumbnail": "", "webpage_url": query
        }

    webpage_url = query

    # 1. Agar URL nahi hai, toh pehle OneGrab Search API se webpage_url nikaalo
    if not query.startswith("http"):
        search_data = await _api_request("/api/search", {"query": query, "platform": "youtube"})
        if not search_data or not search_data.get("results"):
            LOGGER.error(f"❌ Search failed for: {query}")
            return None
        track = search_data["results"][0]
        webpage_url = track.get("webpage_url") or track.get("url")
        if not webpage_url:
            return None

    # 2. Get Direct Stream URL from OneGrab
    track_data = await _api_request("/api/get_url", {"url": webpage_url})
    if not track_data or not track_data.get("results"):
        LOGGER.error(f"❌ Get URL failed for: {webpage_url}")
        return None

    result = track_data["results"][0]
    
    # Direct stream link extract karo (cdnurl / url / download_url)
    direct_url = result.get("cdnurl") or result.get("url") or result.get("download_url")
    
    if not direct_url or "youtube.com" in direct_url or "youtu.be" in direct_url:
        LOGGER.error(f"❌ OneGrab returned non-direct URL: {direct_url}")
        return None

    return {
        "title": result.get("title", "Unknown Track"),
        "url": direct_url,
        "duration": int(result.get("duration") or 0),
        "thumbnail": result.get("thumbnail", ""),
        "webpage_url": webpage_url
    }
