import asyncio
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.queues import KARAOKE_CHATS, get_queue
from SunloMusic.lyrics import fetch_lyrics_text, start_live_karaoke

@bot.on_message(filters.command("karaoke") & filters.group)
@catch_errors
@admin_only
async def karaoke_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/karaoke on</code>")
    state = m.command[1].lower()
    
    if state == "on":
        KARAOKE_CHATS.add(m.chat.id)
        q = get_queue(m.chat.id)
        if q.now_playing:
            await m.reply_text("🎤 <b>Karaoke Mode ON!</b>\nStarting live lyrics for the current song...")
            q.karaoke_task = asyncio.create_task(start_live_karaoke(bot, m.chat.id, q.now_playing.title, q.now_playing.duration, q))
        else:
            await m.reply_text("🎤 <b>Karaoke Mode ON!</b>\nBot will send live lyrics for upcoming songs.")
            
    elif state == "off":
        KARAOKE_CHATS.discard(m.chat.id)
        q = get_queue(m.chat.id)
        if q.karaoke_task:
            q.karaoke_task.cancel()
            q.karaoke_task = None
        await m.reply_text("🎤 <b>Karaoke Mode OFF.</b>")

@bot.on_message(filters.command("lyrics"))
@catch_errors
async def lyrics_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/lyrics song name</code>")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching lyrics...</b>")
    
    res = await fetch_lyrics_text(query)
    if res: 
        await status.edit_text(f"🎤 <b>{query}</b>\n━━━━━━━━━━━━━\n<blockquote>{res[:4000]}</blockquote>")
    else: 
        await status.edit_text("❌ <b>Lyrics not found in any database.</b>")
