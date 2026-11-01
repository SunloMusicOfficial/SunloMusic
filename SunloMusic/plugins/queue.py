import random, os, time
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.formatters import format_duration
from SunloMusic.queues import get_queue

@bot.on_message(filters.command("queue") & filters.group)
@catch_errors
async def queue_cmd(_, m: Message):
    q = get_queue(m.chat.id)
    if not q.now_playing and not q.queue: return await m.reply_text("📭 <b>Queue is empty.</b>")
    text = "<b>📋 Current Queue</b>\n\n"
    if q.now_playing: text += f"<b>▶️ Now Playing:</b>\n🎵 {q.now_playing.title}\n⏱ {format_duration(q.now_playing.duration)}\n\n"
    if q.queue:
        text += "<b>⏭ Up Next:</b>\n"
        for i, t in enumerate(q.queue[:10], 1): text += f"{i}. {t.title} ({format_duration(t.duration)})\n"
    await m.reply_text(text)

# ✅ NEW: EXPORT COMMAND
@bot.on_message(filters.command("export") & filters.group)
@catch_errors
async def export_cmd(_, m: Message):
    q = get_queue(m.chat.id)
    if not q.now_playing and not q.queue:
        return await m.reply_text("📭 <b>Queue is empty, nothing to export.</b>")
        
    status = await m.reply_text("⏳ <b>Generating queue export...</b>")
    
    file_path = f"cache/queue_{m.chat.id}.txt"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"📋 SunloMusic Queue Export\n")
            f.write(f"Group: {m.chat.title}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*40 + "\n\n")
            
            if q.now_playing:
                f.write(f"▶️ NOW PLAYING:\n{q.now_playing.title}\nRequester: {q.now_playing.requester}\nDuration: {format_duration(q.now_playing.duration)}\n\n")
                
            if q.queue:
                f.write("⏭ UP NEXT:\n")
                for i, t in enumerate(q.queue, 1):
                    f.write(f"{i}. {t.title} | {format_duration(t.duration)} | Req: {t.requester}\n")
                    
        await m.reply_document(
            document=file_path,
            caption=f"📁 <b>Queue Exported successfully!</b>\n📊 Total Tracks: {len(q.queue) + (1 if q.now_playing else 0)}",
            file_name=f"Queue_{m.chat.title}.txt"
        )
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ <b>Export failed:</b> <code>{e}</code>")
    finally:
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

@bot.on_message(filters.command("clear") & filters.group)
@catch_errors
@admin_only
async def clear_cmd(_, m: Message):
    q = get_queue(m.chat.id)
    if not q.queue: return await m.reply_text("📭 <b>Queue is already empty.</b>")
    
    for t in q.queue:
        if t.message_id:
            try: await bot.delete_messages(m.chat.id, t.message_id)
            except: pass
            
    q.queue.clear()
    await m.reply_text("🗑 <b>Queue Cleared!</b>")

@bot.on_message(filters.command("shuffle") & filters.group)
@catch_errors
@admin_only
async def shuffle_cmd(_, m: Message):
    q = get_queue(m.chat.id)
    if not q.queue: return await m.reply_text("📭 <b>Queue is empty.</b>")
    random.shuffle(q.queue)
    await m.reply_text("🔀 <b>Queue shuffled!</b>")
