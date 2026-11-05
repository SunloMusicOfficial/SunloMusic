import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.logger import LOGGER

STICKER_DIR = "cache/stickers"
os.makedirs(STICKER_DIR, exist_ok=True)

# 1. Text to Animated Sticker (Neon Glow)
def create_sticker_image(text: str, output_path: str):
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("assets/fonts/bold.ttf", 70)
    except: font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    x, y = (512 - (bbox[2] - bbox[0])) / 2, (512 - (bbox[3] - bbox[1])) / 2

    glow_layer = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.text((x, y), text, font=font, fill=(0, 255, 255, 255))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
    
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
    img.save(output_path, "PNG")
    return output_path

def convert_to_webm(image_path: str, output_path: str, is_zoom: bool = False):
    if is_zoom:
        # ✅ Photo se Live Sticker (Zoom-in effect)
        vf_filter = "scale=512:512:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(zoom+0.0015,1.5)':d=60:s=512x512,format=yuva420p"
    else:
        # ✅ Text sticker filter
        vf_filter = "scale=512:512,format=yuva420p,zoompan=z='min(zoom+0.0015,1.5)':d=60:s=512x512"

    command = [
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-vf", vf_filter,
        "-c:v", "libvpx-vp9", "-b:v", "256k", "-crf", "35",
        "-t", "3.0", "-an", output_path
    ]
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        LOGGER.error(f"FFmpeg Error: {e}")
        return False

@bot.on_message(filters.command("msticker") & filters.group)
@catch_errors
async def make_text_sticker(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/msticker PAYMENT PROOF</code>")
    
    text = " ".join(m.command[1:]).upper()
    status = await m.reply_text(f"⏳ <b>Creating premium text sticker for:</b> <i>{text}</i>...")
    
    img_path = f"{STICKER_DIR}/{abs(hash(text))}.png"
    webm_path = f"{STICKER_DIR}/{abs(hash(text))}.webm"
    
    try:
        create_sticker_image(text, img_path)
        if convert_to_webm(img_path, webm_path, is_zoom=False) and os.path.exists(webm_path):
            if os.path.getsize(webm_path) > 256 * 1024:
                subprocess.run(["ffmpeg", "-y", "-i", webm_path, "-b:v", "150k", "-crf", "40", f"{webm_path}_small.webm"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(f"{webm_path}_small.webm"): os.replace(f"{webm_path}_small.webm", webm_path)
            await m.reply_sticker(webm_path)
            await status.delete()
        else:
            await status.edit_text("❌ <b>Failed to create sticker.</b>")
    except Exception as e:
        await status.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")
    finally:
        if os.path.exists(img_path): os.remove(img_path)
        if os.path.exists(webm_path): os.remove(webm_path)

# ✅ Naya Feature: Photo se Live Sticker
@bot.on_message(filters.command("anim") & filters.group)
@catch_errors
async def make_photo_sticker(_, m):
    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply_text("❌ <b>Usage:</b> Kisi photo ko reply karke <code>/anim</code> bhejo.")
    
    status = await m.reply_text("⏳ <b>Creating live sticker from your photo...</b>")
    
    photo_path = f"{STICKER_DIR}/{abs(hash(m.reply_to_message.photo.file_id))}.jpg"
    webm_path = f"{STICKER_DIR}/{abs(hash(m.reply_to_message.photo.file_id))}.webm"
    
    try:
        # Photo download karo
        await m.reply_to_message.download(file_name=photo_path)
        
        if not os.path.exists(photo_path):
            return await status.edit_text("❌ <b>Failed to download photo.</b>")

        # Convert to WebM with Zoom animation
        if convert_to_webm(photo_path, webm_path, is_zoom=True) and os.path.exists(webm_path):
            if os.path.getsize(webm_path) > 256 * 1024:
                subprocess.run(["ffmpeg", "-y", "-i", webm_path, "-b:v", "150k", "-crf", "40", f"{webm_path}_small.webm"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(f"{webm_path}_small.webm"): os.replace(f"{webm_path}_small.webm", webm_path)
                
            await m.reply_sticker(webm_path)
            await status.delete()
        else:
            await status.edit_text("❌ <b>Failed to convert photo. Check Render logs.</b>")
    except Exception as e:
        LOGGER.error(f"Photo Sticker Error: {e}")
        await status.edit_text("❌ <b>Error creating sticker.</b>")
    finally:
        if os.path.exists(photo_path): os.remove(photo_path)
        if os.path.exists(webm_path): os.remove(webm_path)
