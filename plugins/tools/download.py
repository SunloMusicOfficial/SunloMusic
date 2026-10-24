import os
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp

@Client.on_message(filters.command(["song", "mp3", "video", "mp4"]))
async def download_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:**  or ")
        
    query = message.text.split(None, 1)[1]
    is_video = message.command[0] in ["video", "mp4"]
    status = await message.reply_text("📥 **Downloading... Please wait!**")
    
    ydl_opts = {
        "format": "best" if is_video else "bestaudio/best",
        "outtmpl": "cache/%(title)s.%(ext)s",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}] if not is_video else [],
        "quiet": True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
            filename = ydl.prepare_filename(info)
            if not is_video: filename = filename.rsplit(".", 1)[0] + ".mp3"
            
        if is_video:
            await message.reply_video(filename, caption=f"🎬 **{info['title']}**")
        else:
            await message.reply_audio(filename, caption=f"🎵 **{info['title']}**")
            
        os.remove(filename)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ Failed to download: {e}")
