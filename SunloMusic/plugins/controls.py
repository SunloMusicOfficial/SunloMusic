import time
from pyrogram import filters
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream, play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.database import is_sudo
from SunloMusic.queues import get_queue, clear_queue
from SunloMusic.texts import NOT_PLAYING_TEXT, NO_QUEUE_TEXT
from SunloMusic.keyboards import player_keyboard

@bot.on_message(filters.command("pause") & filters.group)
@admin_only
async def pause_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await pause_stream(m.chat.id); q.paused = True; q.paused_at = time.time()
        await m.reply_text("⏸ <b>Paused</b>")
    else: await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_message(filters.command("resume") & filters.group)
@admin_only
async def resume_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await resume_stream(m.chat.id); q.paused = False; q.total_paused += time.time() - q.paused_at
        await m.reply_text("▶️ <b>Resumed</b>")
    else: await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_callback_query(filters.regex("^cb_"))
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
        if not is_admin:
            return await cq.answer("🚫 Sirf Admin hi ye buttons use kar sakte hain!", show_alert=True)

    try:
        q = get_queue(chat_id)
        
        if action == "cb_pause":
            if q.now_playing:
                if q.paused:
                    # Resume
                    await resume_stream(chat_id)
                    q.paused = False
                    q.total_paused += time.time() - q.paused_at
                    await cq.answer("▶️ Resumed")
                else:
                    # Pause
                    await pause_stream(chat_id)
                    q.paused = True
                    q.paused_at = time.time()
                    await cq.answer("⏸ Paused")
                
                # Instantly update button text
                elapsed = int(time.time() - q.start_time - q.total_paused)
                try:
                    await cq.message.edit_reply_markup(reply_markup=player_keyboard(q, elapsed))
                except: pass
            else:
                await cq.answer("Nothing playing", show_alert=True)
                
        elif action == "cb_skip":
            if q.timer_task: q.timer_task.cancel()
            if q.now_playing:
                q.now_playing = None
                if q.queue:
                    nxt = q.queue.pop(0); q.now_playing = nxt
                    await play_stream(chat_id, nxt.url, nxt.video)
                    await cq.answer(f"⏭ Skipped to {nxt.title}")
                else:
                    await stop_stream(chat_id); clear_queue(chat_id)
                    await cq.answer("⏭ Queue ended")
                    await cq.message.delete()
            else: await cq.answer("Nothing playing", show_alert=True)
            
        elif action == "cb_stop":
            if q.timer_task: q.timer_task.cancel()
            await stop_stream(chat_id); clear_queue(chat_id)
            await cq.answer("⏹ Stopped")
            await cq.message.delete()
            
        elif action == "cb_loop":
            q.loop = (q.loop + 1) % 3
            elapsed = int(time.time() - q.start_time - q.total_paused) if q.now_playing else 0
            await cq.message.edit_reply_markup(reply_markup=player_keyboard(q, elapsed))
            modes = {0: "Off", 1: "One", 2: "All"}
            await cq.answer(f"🔁 Loop: {modes[q.loop]}")
            
        elif action == "cb_more":
            text = (
                f"<b>🎛 More Controls</b>\n\n"
                f"📋 <b>Queue:</b> /queue\n"
                f"🔄 <b>Shuffle:</b> /shuffle\n"
                f"🔊 <b>Volume:</b> Coming Soon"
            )
            await cq.answer(text, show_alert=True)
            
        elif action == "cb_timer":
            await cq.answer("⏱ Timer is running live!")
            
        elif action == "cb_close":
            await cq.message.delete()
            await cq.answer()
    except Exception:
        pass
