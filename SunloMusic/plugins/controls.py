from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream
from SunloMusic.decorators import admin_only
from SunloMusic.queue import get_queue, clear_queue

@bot.on_message(filters.command("pause") & filters.group)
@admin_only
async def pause_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await pause_stream(m.chat.id); q.paused = True
        await m.reply_text("⏸ Paused")

@bot.on_message(filters.command("resume") & filters.group)
@admin_only
async def resume_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await resume_stream(m.chat.id); q.paused = False
        await m.reply_text("▶️ Resumed")

@bot.on_message(filters.command("stop") & filters.group)
@admin_only
async def stop_cmd(_, m):
    await stop_stream(m.chat.id); clear_queue(m.chat.id)
    await m.reply_text("⏹ Stopped")
