from pyrogram import Client
from SunloMusic.config import config
from SunloMusic.logger import LOGGER

# Main Bot Client
bot = Client(
    name="SunloMusicBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    in_memory=True,
)

# Assistant Client (Userbot - Voice Chat join karne ke liye)
assistant = Client(
    name="SunloAssistant",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING,
    in_memory=True,
)

async def start_bot():
    await bot.start()
    await assistant.start()
    me = await bot.get_me()
    LOGGER.info(f"✅ Bot started as @{me.username}")
