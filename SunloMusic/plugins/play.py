from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.database import add_user
from SunloMusic.queues import get_queue, Track
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail
from SunloMusic.keyboards import controls_keyboard

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
@admin_only
async def play_cmd(_, m):
    await add_user(m.from_user.id, m.from_user.first_name)
    
    query = None
    if len(m.command) > 1: query = " ".join(m.command[1:])
    elif m.reply_to_message: query = m.reply_to_message.text or m.reply_to_message.caption
        
    if not query: return await m.reply_text("❌ <b>Give a song name, link, or reply to a text.</b>")
    
    status = await m.reply_text("🔎 <b>Searching...</b>")
    info = await extract_audio(query)
    if not info: return await status.edit_text("❌ <b>Not found or invalid link.</b>")
    
    video = "vplay" in m.command[0].lower()
    q = get_queue(m.chat.id)
    track = Track(info["title"], info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, video)
    
    if q.now_playing:
        q.queue.append(track)
        return await status.edit_text(f"➕ <b>Added to queue:</b>\n{track.title}")
    
    success = await play_stream(m.chat.id, track.url, track.video)
    if not success:
        return await status.edit_text("❌ <b>Failed to join VC. Make sure Voice Chat is active and Assistant is in group.</b>")
        
    q.now_playing = track
    thumb = await generate_thumbnail(track.thumbnail, track.title, format_duration(track.duration), track.requester)
    caption = f"🎶 <b>Now Playing:</b>\n<b>{track.title}</b>\n⏱ {format_duration(track.duration)}\n👤 {track.requester}"
    
    if thumb:
        await status.delete()
        await m.reply_photo(thumb, caption=caption, reply_markup=controls_keyboard())
    else:
        await status.edit_text(caption, reply_markup=controls_keyboard())
