import time, random
from pyrogram import filters, enums
from pyrogram.types import CallbackQuery, Message
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream, start_next_song, play_stream, update_live_timer, call
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.database import is_sudo
from SunloMusic.queues import get_queue, clear_queue, AUTO_DJ_CHATS
from SunloMusic.texts import NOT_PLAYING_TEXT
from SunloMusic.keyboards import player_buttons, more_buttons
from SunloMusic.formatters import format_duration
from SunloMusic.logger import LOGGER
from richgram import rich_edit, rich_heading, rich_kv_table, rich_esc
import base64
from SunloMusic.config import config

@bot.on_message(filters.command(["skip", "next"]) & filters.group)
@catch_errors
@admin_only
async def skip_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
    
    if q.karaoke_task: q.karaoke_task.cancel()
    await start_next_song(m.chat.id, q)

@bot.on_message(filters.command("pause") & filters.group)
@catch_errors
@admin_only
async def pause_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
    
    if not q.paused:
        await pause_stream(m.chat.id)
        q.paused = True
        q.paused_at = time.time()
        await m.reply_text("⏸ <b>Paused!</b>")

@bot.on_message(filters.command("resume") & filters.group)
@catch_errors
@admin_only
async def resume_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
    
    if q.paused:
        await resume_stream(m.chat.id)
        q.paused = False
        q.total_paused += time.time() - q.paused_at
        await m.reply_text("▶️ <b>Resumed!</b>")

@bot.on_message(filters.command("stop") & filters.group)
@catch_errors
@admin_only
async def stop_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    q = get_queue(m.chat.id)
    
    if q.timer_task: q.timer_task.cancel()
    if q.karaoke_task: q.karaoke_task.cancel()
    
    if q.playing_message_id:
        try: await bot.delete_messages(m.chat.id, q.playing_message_id)
        except: pass
        
    await stop_stream(m.chat.id)
    clear_queue(m.chat.id)
    await m.reply_text("⏹ <b>Stopped and Assistant left VC!</b>")

@bot.on_message(filters.command("seek") & filters.group)
@catch_errors
@admin_only
async def seek_cmd(_, m: Message):
    try: await m.delete()
    except: pass
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/seek 1:30</code> or <code>/seek 90</code>")
        
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text(NOT_PLAYING_TEXT)
        
    time_str = m.command[1]
    seconds = 0
    try:
        if ":" in time_str:
            parts = list(map(int, time_str.split(':')))
            if len(parts) == 2: seconds = parts[0] * 60 + parts[1]
            elif len(parts) == 3: seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        else:
            seconds = int(time_str)
    except:
        return await m.reply_text("❌ <b>Invalid time format.</b>")
        
    if seconds >= q.now_playing.duration:
        return await m.reply_text("❌ <b>Seek time is greater than song duration!</b>")
        
    status = await m.reply_text(f"⏳ <b>Seeking to {format_duration(seconds)}...</b>")
    
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video, seek_time=seconds)
    
    q.start_time = time.time() - seconds
    q.total_paused = 0
    q.paused = False
    
    await status.delete()

def get_card_text(q, page_title="🎧🎶 Music Time 🎶🎧"):
    thumb_url = q.now_playing.thumbnail or "https://i.ibb.co/68xK6Z4/sunlo-premium.jpg"
    b64_title = base64.urlsafe_b64encode(q.now_playing.title.encode()).decode().strip("=")
    title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
    
    return (
        f'<img src="{thumb_url}" style="width: 100%; border-radius: 10px; display: block; margin-bottom: 10px;" />'
        f"<b>{page_title}</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"🎵 <a href='{title_link}'>{rich_esc(q.now_playing.title)}</a>\n"
        f"━━━━━━━━━━━━━\n"
        f"⏱ Duration: {format_duration(q.now_playing.duration)}\n"
        f"━━━━━━━━━━━━━\n"
        f"🙋‍♂️ Request: <a href='tg://user?id={q.now_playing.requester_id}'>{rich_esc(q.now_playing.requester)}</a>\n"
        f"━━━━━━━━━━━━━"
    )

