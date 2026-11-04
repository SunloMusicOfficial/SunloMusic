import time
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors

@bot.on_message(filters.command("time"))
@catch_errors
async def time_cmd(_, m: Message):
    now = int(time.time())
    # Telegram date_time entity ka format
    # Ye HTML/Markdown me directly use nahi hota, but API level par entity hai
    # Pyrogram/Kurigram me abhi tak direct support nahi hai, isliye normal text
    await m.reply_text(
        f"🕐 <b>Current Server Time:</b>\n"
        f"<code>{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(now))} UTC</code>"
    )
