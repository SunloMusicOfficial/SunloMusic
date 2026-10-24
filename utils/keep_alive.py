import asyncio
import aiohttp
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.vars import Config
from utils.logger import LOGGER

async def ping_render_and_log(bot: Client):
    # Initial wait taaki bot properly start ho jaye
    await asyncio.sleep(60) 
    
    while True:
        # Ping the Web URL to prevent Render Sleep Mode
        if Config.WEB_URL:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(Config.WEB_URL) as resp:
                        LOGGER.info(f"Self-Ping HTTP Status: {resp.status}")
            except Exception as e:
                LOGGER.error(f"Self-Ping Error: {e}")

        # Send Premium Card to Log Group
        if Config.LOG_GROUP_ID:
            try:
                bot_info = await bot.get_me()
                photo_url = "https://telegra.ph/file/10d1f7c223c6d7a46abf1.jpg" # Premium Ping Image
                
                caption = (
                    f"🔄 **Render Keep-Alive Ping**\n\n"
                    f"🤖 **Bot:** `{bot_info.first_name}`\n"
                    f"✅ **Status:** `Active & Running`\n"
                    f"⏱ **Interval:** `Every 12 Minutes`\n"
                    f"🌐 **Server:** `Render Web Service`\n\n"
                    f"__Bot is automatically staying awake to prevent sleep mode!__"
                )
                
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🖥 View Server URL", url=Config.WEB_URL if Config.WEB_URL else "https://render.com")]
                ])
                
                await bot.send_photo(
                    chat_id=int(Config.LOG_GROUP_ID),
                    photo=photo_url,
                    caption=caption,
                    reply_markup=buttons
                )
            except Exception as e:
                LOGGER.error(f"Keep-Alive Log failed (Check LOG_GROUP_ID): {e}")
                
        # Wait for 12 minutes (12 * 60 = 720 seconds) before next ping
        await asyncio.sleep(720)
