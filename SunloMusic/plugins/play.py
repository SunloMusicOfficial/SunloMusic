import asyncio, time, base64, random
from pyrogram import filters, enums
from pyrogram.types import LinkPreviewOptions
from SunloMusic.bot import bot, ensure_assistant_in_chat
from SunloMusic.config import config
from SunloMusic.calls import play_stream, update_live_timer
from SunloMusic.decorators import catch_errors
from SunloMusic.database import add_user, SPAM_DICT, add_lb_point, add_recent, is_sudo, get_group_setting
from SunloMusic.queues import get_queue, Track, KARAOKE_CHATS
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail, get_default_thumb
from SunloMusic.keyboards import player_buttons, queue_add_keyboard
from SunloMusic.logger import LOGGER
from richgram import rich_send, rich_esc

async def _check_admin(m):
    if not m.from_user: return False
    if m.from_user.id == config.OWNER_ID or m.from_user.id in config.sudo_list: return True
    try:
        if await is_sudo(m.from_user.id): return True
        member = await m.chat.get_member(m.from_user.id)
        if member.privileges and (getattr(member.privileges, "can_manage_video_chats", False) or member.privileges.can_manage_chat): return True
    except: pass
    return False

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
@catch_errors
async def play_cmd(_, m):
    if not m.from_user: return await m.reply_text("❌ Anonymous admins cannot use this.")
    if m.reply_to_message and m.reply_to_message.from_user and m.reply_to_message.from_user.is_bot:
        if m.reply_to_message.from_user.id != bot.me.id: return
    if m.text and m.text.startswith("/") and "@" in m.text.split()[0]:
        if bot.me.username not in m.text.split()[0]: return
    if m.chat.type != enums.ChatType.SUPERGROUP: return await m.reply_text("❌ Voice Chat sirf Supergroup me kaam karta hai.")

    uid = m.from_user.id
    now = time.time()
    if uid in SPAM_DICT:
        count, last_time = SPAM_DICT[uid]
        if now - last_time < 60:
            if count >= 5: return await m.reply_text("⚠️ Spam Detected! Please wait.")
            SPAM_DICT[uid] = (count + 1, now)
        else: SPAM_DICT[uid] = (1, now)
    else: SPAM_DICT[uid] = (1, now)

    query = " ".join(m.command[1:]) if len(m.command) > 1 else (m.reply_to_message.text or m.reply_to_message.caption if m.reply_to_message else None)
    if not query: return await m.reply_text("❌ Give a song name or link.")
    try: await m.delete()
    except: pass

    status = await m.reply_text("<blockquote>🎵 <b>SUNLO ENGINE</b>\n🔍 Searching: <code>{}</code>\n⚡ Status: Initializing...</blockquote>".format(query[:30]))
    asyncio.create_task(bot.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_AUDIO))
    
    video = "vplay" in m.command[0].lower()
    
    admin_task = _check_admin(m)
    assist_task = ensure_assistant_in_chat(m.chat.id)
    db_task = asyncio.gather(add_user(uid, m.from_user.first_name), add_lb_point(m.chat.id, uid, m.from_user.first_name))
    audio_task = extract_audio(query, video=video)
    
    is_admin, assist_ok, _, info = await asyncio.gather(admin_task, assist_task, db_task, audio_task)
    
    if not is_admin: return await status.edit_text("🚫 Only admins can use this.")
    if not assist_ok: return await status.edit_text("❌ Assistant could not join!")
    if not info: return await status.edit_text("❌ Failed to fetch media.")

    await status.edit_text("<blockquote>🎵 <b>SUNLO ENGINE</b>\n🎶 Found: <code>{}</code>\n⚡ Status: Connecting to VC...</blockquote>".format(info['title'][:30]))

    raw_title = info["title"]
    safe_title = raw_title[:40] + "..." if len(raw_title) > 40 else raw_title
    q = get_queue(m.chat.id)
    
    is_duplicate = False
    if q.now_playing and (q.now_playing.url == info["url"] or q.now_playing.title == safe_title): is_duplicate = True
    for t in q.queue:
        if t.url == info["url"] or t.title == safe_title:
            is_duplicate = True
            break
    if is_duplicate: return await status.edit_text("⚠️ Song already in queue!")
    
    track = Track(safe_title, info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, video, video_id=info.get("video_id", ""))
    
    if q.now_playing:
        q.queue.append(track)
        await status.delete()
        thumb = await generate_thumbnail(m.chat.id, track.thumbnail, track.title, format_duration(track.duration), track.requester)
        b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
        caption = f"<b>📥 Added to Queue</b>\n━━━━━━━━━━━━━\n🎵 <a href='https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}'>{track.title}</a>\n⏱ {format_duration(track.duration)}\n🙋‍♂️ {track.requester}\n📌 Position: {len(q.queue)}"
        sent_msg = await m.reply_photo(thumb, caption=caption, reply_markup=queue_add_keyboard(str(abs(hash(track.url))))) if thumb else await m.reply_text(caption)
        track.message_id = sent_msg.id
        return
    
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    q.votes = set()
    await status.delete()
    
    thumb_url = track.thumbnail or "https://i.ibb.co/68xK6Z4/sunlo-premium.jpg"
    b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
    card_text = f'<img src="{thumb_url}" style="width: 100%; border-radius: 10px; display: block; margin-bottom: 10px;" /><b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href="https://t.me/{config.BOT_USERNAME.strip("@")}?start=dl_{b64_title}">{rich_esc(track.title)}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n🙋‍♂️ Request: <a href="tg://user?id={track.requester_id}">{rich_esc(track.requester)}</a>'
    
    from SunloMusic.plugins.voice import speak_in_vc
    async def play_with_tts():
        if await get_group_setting(m.chat.id, "tts", False):
            await speak_in_vc(m.chat.id, f"Ab play ho raha hai, {track.title}")
        await play_stream(m.chat.id, track.url, track.video, duration=track.duration)
        
    sent_msg, _ = await asyncio.gather(rich_send(bot, m.chat.id, card_text + player_buttons(q, 0)), play_with_tts())
    
    q.playing_message_id = sent_msg.id
    try: await sent_msg.pin(disable_notification=True)
    except: pass
    if q.timer_task: q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(m.chat.id, sent_msg.id))
    if m.chat.id in KARAOKE_CHATS: q.karaoke_task = asyncio.create_task(start_live_karaoke(bot, m.chat.id, track.title, track.duration, q))

    asyncio.create_task(add_recent(m.chat.id, {"title": track.title, "url": track.url, "duration": track.duration, "thumbnail": track.thumbnail, "requester": track.requester, "requester_id": track.requester_id, "video": track.video}))
