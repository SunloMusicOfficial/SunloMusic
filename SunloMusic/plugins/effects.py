import asyncio
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.calls import play_stream, stop_stream
from SunloMusic.decorators import admin_only, catch_errors
from SunloMusic.queues import get_queue, clear_queue

@bot.on_message(filters.command("bass") & filters.group)
@catch_errors
@admin_only
async def bass_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text("❌ Nothing is playing.")
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video, effect="bass")
    await m.reply_text("🔊 <b>Bass Boost Activated!</b>")

@bot.on_message(filters.command("8d") & filters.group)
@catch_errors
@admin_only
async def eightd_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text("❌ Nothing is playing.")
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video, effect="8d")
    await m.reply_text("🎧 <b>8D Audio Activated!</b>")

@bot.on_message(filters.command("nightcore") & filters.group)
@catch_errors
@admin_only
async def nightcore_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text("❌ Nothing is playing.")
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video, effect="nightcore")
    await m.reply_text("⚡ <b>Nightcore Activated!</b>")

@bot.on_message(filters.command("reset") & filters.group)
@catch_errors
@admin_only
async def reset_cmd(_, m):
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text("❌ Nothing is playing.")
    await play_stream(m.chat.id, q.now_playing.url, q.now_playing.video, effect="none")
    await m.reply_text("🎵 <b>Normal Audio Restored.</b>")

@bot.on_message(filters.command("sleep") & filters.group)
@catch_errors
@admin_only
async def sleep_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/sleep 10m</code> (or 30s)")
    
    time_str = m.command[1].lower()
    seconds = 0
    if time_str.endswith("m"): seconds = int(time_str[:-1]) * 60
    elif time_str.endswith("s"): seconds = int(time_str[:-1])
    else:
        try: seconds = int(time_str) * 60
        except: return await m.reply_text("❌ Invalid time format. Use 10m or 30s.")
        
    if seconds <= 0: return await m.reply_text("❌ Time must be greater than 0.")
    
    q = get_queue(m.chat.id)
    if not q.now_playing: return await m.reply_text("❌ Nothing is playing.")
    
    await m.reply_text(f"💤 <b>Sleep Timer set for {time_str}.</b>\nBot will leave VC automatically.")
    
    async def sleep_task():
        await asyncio.sleep(seconds)
        await stop_stream(m.chat.id)
        clear_queue(m.chat.id)
        try: await bot.send_message(m.chat.id, "💤 <b>Sleep timer ended. Assistant left VC. Good night!</b>")
        except: pass
        
    asyncio.create_task(sleep_task())
