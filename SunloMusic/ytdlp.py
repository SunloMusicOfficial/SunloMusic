import aiohttp
from urllib.parse import quote
from SunloMusic.config import config
from SunloMusic.logger import LOGGER

API_HEADERS = {
    "X-API-Key": config.ONEGRAB_API_KEY,
    "Accept": "application/json"
}

async def _search_api(query: str) -> dict | None:
    """Search for a song using OneGrab API"""
    url = f"{config.ONEGRAB_API_URL}/api/search?query={quote(query)}&platform=youtube"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=API_HEADERS, timeout=20) as resp:
                if resp.status != 200:
                    LOGGER.error(f"OneGrab Search API Error: {resp.status}")
                    return None
                data = await resp.json()
                results = data.get("results", [])
                if not results: return None
                
                # Return the first result
                track = results[0]
                return {
                    "title": track.get("title", "Unknown"),
                    "url": track.get("url"), # This is the webpage URL
                    "duration": int(track.get("duration") or 0),
                    "thumbnail": track.get("thumbnail", ""),
                    "webpage_url": track.get("url", "")
                }
        except Exception as e:
            LOGGER.error(f"OneGrab Search Exception: {e}")
            return None

async def _get_direct_url(webpage_url: str) -> dict | None:
    """Get direct stream URL from a YouTube/Spotify link using OneGrab API"""
    url = f"{config.ONEGRAB_API_URL}/api/get_url?url={quote(webpage_url)}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=API_HEADERS, timeout=20) as resp:
                if resp.status != 200:
                    LOGGER.error(f"OneGrab GetURL API Error: {resp.status}")
                    return None
                data = await resp.json()
                results = data.get("results", [])
                if not results: return None
                
                track = results[0]
                # API usually returns 'url' (webpage) and 'cdnurl' (direct stream)
                direct_stream = track.get("cdnurl") or track.get("url")
                
                return {
                    "title": track.get("title", "Unknown"),
                    "url": direct_stream,
                    "duration": int(track.get("duration") or 0),
                    "thumbnail": track.get("thumbnail", ""),
                    "webpage_url": track.get("url", webpage_url)
                }
        except Exception as e:
            LOGGER.error(f"OneGrab GetURL Exception: {e}")
            return None

async def extract_audio(query: str) -> dict | None:
    """Main function to extract audio using OneGrab API"""
    if not config.ONEGRAB_API_KEY:
        LOGGER.error("❌ ONEGRAB_API_KEY is missing in .env")
        return None

    # If query is a URL, directly get stream URL
    if query.startswith("http://") or query.startswith("https://"):
        return await _get_direct_url(query)
    else:
        # Otherwise, search first, then get direct URL
        search_result = await _search_api(query)
        if search_result and search_result.get("webpage_url"):
            return await _get_direct_url(search_result["webpage_url"])
        return search_result
