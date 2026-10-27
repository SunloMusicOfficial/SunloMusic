from pyrogram import filters
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.ytdlp import extract_audio
from SunloMusic.formatters import format_duration
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

@bot.on_message(filters.command("song"))
@catch_errors
async def song_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Give a song name.</b>")
    
    query = " ".join(m.command[1:])
    status = await m.reply_text("⏳ <b>Wait a sec, getting the beats...</b>")
    
    info = await extract_audio(query)
    if not info:
        return await status.edit_text("❌ <b>Not found.</b>")
        
    await status.edit_text("📤 <b>Uploading audio file...</b>")
    
    try:
        # ✅ Direct Audio File bhejega
        await m.reply_audio(
            audio=info["url"],
            title=info["title"],
            duration=info["duration"],
            caption=f"🎶 <b>{info['title']}</b>\n\n🤖 @{config.BOT_USERNAME.strip('@')}"
        )
        await status.delete()
    except Exception as e:
        LOGGER.error(f"Error sending song: {e}")
        await status.edit_text(f"❌ <b>Failed to upload audio.</b>\n<code>{e}</code>")
