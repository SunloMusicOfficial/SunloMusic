import time
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.database import (
    add_voteplay, get_voteplay, remove_voteplay, is_sudo, add_recent
)
from SunloMusic.queues import get_queue, Track
from SunloMusic.calls import play_stream
from SunloMusic.ytdlp import extract_audio

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
    # Admin check
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
    
    # Approve — play the song
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
        
        await cq.message.edit_text(
            f"▶️ <b>Now Playing!</b>\n\n"
            f"🎵 {info['title']}\n"
            f"🙋‍♂️ Requested by: {req['requester']}\n"
            f"👮 Approved by: {cq.from_user.mention}"
        )
    
    await remove_voteplay(cq.message.chat.id)
