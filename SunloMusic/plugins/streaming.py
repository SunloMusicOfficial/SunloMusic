import asyncio, time, random
from pyrogram import filters, enums
from pyrogram.types import Message, LinkPreviewOptions
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.config import config
from SunloMusic.ytdlp import extract_audio
from SunloMusic.calls import play_stream
from SunloMusic.queues import get_queue, Track
from SunloMusic.database import add_user, SPAM_DICT, add_lb_point, add_recent, is_sudo, get_group_setting
from SunloMusic.logger import LOGGER

LOADING_EMOJIS = ["✨", "🌸", "🪄", "🌟", "🦋", "🎧", "🎶", "🍃", "🔥", "💫", "🪐", "🌈"]

async def _check_admin(m):
    if m.from_user.id == config.OWNER_ID or m.from_user.id in config.sudo_list: return True
    try:
        if await is_sudo(m.from_user.id): return True
        member = await m.chat.get_member(m.from_user.id)
        if member.privileges and (getattr(member.privileges, "can_manage_video_chats", False) or getattr(member.privileges, "can_manage_voice_chats", False) or member.privileges.can_manage_chat):
            return True
    except: pass
    return False

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
@catch_errors
async def play_cmd(_, m: Message):
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
            if count >= 5: return await m.reply_text("⚠️ <b>Spam Detected!</b>")
            SPAM_DICT[uid] = (count + 1, now)
        else: SPAM_DICT[uid] = (1, now)
    else: SPAM_DICT[uid] = (1, now)

    query = " ".join(m.command[1:]) if len(m.command) > 1 else (m.reply_to_message.text or m.reply_to_message.caption if m.reply_to_message else None)
    if not query: return await m.reply_text("❌ <b>Give a song name or link.</b>")
    try: await m.delete()
    except: pass

    # ✅ Streaming Start
    status = await m.reply_text(f"{random.choice(LOADING_EMOJIS)} <b>Searching YouTube...</b>")
    video = "vplay" in m.command[0].lower()
    
    admin_task = _check_admin(m)
    assist_task = __import__('SunloMusic.bot', fromlist=['ensure_assistant_in_chat']).ensure_assistant_in_chat(m.chat.id)
    db_task = asyncio.gather(add_user(uid, m.from_user.first_name), add_lb_point(m.chat.id, uid, m.from_user.first_name))
    audio_task = extract_audio(query, video=video)
    
    is_admin, assist_ok, _, info = await asyncio.gather(admin_task, assist_task, db_task, audio_task)
    
    if not is_admin: return await status.edit_text("🚫 <b>Only admins can use this.</b>")
    if not assist_ok: return await status.edit_text("❌ <b>Assistant could not join!</b>")
    if not info: return await status.edit_text("❌ <b>Failed to fetch media.</b>")

    # Streaming Update 2
    await status.edit_text(f"⬇️ <b>Downloading Audio...</b>\n<pre>{info['title'][:50]}</pre>")
    
    raw_title = info["title"]
    safe_title = raw_title[:40] + "..." if len(raw_title) > 40 else raw_title
    q = get_queue(m.chat.id)
    
    is_duplicate = False
    if q.now_playing and (q.now_playing.url == info["url"] or q.now_playing.title == safe_title):
        is_duplicate = True
    for t in q.queue:
        if t.url == info["url"] or t.title == safe_title:
            is_duplicate = True
            break
    if is_duplicate:
        return await status.edit_text("⚠️ <b>Already in queue!</b>")
    
    track = Track(safe_title, info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, video)
    
    if q.now_playing:
        q.queue.append(track)
        await status.edit_text(f"📥 <b>Added to Queue:</b> {track.title}")
        return
    
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    q.votes = set()
    
    # Streaming Update 3
    await status.edit_text(f"⚡ <b>Connecting to VC...</b>\n<pre>{track.title[:50]}</pre>")
    
    from SunloMusic.plugins.voice import speak_in_vc
    async def play_with_tts():
        if await get_group_setting(m.chat.id, "tts", False):
            await speak_in_vc(m.chat.id, f"Ab play ho raha hai, {track.title}")
        await play_stream(m.chat.id, track.url, track.video)
    
    play_task = asyncio.create_task(play_with_tts())
    
    # Final Rich Message
    from richgram import rich_send, rich_esc
    from SunloMusic.keyboards import player_buttons
    thumb_url = track.thumbnail or "https://i.ibb.co/68xK6Z4/sunlo-premium.jpg"
    card_text = (
        f'<img src="{thumb_url}" style="width: 100%; border-radius: 10px; display: block; margin-bottom: 10px;" />'
        f"<b>🎧🎶 Music Time 🎶🎧</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"🎵 {rich_esc(track.title)}\n"
        f"━━━━━━━━━━━━━\n"
        f"⏱ Duration: {__import__('SunloMusic.formatters', fromlist=['format_duration']).format_duration(track.duration)}\n"
        f"━━━━━━━━━━━━━\n"
        f"🙋‍♂️ Request: {rich_esc(track.requester)}\n"
        f"━━━━━━━━━━━━━"
    )
    
    sent_msg = await rich_send(bot, m.chat.id, card_text + player_buttons(q, 0))
    q.playing_message_id = sent_msg.id
    try: await sent_msg.pin(disable_notification=True)
    except: pass
    
    await status.delete()
    await play_task
    
    from SunloMusic.calls import update_live_timer
    if q.timer_task: q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(m.chat.id, sent_msg.id))