@bot.on_callback_query(filters.regex("^cb_"))
@catch_errors
async def controls_cb(_, cq: CallbackQuery):
    action = cq.data
    chat_id = cq.message.chat.id
    user = cq.from_user
    
    if action not in ["cb_more", "cb_close", "cb_timer", "cb_back_player", "cb_autoplay", "cb_info_seek", "cb_info_speed", "cb_info_volume", "cb_info_eq", "cb_info_sleep", "cb_info_karaoke", "cb_info_dedicate", "cb_q_clear"] and not action.startswith("cb_more_page_"):
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
                
                await rich_edit(cq.message, get_card_text(q) + player_buttons(q, elapsed))
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
            
        elif action == "cb_autoplay":
            if chat_id in AUTO_DJ_CHATS:
                AUTO_DJ_CHATS.discard(chat_id)
                await cq.answer("🔄 Autoplay Disabled!")
            else:
                AUTO_DJ_CHATS.add(chat_id)
                await cq.answer("🔄 Autoplay Enabled!")
            
            elapsed = int(time.time() - q.start_time - q.total_paused) if q.now_playing else 0
            await rich_edit(cq.message, get_card_text(q) + player_buttons(q, elapsed))
            
        elif action == "cb_more":
            page = 1
            await rich_edit(cq.message, get_card_text(q, f"🎛 Control Panel (Page {page}/4)") + more_buttons(q, page))
            await cq.answer()

        elif action.startswith("cb_more_page_"):
            page = int(action.replace("cb_more_page_", ""))
            await rich_edit(cq.message, get_card_text(q, f"🎛 Control Panel (Page {page}/4)") + more_buttons(q, page))
            await cq.answer(f"Page {page}")

        elif action == "cb_back_player":
            elapsed = int(time.time() - q.start_time - q.total_paused) if q.now_playing else 0
            await rich_edit(cq.message, get_card_text(q) + player_buttons(q, elapsed))
            await cq.answer()

        elif action == "cb_loop":
            q.loop = (q.loop + 1) % 3
            await rich_edit(cq.message, get_card_text(q, "🎛 Control Panel (Page 2/4)") + more_buttons(q, 2))
            modes = {0: "Off", 1: "One", 2: "All"}
            await cq.answer(f"🔁 Loop: {modes[q.loop]}")

        # ✅ Audio Effects
        elif action.startswith("cb_effect_"):
            effect = action.replace("cb_effect_", "")
            if q.now_playing:
                await cq.answer(f"Applying {effect.upper()}...")
                await play_stream(chat_id, q.now_playing.url, q.now_playing.video, effect=effect)
                await rich_edit(cq.message, get_card_text(q, "🎛 Control Panel (Page 2/4)") + more_buttons(q, 2))
            else:
                await cq.answer("Nothing playing", show_alert=True)

        # ✅ Info Alerts
        elif action == "cb_info_seek":
            await cq.answer("Use: /seek 1:30 (or /seek 30 to skip forward)", show_alert=True)
        elif action == "cb_info_speed":
            await cq.answer("Use: /speed 1.5 (Values: 0.5 to 2.0)", show_alert=True)
        elif action == "cb_info_volume":
            await cq.answer("Use: /volume 150 (Values: 0 to 200)", show_alert=True)
        elif action == "cb_info_eq":
            await cq.answer("Use: /eq rock (Options: bass, pop, rock, jazz, vocal, flat)", show_alert=True)
        elif action == "cb_info_sleep":
            await cq.answer("Use: /sleep 10m (Bot leaves VC after time)", show_alert=True)
        elif action == "cb_info_karaoke":
            await cq.answer("Use: /karaoke on/off", show_alert=True)
        elif action == "cb_info_dedicate":
            await cq.answer("Use: /dedicate @user song_name", show_alert=True)

        elif action == "cb_q_show":
            if not q.now_playing and not q.queue:
                return await cq.answer("Queue is empty.", show_alert=True)
            text = f"▶️ Playing: {q.now_playing.title[:30] if q.now_playing else 'None'}\n"
            text += f"⏭ Up Next: {len(q.queue)} songs"
            await cq.answer(text, show_alert=True)

        elif action == "cb_q_shuffle":
            if not q.queue:
                return await cq.answer("Queue is empty.", show_alert=True)
            random.shuffle(q.queue)
            await cq.answer("🔀 Queue Shuffled!", show_alert=True)

        elif action == "cb_q_export":
            if not q.now_playing and not q.queue:
                return await cq.answer("Queue is empty.", show_alert=True)
            await cq.answer("Please use /export in chat to get the file.", show_alert=True)

        elif action == "cb_q_clear":
            if q.queue:
                q.queue.clear()
                await cq.answer("🗑 Queue Cleared!", show_alert=True)
            else:
                await cq.answer("Queue is already empty.", show_alert=True)

        elif action == "cb_close":
            await cq.message.delete(); await cq.answer()
    except Exception as e:
        LOGGER.error(f"Callback Error: {e}")
        await cq.answer("An error occurred", show_alert=True)
