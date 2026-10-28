import os, aiohttp, hashlib
from PIL import Image
from SunloMusic.logger import LOGGER
from SunloMusic.database import get_custom_thumb
import SunloMusic.bot as bot_module

CACHE = "cache/thumbnails"
os.makedirs(CACHE, exist_ok=True)

async def generate_thumbnail(chat_id: int, url: str, title: str, duration: str, req: str):
    try:
        # ✅ Check for Custom Thumbnail
        custom_thumb = await get_custom_thumb(chat_id)
        if custom_thumb and bot_module.bot:
            path = f"{CACHE}/custom_{chat_id}.jpg"
            if not os.path.exists(path):
                await bot_module.bot.download_media(custom_thumb, file_name=path)
            if os.path.exists(path):
                return path

        if not url: return None
        file_hash = hashlib.md5(url.encode()).hexdigest()
        path = f"{CACHE}/{file_hash}.jpg"
        if os.path.exists(path): return path
        
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status == 200: 
                    with open(path, "wb") as f: f.write(await r.read())
                else: return None
                        
        img = Image.open(path).convert("RGB").resize((1280, 720))
        img.save(path, "JPEG", quality=95)
        return path
    except Exception as e:
        LOGGER.error(f"Thumbnail error: {e}")
        return None
