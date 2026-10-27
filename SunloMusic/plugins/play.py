import asyncio
import time
import base64
from pyrogram import filters, enums
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.calls import play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.database import add_user
from SunloMusic.queues import get_queue, Track
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail
from SunloMusic.keyboards import player_keyboard

def make_progress_bar(current: int, total: int, length: int = 10) -> str:
    if not total: return "─" * length
    pos = int(length * current / total)
    pos = min(max(pos, 0), length - 1)
    return "─" * pos + "🎵" + "─" * (length - pos - 1)

async def update_live_timer(chat_id, msg_id):
    while True:
        await asyncio.sleep(5)
        q = get_queue(chat_id)
        if not q.now_playing or q.playing_message_id != msg_id:
            break
        if q.paused:
            continue
            
        elapsed = int(time.time() - q.start_time - q.total_paused)
        if elapsed >= q.now_playing.duration and q.now_playing.duration > 0:
            break
            
        try:
            dur_str = format_duration(q.now_playing.duration)
            elapsed_str = format_duration(elapsed)
            progress = make_progress_bar(elapsed, q.now_playing.duration)
            
            b64_title = base64.urlsafe_b64encode(q.now_playing.title.encode()).decode().strip("=")
            title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
            
            caption = (
                f"<b>🎧🎶 Music Time 🎶🎧</b>\n\n"
                f"🎵 <a href='{title_link}'>{q.now_playing.title}</a>\n"
                f"⏱ <b>Duration:</b> {dur_str}\n"
                f"👤 <b>Request:</b> <a href='tg://user?id={q.now_playing.requester_id}'>{q.now_playing.requester}</a>\n\n"
                f"<code>{elapsed_str}</code> 🎵 {progress} <code>{dur_str}</code>"
            )
            
            try:
                await bot.edit_message_caption(
                    chat_id=chat_id, message_id=msg_id,
                    caption=caption, reply_markup=player_keyboard(q)
                )
            except Exception:
                await bot.edit_message_text(
                    chat_id=chat_id, message_id=msg_id,
                    text=caption, reply_markup=player_keyboard(q)
                )
        except Exception:
            pass

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
@admin_only
async def play_cmd(_, m):
    if m.chat.type != enums.ChatType.SUPERGROUP:
        return await m.reply_text("❌ <b>Voice Chat sirf Supergroup me kaam karta hai.</b>")

    await add_user(m.from_user.id, m.from_user.first_name)
    query = " ".join(m.command[1:]) if len(m.command) > 1 else (m.reply_to_message.text or m.reply_to_message.caption if m.reply_to_message else None)
    if not query: return await m.reply_text("❌ <b>Give a song name or link.</b>")
    
    status = await m.reply_text("🔎 <b>Fetching...</b>")
    info = await extract_audio(query)
    
    if not info:
        return await status.edit_text("❌ <b>Failed to fetch stream link.</b>")
    
    video = "vplay" in m.command[0].lower()
    q = get_queue(m.chat.id)
    track = Track(info["title"], info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, video)
    
    if q.now_playing:
        q.queue.append(track)
        return await status.edit_text(f"➕ <b>Added to queue:</b>\n{track.title}")
    
    await status.edit_text("⏳ <b>Joining Voice Chat...</b>")
    success = await play_stream(m.chat.id, track.url, track.video)
    
    if not success:
        return await status.edit_text("❌ <b>Failed to join VC.</b>\nCheck Render logs.")
        
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    
    b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
    title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
    
    thumb = await generate_thumbnail(track.thumbnail, track.title, format_duration(track.duration), track.requester)
    
    dur_str = format_duration(track.duration)
    progress = make_progress_bar(0, track.duration)
    
    caption = (
        f"<b>🎧🎶 Music Time 🎶🎧</b>\n\n"
        f"🎵 <a href='{title_link}'>{track.title}</a>\n"
        f"⏱ <b>Duration:</b> {dur_str}\n"
        f"👤 <b>Request:</b> <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n\n"
        f"<code>00:00</code> 🎵 {progress} <code>{dur_str}</code>"
    )
    
    if thumb:
        await status.delete()
        sent_msg = await m.reply_photo(thumb, caption=caption, reply_markup=player_keyboard(q))
    else:
        sent_msg = await status.edit_text(caption, reply_markup=player_keyboard(q))
        
    q.playing_message_id = sent_msg.id
    
    if q.timer_task:
        q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(m.chat.id, sent_msg.id))
