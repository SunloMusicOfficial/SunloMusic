import asyncio
from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.queues import KARAOKE_CHATS, get_queue
from SunloMusic.lyrics import fetch_lyrics_text, send_karaoke

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
            await m.reply_text("🎤 <b>Karaoke Mode ON!</b>\nFetching lyrics for the current song...")
            asyncio.create_task(send_karaoke(bot, m.chat.id, q.now_playing.title))
        else:
            await m.reply_text("🎤 <b>Karaoke Mode ON!</b>\nBot will send lyrics for upcoming songs.")
            
    elif state == "off":
        KARAOKE_CHATS.discard(m.chat.id)
        await m.reply_text("🎤 <b>Karaoke Mode OFF.</b>")

@bot.on_message(filters.command("lyrics"))
@catch_errors
async def lyrics_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/lyrics song name</code>")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching lyrics...</b>")
    res = await fetch_lyrics_text(query)
    if res: 
        await status.edit_text(res)
    else: 
        await status.edit_text("❌ <b>Lyrics not found in any database.</b>")
