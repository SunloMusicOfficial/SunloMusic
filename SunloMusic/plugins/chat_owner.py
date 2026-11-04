from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

@bot.on_message(filters.service & filters.group)
@catch_errors
async def owner_change_handler(_, m: Message):
    # Chat owner left ya changed
    if hasattr(m, "chat_owner_left") and m.chat_owner_left:
        log = f"👑 <b>Chat Owner Left</b>\n💬 {m.chat.title}\n🆔 <code>{m.chat.id}</code>"
        if config.LOGGER_ID:
            try: await bot.send_message(config.LOGGER_ID, log)
            except: pass
    
    if hasattr(m, "chat_owner_changed") and m.chat_owner_changed:
        log = f"👑 <b>Chat Owner Changed</b>\n💬 {m.chat.title}\n🆔 <code>{m.chat.id}</code>"
        if config.LOGGER_ID:
            try: await bot.send_message(config.LOGGER_ID, log)
            except: pass
