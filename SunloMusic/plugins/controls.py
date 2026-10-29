import time
from pyrogram import filters, enums
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream, start_next_song
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.database import is_sudo
from SunloMusic.queues import get_queue, clear_queue
from SunloMusic.texts import NOT_PLAYING_TEXT
from SunloMusic.keyboards import player_keyboard

@bot.on_message(filters.command(["skip", "next"]) & filters.group)
@catch_errors
async def skip_cmd(_, m):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
    
    user = m.from_user
    is_admin = False
    if await is_sudo(user.id): is_admin = True
    else:
        try:
            member = await m.chat.get_member(user.id)
            if member.privileges and (member.privileges.can_manage_voice_chats or member.privileges.can_manage_chat): is_admin = True
        except: pass
        
    if is_admin:
        if q.karaoke_task: q.karaoke_task.cancel()
        return await start_next_song(m.chat.id, q)
        
    if user.id in q.votes: return await m.reply_text("🗳️ You have already voted to skip!")
    q.votes.add(user.id)
    
    try:
        participants = await m.chat.get_members(filter=enums.ChatMembersFilter.VOICE_CHAT)
        total_listeners = len(participants) - 2
    except: total_listeners = 5
        
    votes_needed = max(1, int(total_listeners / 2))
    if len(q.votes) >= votes_needed:
        await m.reply_text(f"🗳️ <b>Vote Skip Passed!</b> Skipping...")
        if q.karaoke_task: q.karaoke_task.cancel()
        await start_next_song(m.chat.id, q)
    else:
        await m.reply_text(f"🗳️ <b>Vote Added!</b> Needed: {votes_needed - len(q.votes)} more.")

@bot.on_callback_query(filters.regex("^cb_"))
@catch_errors
async def controls_cb(_, cq: CallbackQuery):
    action = cq.data
    chat_id = cq.message.chat.id
    user = cq.from_user
    
    if action not in ["cb_more", "cb_close", "cb_timer"]:
        is_admin = False
        if await is_sudo(user.id): is_admin = True
        else:
            try:
                member = await cq.message.chat.get_member(user.id)
                if member.privileges and (member.privileges.can_manage_voice_chats or member.privileges.can_manage_chat): is_admin = True
            except: pass
        if not is_admin: return await cq.answer("🚫 Sirf Admin hi ye buttons use kar sakte hain!", show_alert=True)

    try:
        q = get_queue(chat_id)
        
        if action == "cb_pause":
            if q.now_playing:
                elapsed = int(time.time() - q.start_time - q.total_paused)
                if q.paused:
                    await resume_stream(chat_id); q.paused = False; q.total_paused += time.time() - q.paused_at
                    await cq.answer("▶️ Resumed")
                else:
                    await pause_stream(chat_id); q.paused = True; q.paused_at = time.time()
                    await cq.answer("⏸ Paused")
                try: await cq.message.edit_reply_markup(reply_markup=player_keyboard(q, elapsed))
                except: pass
            else: await cq.answer("Nothing playing", show_alert=True)
                
        elif action == "cb_skip":
            if q.karaoke_task: q.karaoke_task.cancel()
            await start_next_song(chat_id, q)
            await cq.answer("⏭ Skipped")
            
        elif action == "cb_stop":
            if q.timer_task: q.timer_task.cancel()
            if q.karaoke_task: q.karaoke_task.cancel()
            await stop_stream(chat_id)
            clear_queue(chat_id)
            await cq.answer("⏹ Stopped")
            try: await cq.message.delete()
            except: pass
            
        elif action == "cb_loop":
            q.loop = (q.loop + 1) % 3
            elapsed = int(time.time() - q.start_time - q.total_paused) if q.now_playing else 0
            try: await cq.message.edit_reply_markup(reply_markup=player_keyboard(q, elapsed))
            except: pass
            modes = {0: "Off", 1: "One", 2: "All"}
            await cq.answer(f"🔁 Loop: {modes[q.loop]}")
            
        elif action == "cb_more":
            await cq.answer("📋 Queue: /queue\n🔄 Shuffle: /shuffle", show_alert=True)
        elif action == "cb_close":
            await cq.message.delete(); await cq.answer()
    except Exception: pass
