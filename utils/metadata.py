import aiohttp
import re
from utils.logger import LOGGER

async def get_url_metadata(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    # Webpage se OpenGraph title nikalna
                    match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                    if match:
                        title = match.group(1)
                        # Spotify aur Apple ke faltu text ko clean karna
                        title = title.replace(" - song and lyrics by ", " ")
                        title = title.replace(" | Spotify", "")
                        title = title.replace(" - Single by ", " ")
                        title = title.replace(" on Apple Music", "")
                        return title
    except Exception as e:
        LOGGER.error(f"Metadata fetch error: {e}")
    return None
