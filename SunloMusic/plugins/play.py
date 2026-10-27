import asyncio, time, base64
from pyrogram import filters, enums
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.calls import play_stream, update_live_timer
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.database import add_user
from SunloMusic.queues import get_queue, Track
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail
from SunloMusic.keyboards import player_keyboard, queue_add_keyboard

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
@catch_errors
@admin_only
async def play_cmd(_, m):
    if m.reply_to_message and m.reply_to_message.from_user and m.reply_to_message.from_user.is_bot:
        if m.reply_to_message.from_user.id != bot.me.id: return
    if m.text and m.text.startswith("/") and "@" in m.text.split()[0]:
        if bot.me.username not in m.text.split()[0]: return

    if m.chat.type != enums.ChatType.SUPERGROUP:
        return await m.reply_text("❌ <b>Voice Chat sirf Supergroup me kaam karta hai.</b>")

    await add_user(m.from_user.id, m.from_user.first_name)
    query = " ".join(m.command[1:]) if len(m.command) > 1 else (m.reply_to_message.text or m.reply_to_message.caption if m.reply_to_message else None)
    if not query: return await m.reply_text("❌ <b>Give a song name or link.</b>")
    try: await m.delete()
    except: pass

    status = await m.reply_text("🔎 <b>Fetching...</b>")
    info = await extract_audio(query)
    if not info: return await status.edit_text("❌ <b>Failed to fetch stream link.</b>")
    
    raw_title = info["title"]
    safe_title = raw_title[:40] + "..." if len(raw_title) > 40 else raw_title
    
    video = "vplay" in m.command[0].lower()
    q = get_queue(m.chat.id)
    track = Track(safe_title, info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, video)
    
    # ✅ Queue UI
    if q.now_playing:
        q.queue.append(track)
        track_hash = str(abs(hash(track.url)))
        thumb = await generate_thumbnail(track.thumbnail, track.title, format_duration(track.duration), track.requester)
        b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
        title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
        
        caption = (
            f"<b>📥 Added to Queue 📥</b>\n"
            f"━━━━━━━━━━━━━\n"
            f"🎵 <a href='{title_link}'>{track.title}</a>\n"
            f"━━━━━━━━━━━━━\n"
            f"⏱ Duration: {format_duration(track.duration)}\n"
            f"━━━━━━━━━━━━━\n"
            f"🙋‍♂️ Request: <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n"
            f"━━━━━━━━━━━━━\n"
            f"📌 Position: {len(q.queue)}\n"
            f"━━━━━━━━━━━━━"
        )
        
        if thumb: sent_msg = await m.reply_photo(thumb, caption=caption, reply_markup=queue_add_keyboard(track_hash))
        else: sent_msg = await status.edit_text(caption, reply_markup=queue_add_keyboard(track_hash))
        track.message_id = sent_msg.id
        return
    
    await status.edit_text("⏳ <b>Joining Voice Chat...</b>")
    success = await play_stream(m.chat.id, track.url, track.video)
    if not success: return await status.edit_text("❌ <b>Failed to join VC.</b>\nCheck Render logs.")
        
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    
    b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
    title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
    thumb = await generate_thumbnail(track.thumbnail, track.title, format_duration(track.duration), track.requester)
    
    # ✅ Initial Play UI
    caption = (
        f"<b>🎧🎶 Music Time 🎶🎧</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"🎵 <a href='{title_link}'>{track.title}</a>\n"
        f"━━━━━━━━━━━━━\n"
        f"⏱ Duration: {format_duration(track.duration)}\n"
        f"━━━━━━━━━━━━━\n"
        f"🙋‍♂️ Request: <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n"
        f"━━━━━━━━━━━━━"
    )
    
    if thumb:
        await status.delete()
        sent_msg = await m.reply_photo(thumb, caption=caption, reply_markup=player_keyboard(q, 0))
    else:
        sent_msg = await status.edit_text(caption, reply_markup=player_keyboard(q, 0))
        
    q.playing_message_id = sent_msg.id
    if q.timer_task: q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(m.chat.id, sent_msg.id))
