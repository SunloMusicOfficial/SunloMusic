import asyncio, time, base64
from pyrogram import filters, enums
from pyrogram.types import LinkPreviewOptions
from SunloMusic.bot import bot, ensure_assistant_in_chat
from SunloMusic.config import config
from SunloMusic.calls import play_stream, update_live_timer
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.database import add_user, SPAM_DICT, add_lb_point
from SunloMusic.queues import get_queue, Track, KARAOKE_CHATS
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail
from SunloMusic.keyboards import player_keyboard, queue_add_keyboard
from SunloMusic.lyrics import start_live_karaoke

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

    uid = m.from_user.id
    now = time.time()
    if uid in SPAM_DICT:
        count, last_time = SPAM_DICT[uid]
        if now - last_time < 60:
            if count >= 5: return await m.reply_text("⚠️ <b>Spam Detected! Please wait.</b>")
            SPAM_DICT[uid] = (count + 1, now)
        else: SPAM_DICT[uid] = (1, now)
    else: SPAM_DICT[uid] = (1, now)

    await add_user(uid, m.from_user.first_name)
    await add_lb_point(m.chat.id, uid, m.from_user.first_name) # ✅ Leaderboard point
    
    query = " ".join(m.command[1:]) if len(m.command) > 1 else (m.reply_to_message.text or m.reply_to_message.caption if m.reply_to_message else None)
    if not query: return await m.reply_text("❌ <b>Give a song name or link.</b>")
    try: await m.delete()
    except: pass

    status = await m.reply_text("🔎 <b>Checking Assistant...</b>")
    if not await ensure_assistant_in_chat(m.chat.id):
        return await status.edit_text("❌ <b>Assistant could not join the group!</b>")
        
    video = "vplay" in m.command[0].lower()
    await status.edit_text("🎬 <b>Downloading Video...</b>" if video else "⏳ <b>Wait a sec, getting the beats...</b>")
        
    info = await extract_audio(query, video=video)
    if not info: return await status.edit_text("❌ <b>Failed to fetch media.</b>")
    
    raw_title = info["title"]
    safe_title = raw_title[:40] + "..." if len(raw_title) > 40 else raw_title
    
    q = get_queue(m.chat.id)
    track = Track(safe_title, info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, video)
    
    if q.now_playing:
        q.queue.append(track)
        track_hash = str(abs(hash(track.url)))
        thumb = await generate_thumbnail(m.chat.id, track.thumbnail, track.title, format_duration(track.duration), track.requester)
        b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
        title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
        caption = f"<b>📥 Added to Queue 📥</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{track.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n━━━━━━━━━━━━━\n📌 Position: {len(q.queue)}\n━━━━━━━━━━━━━"
        
        if thumb: sent_msg = await m.reply_photo(thumb, caption=caption, reply_markup=queue_add_keyboard(track_hash))
        else: sent_msg = await bot.send_message(m.chat.id, caption, reply_markup=queue_add_keyboard(track_hash), link_preview_options=LinkPreviewOptions(is_disabled=True))
        track.message_id = sent_msg.id
        return
    
    await status.edit_text("⚡ <b>Joining VC at light speed...</b>")
    await play_stream(m.chat.id, track.url, track.video)
        
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    q.votes = set()
    
    b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
    title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
    thumb = await generate_thumbnail(m.chat.id, track.thumbnail, track.title, format_duration(track.duration), track.requester)
    
    caption = f"<b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{track.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n━━━━━━━━━━━━━"
    
    if thumb:
        await status.delete()
        sent_msg = await m.reply_photo(thumb, caption=caption, reply_markup=player_keyboard(q, 0))
    else:
        await status.delete()
        sent_msg = await bot.send_message(m.chat.id, caption, reply_markup=player_keyboard(q, 0), link_preview_options=LinkPreviewOptions(is_disabled=True))
        
    q.playing_message_id = sent_msg.id
    
    # ✅ AUTO-PIN THE MESSAGE
    try: 
        await sent_msg.pin(disable_notification=True)
    except: pass
    
    if q.timer_task: q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(m.chat.id, sent_msg.id))

    if m.chat.id in KARAOKE_CHATS:
        q.karaoke_task = asyncio.create_task(start_live_karaoke(bot, m.chat.id, track.title, track.duration, q))
