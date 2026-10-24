import asyncio
from core.bot import SunloBot
from core.call import sunlo_call, CallManager
from utils.logger import LOGGER
from pyrogram import idle
from database.mongodb import db

async def main():
    LOGGER.info("Starting SunloMusic Engine...")
    
    app = SunloBot()
    # PyTgCalls ko original app pass karenge
    sunlo_call._app = app 
    
    try:
        await app.start()
        await CallManager.start()
        
        LOGGER.info("🚀 SunloMusic is now completely ONLINE with Audio Engine!")
        await idle()
    except Exception as e:
        LOGGER.error(f"Error during startup: {e}")
    finally:
        LOGGER.info("Stopping services...")
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
