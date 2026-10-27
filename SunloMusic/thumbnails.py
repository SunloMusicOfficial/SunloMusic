import os, aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from SunloMusic.logger import LOGGER

CACHE = "cache/thumbnails"
os.makedirs(CACHE, exist_ok=True)

async def generate_thumbnail(url: str, title: str, duration: str, req: str):
    if not url: return None
    try:
        path = f"{CACHE}/{abs(hash(url))}.jpg"
        if os.path.exists(path): return path
        
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status == 200: 
                    with open(path, "wb") as f:
                        f.write(await r.read())
                        
        img = Image.open(path).convert("RGB").resize((1280, 720)).filter(ImageFilter.GaussianBlur(20))
        overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 180))
        img = Image.alpha_composite(img.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(img)
        
        # Fallback in case custom font is missing
        try:
            font = ImageFont.truetype("assets/fonts/bold.ttf", 60)
        except Exception:
            font = ImageFont.load_default()
            
        draw.text((100, 300), f"🎶 {title[:35]}", fill="white", font=font)
        draw.text((100, 400), f"⏱ {duration}   |   👤 {req}", fill="#a0a0ff", font=font)
        
        img.convert("RGB").save(path, "JPEG", quality=90)
        return path
    except Exception as e:
        LOGGER.error(f"Thumbnail error: {e}")
        return None
