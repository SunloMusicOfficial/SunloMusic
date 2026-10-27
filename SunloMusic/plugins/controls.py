import time
from pyrogram import filters
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream, start_next_song
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.database import is_sudo
from SunloMusic.queues import get_queue, clear_queue
from SunloMusic.texts import NOT_PLAYING_TEXT, NO_QUEUE_TEXT
from SunloMusic.keyboards import player_keyboard

@bot.on_message(filters.command("pause") & filters.group)
@catch_errors
@admin_only
async def pause_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await pause_stream(m.chat.id); q.paused = True; q.paused_at = time.time()
        await m.reply_text("⏸ <b>Paused</b>")
    else: await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_message(filters.command("resume") & filters.group)
@catch_errors
@admin_only
async def resume_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await resume_stream(m.chat.id); q.paused = False; q.total_paused += time.time() - q.paused_at
        await m.reply_text("▶️ <b>Resumed</b>")
    else: await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_message(filters.command(["skip", "next"]) & filters.group)
@catch_errors
@admin_only
async def skip_cmd(_, m):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
    await start_next_song(m.chat.id, q)

@bot.on_message(filters.command(["stop", "end"]) & filters.group)
@catch_errors
@admin_only
async def stop_cmd(_, m):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    if q.timer_task: q.timer_task.cancel(); q.timer_task = None
    if q.playing_message_id:
        try: await m.chat.delete_messages(q.playing_message_id)
        except: pass
        q.playing_message_id = 0
    for track in q.queue:
        if track.message_id:
            try: await m.chat.delete_messages(track.message_id)
            except: pass
    await stop_stream(m.chat.id)
    clear_queue(m.chat.id)
    await m.reply_text("⏹ <b>Stopped and left VC.</b>")

@bot.on_callback_query(filters.regex("^cb_del_"))
@catch_errors
async def del_queue_cb(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    user = cq.from_user
    is_admin = False
    if await is_sudo(user.id): is_admin = True
    else:
        try:
            member = await cq.message.chat.get_member(user.id)
            if member.privileges and (member.privileges.can_manage_voice_chats or member.privileges.can_manage_chat): is_admin = True
        except: pass
    if not is_admin: return await cq.answer("🚫 Sirf Admin hi ye buttons use kar sakte hain!", show_alert=True)
    track_hash = cq.data.replace("cb_del_", "")
    q = get_queue(chat_id)
    found = False
    for i, t in enumerate(q.queue):
        if str(abs(hash(t.url))) == track_hash:
            q.queue.pop(i); found = True; break
    if found:
        await cq.message.delete()
        await cq.answer("❌ Removed from queue!")
    else: await cq.answer("❌ Song already played or removed.", show_alert=True)

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
            await start_next_song(chat_id, q)
            await cq.answer("⏭ Skipped")
        elif action == "cb_stop":
            if q.timer_task: q.timer_task.cancel(); q.timer_task = None
            await stop_stream(chat_id)
            for track in q.queue:
                if track.message_id:
                    try: await bot.delete_messages(chat_id, track.message_id)
                    except: pass
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
            await cq.answer("📋 Queue: /queue\n🔄 Shuffle: /shuffle\n🔊 Volume: Coming Soon", show_alert=True)
        elif action == "cb_close":
            await cq.message.delete(); await cq.answer()
    except Exception: pass
