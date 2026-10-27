import os, aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
CACHE = "cache/thumbnails"
os.makedirs(CACHE, exist_ok=True)

async def generate_thumbnail(url: str, title: str, duration: str, req: str):
    if not url: return None
    try:
        path = f"{CACHE}/{abs(hash(url))}.jpg"
        if os.path.exists(path): return path
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status == 200: open(path, "wb").write(await r.read())
        img = Image.open(path).convert("RGB").resize((1280, 720)).filter(ImageFilter.GaussianBlur(15))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((100, 300), f"Playing: {title[:30]}", fill="white", font=font)
        img.save(path, "JPEG")
        return path
    except Exception: return None
