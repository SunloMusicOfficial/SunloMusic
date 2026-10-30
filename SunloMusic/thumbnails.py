import os
from PIL import Image, ImageDraw
from SunloMusic.logger import LOGGER
from SunloMusic.database import get_custom_thumb

CACHE = "cache/thumbnails"
os.makedirs(CACHE, exist_ok=True)
DEFAULT_THUMB_PATH = f"{CACHE}/default_sunlo.jpg"

def get_default_thumb():
    if os.path.exists(DEFAULT_THUMB_PATH):
        return DEFAULT_THUMB_PATH
    try:
        # ✅ 100% Guaranteed Fallback Image (Agar internet URL fail ho jaye)
        img = Image.new('RGB', (1280, 720), color=(20, 25, 35))
        d = ImageDraw.Draw(img)
        d.text((450, 320), "SunloMusic", fill=(0, 255, 255))
        d.text((480, 360), "Playing Now", fill=(200, 200, 200))
        img.save(DEFAULT_THUMB_PATH, "JPEG", quality=90)
        return DEFAULT_THUMB_PATH
    except Exception as e:
        LOGGER.error(f"Default thumb generation error: {e}")
        return None

async def generate_thumbnail(chat_id: int, url: str, title: str, duration: str, req: str):
    try:
        custom_thumb = await get_custom_thumb(chat_id)
        if custom_thumb:
            return custom_thumb

        if not url or not url.startswith("http"):
            return get_default_thumb()
            
        return url
    except Exception as e:
        LOGGER.error(f"Thumbnail error: {e}")
        return get_default_thumb()
