from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import pause_stream, resume_stream, stop_stream, play_stream
from SunloMusic.decorators import admin_only
from SunloMusic.queue import get_queue, clear_queue
from SunloMusic.texts import NOT_PLAYING_TEXT

@bot.on_message(filters.command("pause") & filters.group)
@admin_only
async def pause_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await pause_stream(m.chat.id); q.paused = True
        await m.reply_text("⏸ <b>Paused</b>")
    else:
        await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_message(filters.command("resume") & filters.group)
@admin_only
async def resume_cmd(_, m):
    q = get_queue(m.chat.id)
    if q.now_playing:
        await resume_stream(m.chat.id); q.paused = False
        await m.reply_text("▶️ <b>Resumed</b>")
    else:
        await m.reply_text(NOT_PLAYING_TEXT)

@bot.on_message(filters.command(["skip", "next"]) & filters.group)
@admin_only
async def skip_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.now_playing:
        return await m.reply_text(NOT_PLAYING_TEXT)
    q.now_playing = None
    if q.queue:
        nxt = q.queue.pop(0)
        q.now_playing = nxt
        await play_stream(m.chat.id, nxt.url, nxt.video)
        await m.reply_text(f"⏭ <b>Skipped to:</b> {nxt.title}")
    else:
        await stop_stream(m.chat.id)
        clear_queue(m.chat.id)
        await m.reply_text("⏭ <b>Skipped. Queue is now empty.</b>")

@bot.on_message(filters.command(["stop", "end"]) & filters.group)
@admin_only
async def stop_cmd(_, m):
    await stop_stream(m.chat.id)
    clear_queue(m.chat.id)
    await m.reply_text("⏹ <b>Stopped and left VC.</b>")
