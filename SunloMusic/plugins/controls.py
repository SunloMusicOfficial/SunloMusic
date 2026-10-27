from pyrogram import filters
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream, play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.database import is_sudo
from SunloMusic.queues import get_queue, clear_queue
from SunloMusic.texts import NOT_PLAYING_TEXT, NO_QUEUE_TEXT

@bot.on_message(filters.command("pause") & filters.group)
@admin_only
async def pause_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await pause_stream(m.chat.id); q.paused = True
        await m.reply_text("⏸ <b>Paused</b>")
    else: await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_message(filters.command("resume") & filters.group)
@admin_only
async def resume_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await resume_stream(m.chat.id); q.paused = False
        await m.reply_text("▶️ <b>Resumed</b>")
    else: await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_message(filters.command(["skip", "next"]) & filters.group)
@admin_only
async def skip_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
    q.now_playing = None
    if q.queue:
        nxt = q.queue.pop(0)
        q.now_playing = nxt
        await play_stream(m.chat.id, nxt.url, nxt.video)
        await m.reply_text(f"⏭ <b>Skipped to:</b> {nxt.title}")
    else:
        await stop_stream(m.chat.id); clear_queue(m.chat.id)
        await m.reply_text("⏭ <b>Skipped. Queue is now empty.</b>")

@bot.on_message(filters.command(["stop", "end"]) & filters.group)
@admin_only
async def stop_cmd(_, m):
    await stop_stream(m.chat.id); clear_queue(m.chat.id)
    await m.reply_text("⏹ <b>Stopped and left VC.</b>")

@bot.on_callback_query(filters.regex("^cb_"))
async def controls_cb(_, cq: CallbackQuery):
    action = cq.data
    chat_id = cq.message.chat.id
    user = cq.from_user
    
    # Sirf play controls ke liye admin lock hai
    if action in ["cb_pause", "cb_resume", "cb_skip", "cb_stop", "cb_loop"]:
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
                await pause_stream(chat_id); q.paused = True
                await cq.answer("⏸ Paused")
            else: await cq.answer("Nothing playing", show_alert=True)
            
        elif action == "cb_resume":
            if q.now_playing:
                await resume_stream(chat_id); q.paused = False
                await cq.answer("▶️ Resumed")
            else: await cq.answer("Nothing playing", show_alert=True)
            
        elif action == "cb_skip":
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
            await stop_stream(chat_id); clear_queue(chat_id)
            await cq.answer("⏹ Stopped")
            await cq.message.delete()
            
        elif action == "cb_loop":
            q.loop = (q.loop + 1) % 3
            modes = {0: "Off", 1: "Track", 2: "Queue"}
            await cq.answer(f"🔁 Loop: {modes[q.loop]}")
            
        elif action == "cb_queue":
            if not q.queue: 
                await cq.answer(NO_QUEUE_TEXT, show_alert=True)
            else:
                text = "⏭ Up Next:\n" + "\n".join(f"{i+1}. {t.title}" for i, t in enumerate(q.queue[:10]))
                await cq.answer(text, show_alert=True)
                
        elif action == "cb_close":
            await cq.message.delete()
            await cq.answer()
    except Exception:
        pass
