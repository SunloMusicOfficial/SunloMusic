import asyncio, time, base64
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.decorators import catch_errors
from SunloMusic.database import (
    add_voteplay, get_voteplay, remove_voteplay, is_sudo, add_recent
)
from SunloMusic.queues import get_queue, Track
from SunloMusic.calls import play_stream, update_live_timer
from SunloMusic.ytdlp import extract_audio
from SunloMusic.thumbnails import generate_thumbnail, get_default_thumb
from SunloMusic.keyboards import player_keyboard
from SunloMusic.formatters import format_duration
from SunloMusic.logger import LOGGER

@bot.on_message(filters.command("voteplay") & filters.group)
@catch_errors
async def voteplay_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/voteplay song name</code>")
    
    existing = await get_voteplay(m.chat.id)
    if existing:
        return await m.reply_text("❌ <b>A request is already pending!</b>\nWait for admin to approve/deny.")
    
    song = " ".join(m.command[1:])
    
    await add_voteplay(m.chat.id, {
        "song": song,
        "requester": m.from_user.first_name,
        "requester_id": m.from_user.id,
        "timestamp": time.time(),
    })
    
    await m.reply_text(
        f"📋 <b>Song Request Pending</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"🎵 {song}\n"
        f"🙋‍♂️ By: {m.from_user.mention}\n"
        f"━━━━━━━━━━━━━\n"
        f"⏳ <i>Waiting for admin approval...</i>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data="vp_approve"),
             InlineKeyboardButton("❌ Deny", callback_data="vp_deny")]
        ])
    )

@bot.on_callback_query(filters.regex("^vp_(approve|deny)$"))
@catch_errors
async def voteplay_cb(_, cq: CallbackQuery):
    is_admin = False
    if await is_sudo(cq.from_user.id):
        is_admin = True
    else:
        try:
            member = await cq.message.chat.get_member(cq.from_user.id)
            if member.privileges and (
                getattr(member.privileges, "can_manage_voice_chats", False)
                or getattr(member.privileges, "can_manage_video_chats", False)
                or member.privileges.can_manage_chat
            ):
                is_admin = True
        except: pass
    
    if not is_admin:
        return await cq.answer("🚫 Only admins can approve/deny!", show_alert=True)
    
    req = await get_voteplay(cq.message.chat.id)
    if not req:
        return await cq.answer("No pending request", show_alert=True)
    
    action = cq.data.replace("vp_", "")
    
    if action == "deny":
        await remove_voteplay(cq.message.chat.id)
        await cq.message.edit_text(
            f"❌ <b>Request Denied</b>\n\n"
            f"🎵 {req['song']}\n"
            f"🙋‍♂️ By: {req['requester']}\n"
            f"👮 Denied by: {cq.from_user.mention}"
        )
        return await cq.answer("Denied", show_alert=True)
    
    await cq.answer("✅ Approved! Loading...")
    await cq.message.edit_text(f"⏳ <b>Approved! Loading:</b> {req['song']}...")
    
    info = await extract_audio(req["song"])
    if not info:
        await remove_voteplay(cq.message.chat.id)
        return await cq.message.edit_text("❌ <b>Could not fetch song.</b>")
    
    q = get_queue(cq.message.chat.id)
    track = Track(
        info["title"], info["url"], info["duration"],
        info["thumbnail"], req["requester"], req["requester_id"], False
    )
    
    if q.now_playing:
        q.queue.append(track)
        await cq.message.edit_text(
            f"✅ <b>Approved & Queued!</b>\n\n"
            f"🎵 {info['title']}\n"
            f"📌 Position: {len(q.queue)}\n"
            f"👮 By: {cq.from_user.mention}"
        )
    else:
        await play_stream(cq.message.chat.id, track.url, track.video)
        
        q.now_playing = track
        q.start_time = time.time()
        q.total_paused = 0
        q.paused = False
        q.votes = set()
        
        try:
            await add_recent(cq.message.chat.id, {
                "title": track.title, "url": track.url,
                "duration": track.duration, "thumbnail": track.thumbnail,
                "requester": track.requester, "requester_id": track.requester_id,
                "video": track.video
            })
        except: pass
        
        thumb = await generate_thumbnail(cq.message.chat.id, track.thumbnail, track.title, format_duration(track.duration), track.requester)
        b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
        title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
        caption = f"<b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{track.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={track.requester_id}'>{track.requester}</a>\n━━━━━━━━━━━━━\n👮 Approved: {cq.from_user.mention}"
        
        sent_msg = None
        if thumb:
            try: sent_msg = await cq.message.reply_photo(thumb, caption=caption, reply_markup=player_keyboard(q, 0))
            except Exception: pass
            
        if not sent_msg:
            local_thumb = get_default_thumb()
            if local_thumb:
                try: sent_msg = await cq.message.reply_photo(local_thumb, caption=caption, reply_markup=player_keyboard(q, 0))
                except Exception: pass
                
        if not sent_msg:
            sent_msg = await cq.message.reply_text(caption, reply_markup=player_keyboard(q, 0), link_preview_options=LinkPreviewOptions(is_disabled=True))
            
        q.playing_message_id = sent_msg.id
        try: await sent_msg.pin(disable_notification=True)
        except: pass
        
        if q.timer_task: q.timer_task.cancel()
        q.timer_task = asyncio.create_task(update_live_timer(cq.message.chat.id, sent_msg.id))
        
        try: await cq.message.delete()
        except: pass
    
    await remove_voteplay(cq.message.chat.id)
