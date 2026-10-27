from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.queue import get_queue, Track
from SunloMusic.ytdlp import extract_audio

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
@admin_only
async def play_cmd(_, m):
    if len(m.command) < 2 and not m.reply_to_message: return await m.reply_text("❌ Give a song name.")
    query = " ".join(m.command[1:]) if len(m.command) > 1 else m.reply_to_message.text
    status = await m.reply_text("🔎 Searching...")
    info = await extract_audio(query)
    if not info: return await status.edit_text("❌ Not found.")
    
    q = get_queue(m.chat.id)
    track = Track(info["title"], info["url"], info["duration"], info["thumbnail"], m.from_user.first_name)
    
    if q.now_playing:
        q.queue.append(track)
        return await status.edit_text(f"➕ Added to queue: {track.title}")
    
    q.now_playing = track
    await play_stream(m.chat.id, track.url)
    await status.edit_text(f"🎶 <b>Now Playing:</b>\n{track.title}")
