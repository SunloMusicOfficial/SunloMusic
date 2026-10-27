import os, aiohttp, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from SunloMusic.logger import LOGGER

CACHE = "cache/thumbnails"
os.makedirs(CACHE, exist_ok=True)

async def generate_thumbnail(url: str, title: str, duration: str, req: str):
    if not url: return None
    try:
        file_hash = hashlib.md5(url.encode()).hexdigest()
        path = f"{CACHE}/{file_hash}.jpg"
        if os.path.exists(path): return path
        
        # 1. Download Image
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status == 200: 
                    with open(path, "wb") as f: f.write(await r.read())
                else: return None
                        
        # 2. Process Image (Clear background, no blur)
        img = Image.open(path).convert("RGB").resize((1280, 720))
        
        # Slight dark overlay to make the play button visible
        overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 80))
        img = Image.alpha_composite(img.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(img)
        
        # 3. Draw Center Play Button (Circle + Triangle)
        center_x, center_y = 640, 360
        radius = 80
        # Draw semi-transparent black circle
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=(0, 0, 0, 150))
        # Draw white play triangle
        triangle = [(center_x - 20, center_y - 35), (center_x - 20, center_y + 35), (center_x + 40, center_y)]
        draw.polygon(triangle, fill=(255, 255, 255, 230))
        
        img.convert("RGB").save(path, "JPEG", quality=95)
        return path
    except Exception as e:
        LOGGER.error(f"Thumbnail error: {e}")
        return None
