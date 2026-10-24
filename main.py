import asyncio
from core.bot import SunloBot
from core.call import SunloCall
from utils.logger import LOGGER
from pyrogram import idle

# Initialize database to trigger connection
from database.mongodb import db

async def main():
    LOGGER.info("Starting SunloMusic Engine...")
    
    # Initialize Bot & Call instances
    app = SunloBot()
    call = SunloCall(app)
    
    try:
        await app.start()
        await call.start()
        
        LOGGER.info("🚀 SunloMusic is now completely ONLINE with Audio Engine!")
        
        # Idle block karta hai taaki script band na ho
        await idle()
    except KeyboardInterrupt:
        LOGGER.warning("Received stop signal from user.")
    except Exception as e:
        LOGGER.error(f"Error during startup: {e}")
    finally:
        LOGGER.info("Stopping services...")
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
