import os, aiohttp, hashlib
from PIL import Image
from SunloMusic.logger import LOGGER

CACHE = "cache/thumbnails"
os.makedirs(CACHE, exist_ok=True)

async def generate_thumbnail(url: str, title: str, duration: str, req: str):
    if not url: return None
    try:
        file_hash = hashlib.md5(url.encode()).hexdigest()
        path = f"{CACHE}/{file_hash}.jpg"
        if os.path.exists(path): return path
        
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status == 200: 
                    with open(path, "wb") as f: f.write(await r.read())
                else: return None
                        
        # Just resize and save, no text, no play button
        img = Image.open(path).convert("RGB").resize((1280, 720))
        img.save(path, "JPEG", quality=95)
        return path
    except Exception as e:
        LOGGER.error(f"Thumbnail error: {e}")
        return None
