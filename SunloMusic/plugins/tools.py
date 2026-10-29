from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors, admin_only
from SunloMusic.queues import KARAOKE_CHATS
from SunloMusic.lyrics import fetch_lyrics_text

@bot.on_message(filters.command("karaoke") & filters.group)
@catch_errors
@admin_only
async def karaoke_cmd(_, m):
    if len(m.command) < 2: return await m.reply_text("❌ <b>Usage:</b> <code>/karaoke on</code>")
    state = m.command[1].lower()
    if state == "on":
        KARAOKE_CHATS.add(m.chat.id)
        await m.reply_text("🎤 <b>Karaoke Mode ON!</b>")
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
    if res: await status.edit_text(res)
    else: await status.edit_text("❌ <b>Lyrics not found in any database.</b>")
