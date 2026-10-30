import os
from SunloMusic.logger import LOGGER
from SunloMusic.database import get_custom_thumb
import SunloMusic.bot as bot_module

CACHE = "cache/thumbnails"
os.makedirs(CACHE, exist_ok=True)

async def generate_thumbnail(chat_id: int, url: str, title: str, duration: str, req: str):
    try:
        # ✅ Custom Thumb Check (If user set any)
        custom_thumb = await get_custom_thumb(chat_id)
        if custom_thumb:
            return custom_thumb

        # ✅ Return URL directly (Telegram fetches it instantly)
        if url and url.startswith("http"):
            return url
            
        return None
    except Exception as e:
        LOGGER.error(f"Thumbnail error: {e}")
        return None
