from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.queue import get_queue, Track
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail
from SunloMusic.keyboards import controls_keyboard

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
@admin_only
async def play_cmd(_, m):
    if len(m.command) < 2 and not m.reply_to_message: 
        return await m.reply_text("❌ <b>Give a song name or link.</b>")
    
    query = " ".join(m.command[1:]) if len(m.command) > 1 else m.reply_to_message.text
    status = await m.reply_text("🔎 <b>Searching...</b>")
    info = await extract_audio(query)
    
    if not info: 
        return await status.edit_text("❌ <b>Not found.</b>")
    
    video = m.command[0] == "vplay"
    q = get_queue(m.chat.id)
    track = Track(info["title"], info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, video)
    
    if q.now_playing:
        q.queue.append(track)
        return await status.edit_text(f"➕ <b>Added to queue:</b>\n{track.title}")
    
    q.now_playing = track
    await play_stream(m.chat.id, track.url, track.video)
    
    # Thumbnail generate karega
    thumb = await generate_thumbnail(track.thumbnail, track.title, format_duration(track.duration), track.requester)
    caption = f"🎶 <b>Now Playing:</b>\n<b>{track.title}</b>\n⏱ {format_duration(track.duration)}\n👤 {track.requester}"
    
    if thumb:
        await status.delete()
        await m.reply_photo(thumb, caption=caption, reply_markup=controls_keyboard())
    else:
        await status.edit_text(caption, reply_markup=controls_keyboard())
