import aiohttp
import os
import io
from PIL import Image
from utils.logger import LOGGER

async def gen_thumb(title: str, image_url: str):
    try:
        os.makedirs("cache", exist_ok=True)
        filepath = f"cache/thumb_{hash(title)}.png"
        
        if not image_url:
            return None
            
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    
        # Resize image for premium look
        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        img = img.resize((1280, 720))
        img.save(filepath)
        
        return filepath
    except Exception as e:
        LOGGER.error(f"Thumbnail Error: {e}")
        return None
