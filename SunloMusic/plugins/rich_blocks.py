from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from richgram import rich_send, rich_heading, rich_esc

# Note: richgram ke exact block names library ke version par depend karte hain.
# Agar error aaye toh fallback ke liye normal text use karein.

@bot.on_message(filters.command("allcommand_rich"))
@catch_errors
async def allcommand_rich_cmd(_, m: Message):
    # Ye ek structured rich message bhejega jisme headings, lists, aur tables honge
    text = (
        rich_heading("📜 SunloMusic Commands", level=2) +
        rich_heading("🎵 Music", level=3) +
        "<ul><li>/play</li><li>/vplay</li><li>/search</li><li>/trending</li></ul>" +
        rich_heading("⏯ Controls", level=3) +
        "<ul><li>/pause</li><li>/resume</li><li>/skip</li><li>/stop</li><li>/seek</li></ul>" +
        rich_heading("🎛 Effects", level=3) +
        "<ul><li>/bass</li><li>/8d</li><li>/nightcore</li><li>/reset</li></ul>" +
        rich_heading("🛡 Admin", level=3) +
        "<ul><li>/settings</li><li>/welcome</li><li>/tagall</li><li>/purge</li></ul>"
    )
    try:
        await rich_send(bot, m.chat.id, text)
    except:
        # Fallback if rich blocks not supported
        await m.reply_text("📜 <b>Use /allcommand for the full list.</b>")
