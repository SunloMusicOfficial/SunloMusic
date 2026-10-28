import random
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.formatters import format_duration
from SunloMusic.queues import get_queue

@bot.on_message(filters.command("queue") & filters.group)
@catch_errors
async def queue_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.now_playing and not q.queue: return await m.reply_text("📭 <b>Queue is empty.</b>")
    text = "<b>📋 Current Queue</b>\n\n"
    if q.now_playing: text += f"<b>▶️ Now Playing:</b>\n🎵 {q.now_playing.title}\n⏱ {format_duration(q.now_playing.duration)}\n\n"
    if q.queue:
        text += "<b>⏭ Up Next:</b>\n"
        for i, t in enumerate(q.queue[:10], 1): text += f"{i}. {t.title} ({format_duration(t.duration)})\n"
    await m.reply_text(text)

@bot.on_message(filters.command("clear") & filters.group)
@catch_errors
@admin_only
async def clear_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.queue: return await m.reply_text("📭 <b>Queue is already empty.</b>")
    
    # Delete queue messages
    for t in q.queue:
        if t.message_id:
            try: await bot.delete_messages(m.chat.id, t.message_id)
            except: pass
            
    q.queue.clear()
    await m.reply_text("🗑 <b>Queue Cleared!</b>")

@bot.on_message(filters.command("shuffle") & filters.group)
@catch_errors
@admin_only
async def shuffle_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.queue: return await m.reply_text("📭 <b>Queue is empty.</b>")
    random.shuffle(q.queue)
    await m.reply_text("🔀 <b>Queue shuffled!</b>")
