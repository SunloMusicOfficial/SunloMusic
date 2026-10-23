import asyncio
from core.bot import SunloBot
from pyrogram import idle
from utils.logger import LOGGER

async def main():
    LOGGER.info("Starting SunloMusic Engine...")
    bot = SunloBot()
    
    try:
        await bot.start()
        LOGGER.info("Bot is now online and ready to receive commands.")
        await idle()
    except Exception as e:
        LOGGER.error(f"Error during bot startup: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
