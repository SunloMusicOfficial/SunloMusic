import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.logger import LOGGER

STICKER_DIR = "cache/stickers"
os.makedirs(STICKER_DIR, exist_ok=True)

def create_sticker_image(text: str, output_path: str):
    # 512x512 transparent image
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Font load karo (Bold arial ya default)
    try:
        font = ImageFont.truetype("assets/fonts/bold.ttf", 70)
    except:
        font = ImageFont.load_default()

    # Text ka size calculate karo center karne ke liye
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (512 - text_width) / 2
    y = (512 - text_height) / 2

    # ✅ Neon Glow Effect (Text ko multiple baar draw karke blur karenge)
    glow_layer = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    
    # Glow color (Cyan/Blue)
    glow_draw.text((x, y), text, font=font, fill=(0, 255, 255, 255))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
    
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # Main White Text with Black Outline (Taaki clear dikhe)
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    
    img.save(output_path, "PNG")
    return output_path

def convert_to_webm(image_path: str, output_path: str):
    # FFmpeg command for 3-sec video with slight zoom effect
    command = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", "scale=512:512,format=yuva420p,zoompan=z='min(zoom+0.0015,1.5)':d=60:s=512x512",
        "-c:v", "libvpx-vp9",
        "-b:v", "256k",
        "-crf", "35",
        "-t", "3.0",
        "-an", output_path
    ]
    
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        LOGGER.error(f"FFmpeg Error: {e}")
        return False

@bot.on_message(filters.command("msticker") & filters.group)
@catch_errors
async def make_sticker(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/msticker PAYMENT PROOF</code>")
    
    text = " ".join(m.command[1:]).upper()
    status = await m.reply_text(f"⏳ <b>Creating premium sticker for:</b> <i>{text}</i>...")
    
    img_path = f"{STICKER_DIR}/{abs(hash(text))}.png"
    webm_path = f"{STICKER_DIR}/{abs(hash(text))}.webm"
    
    try:
        # 1. Image Generate
        create_sticker_image(text, img_path)
        
        # 2. Convert to Animated WebM
        success = convert_to_webm(img_path, webm_path)
        
        if success and os.path.exists(webm_path):
            # Size check (Telegram limit: 256KB)
            if os.path.getsize(webm_path) > 256 * 1024:
                LOGGER.warning("Sticker size > 256KB, quality reduce kar rahe hain...")
                # Agar size zyada hui toh aur compress karo
                subprocess.run(["ffmpeg", "-y", "-i", webm_path, "-b:v", "150k", "-crf", "40", f"{webm_path}_small.webm"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(f"{webm_path}_small.webm"):
                    os.replace(f"{webm_path}_small.webm", webm_path)

            # 3. Send Sticker
            await m.reply_sticker(webm_path)
            await status.delete()
        else:
            await status.edit_text("❌ <b>Sticker banane me error aayi. Render logs check karo.</b>")
            
    except Exception as e:
        await status.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")
    finally:
        # Cleanup
        if os.path.exists(img_path): os.remove(img_path)
        if os.path.exists(webm_path): os.remove(webm_path)
