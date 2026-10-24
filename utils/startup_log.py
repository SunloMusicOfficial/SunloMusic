from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.vars import Config
from utils.logger import LOGGER

async def send_startup_log(bot: Client):
    if not Config.LOG_GROUP_ID:
        return
        
    try:
        bot_info = await bot.get_me()
        # Ek premium music bot ka default image (aap isko baad me change kar sakte ho)
        photo_url = "https://telegra.ph/file/c5952793fa720b08db669.jpg" 
        
        caption = (
            f"🚀 **{bot_info.first_name} is Online!**\n\n"
            f"🤖 **Bot Status:** `Online`\n"
            f"👤 **Assistant:** `Connected`\n"
            f"🌐 **API Router:** `Active (Universal)`\n"
            f"⚡ **Engine:** `SunloMusic Premium Engine`\n\n"
            f"__All systems are fully operational and ready to stream.__"
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Bot to your Group", url=f"https://t.me/{bot_info.username}?startgroup=true")]
        ])
        
        # Log group me premium card bhejna
        await bot.send_photo(
            chat_id=int(Config.LOG_GROUP_ID),
            photo=photo_url,
            caption=caption,
            reply_markup=buttons
        )
        LOGGER.info("Startup Premium Card sent to Log Group!")
    except Exception as e:
        LOGGER.error(f"Failed to send startup log (Check LOG_GROUP_ID): {e}")
