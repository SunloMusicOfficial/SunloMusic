import os, asyncio
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER
from shazamio import Shazam
from SunloMusic.ytdlp import extract_audio

@bot.on_message(filters.voice | filters.audio | (filters.video & ~filters.command(["play", "vplay", "song"])) & filters.group)
@catch_errors
async def shazam_handler(_, m):
    # Ignore if it's a command
    if m.text and m.text.startswith("/"): return
    
    msg = await m.reply_text("🎧 <b>Listening to your voice/audio...</b>")
    path = await m.download()
    
    try:
        shazam = Shazam()
        out = await shazam.recognize(path)
        
        if out and "track" in out:
            title = out["track"]["title"]
            artist = out["track"]["subtitle"]
            await msg.edit_text(f"🎵 <b>Found:</b> {title} by {artist}\n\n⚡ <b>Fetching stream link to play...</b>")
            
            # Play the song
            info = await extract_audio(f"{title} {artist}")
            if info:
                await msg.edit_text(f"🎶 <b>Matched:</b> {title} by {artist}\n\n<i>Use /play {title} to play it in VC!</i>")
            else:
                await msg.edit_text(f"🎵 <b>Matched:</b> {title} by {artist}\n<i>Could not auto-fetch stream link.</i>")
        else:
            await msg.edit_text("❌ <b>Could not recognize this audio.</b> Try a clearer snippet.")
    except Exception as e:
        LOGGER.error(f"Shazam Error: {e}")
        await msg.edit_text("❌ <b>Failed to analyze audio.</b>")
    finally:
        if os.path.exists(path): os.remove(path)
