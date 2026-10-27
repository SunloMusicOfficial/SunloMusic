from pyrogram import Client
from SunloMusic.config import config
from SunloMusic.logger import LOGGER

bot = None
assistant = None

def init_clients():
    global bot, assistant
    bot = Client("SunloMusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN, in_memory=True)
    if config.SESSION_STRING:
        assistant = Client("SunloAssistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION_STRING, in_memory=True)

async def start_bot():
    await bot.start()
    me = await bot.get_me()
    LOGGER.info(f"✅ Bot started as @{me.username}")
    
    if assistant:
        await assistant.start()
        LOGGER.info("✅ Assistant started (VC Ready)")
    else:
        LOGGER.warning("⚠️ No SESSION_STRING provided. Voice Chat won't work!")
