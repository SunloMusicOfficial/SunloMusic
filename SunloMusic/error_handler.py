import traceback
from pyrogram.types import Message, CallbackQuery
from SunloMusic.config import config
from SunloMusic.logger import LOGGER

async def log_error_to_group(update, error: Exception):
    error_msg = traceback.format_exc()
    LOGGER.error(error_msg)
    
    user = update.from_user if hasattr(update, 'from_user') else None
    user_mention = user.mention if user else "Unknown"
    user_id = user.id if user else 0
    
    if isinstance(update, Message):
        chat_title = update.chat.title or update.chat.first_name
        chat_id = update.chat.id
        cmd = update.text or update.caption or "Unknown Command"
    elif isinstance(update, CallbackQuery):
        chat_title = update.message.chat.title or update.message.chat.first_name
        chat_id = update.message.chat.id
        cmd = update.data
    else:
        chat_title = "Unknown"
        chat_id = 0
        cmd = "Unknown"

    text = (
        f"<b>🚨 EMERGENCY ERROR 🚨</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 <b>Owner:</b> <a href='tg://user?id={config.OWNER_ID}'>Sakil</a>\n"
        f"👤 <b>User:</b> {user_mention} (<code>{user_id}</code>)\n"
        f"💬 <b>Chat:</b> {chat_title} (<code>{chat_id}</code>)\n"
        f"🛠 <b>Action:</b> <code>{cmd}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Error Details:</b>\n"
        f"<pre>{error_msg[-3000:]}</pre>" # Show last 3000 chars
    )

    try:
        if config.LOGGER_ID:
            from SunloMusic.bot import bot
            if bot:
                await bot.send_message(config.LOGGER_ID, text)
    except Exception as e:
        LOGGER.error(f"Failed to send error log: {e}")

    try:
        user_text = (
            f"🚨 <b>Oops! An unexpected error occurred.</b>\n\n"
            f"Don't worry, the Owner (<a href='tg://user?id={config.OWNER_ID}'>Sakil</a>) has been tagged and "
            f"the error details have been sent to the Log Group automatically."
        )
        if isinstance(update, Message):
            await update.reply_text(user_text)
        elif isinstance(update, CallbackQuery):
            await update.answer("🚨 Error occurred! Owner has been notified.", show_alert=True)
    except: pass
