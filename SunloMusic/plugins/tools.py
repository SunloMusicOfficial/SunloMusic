from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration # ✅ Added missing import

@bot.on_message(filters.command("song"))
async def song_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Give a song name.</b>")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching...</b>")
    info = await extract_audio(query)
    if not info:
        return await status.edit_text("❌ <b>Not found.</b>")
    await status.edit_text(
        f"🎵 <b>{info['title']}</b>\n"
        f"⏱ <b>Duration:</b> {format_duration(info['duration'])}\n\n"
        f"🔗 <a href='{info['url']}'>Direct Link</a>"
    )
