from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from richgram import rich_send

@bot.on_message(filters.command("richhelp"))
@catch_errors
async def rich_help_cmd(_, m: Message):
    text = (
        "<tg-thinking>User is asking for help, loading the best UI...</tg-thinking>\n"
        "<h2>🎵 SunloMusic Help</h2>\n"
        "<p>Here are the available commands:</p>\n"
        "<tg-codeblock language='python'>\n# Play a song\nbot.play('Kesariya')\n</tg-codeblock>\n"
        "<tg-math>E = mc^2</tg-math>\n"
        "<b>Click the button below to see all commands!</b>"
    )
    try:
        await rich_send(bot, m.chat.id, text)
    except Exception as e:
        await m.reply_text(f"Rich blocks error: {e}")
