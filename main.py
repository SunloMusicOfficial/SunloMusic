from utils.keep_alive import ping_render_and_log
from utils.startup_log import send_startup_log
from core.auto_leave import auto_leave_monitor
import asyncio
import uvicorn
from core.bot import SunloBot
from core.call import sunlo_call, CallManager
from utils.logger import LOGGER
from pyrogram import idle
from database.mongodb import db
from web.app import app as web_app

async def start_web_server():
    config = uvicorn.Config(web_app, host="0.0.0.0", port=8080, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    import shutil, os
    if os.path.exists("cache"):
        shutil.rmtree("cache", ignore_errors=True)
    os.makedirs("cache", exist_ok=True)
    LOGGER.info("Starting SunloMusic Engine & Web Dashboard...")
    
    app = SunloBot()
    sunlo_call._app = app 
    
    try:
        await app.start()
        await CallManager.start()
        
        # Start web dashboard in background
        asyncio.create_task(start_web_server())
        asyncio.create_task(auto_leave_monitor())
        
        LOGGER.info("🚀 SunloMusic is ONLINE! Web Dashboard running on port 8080")
        await asyncio.create_task(ping_render_and_log(app))
    await send_startup_log(app) # Assuming app is your pyrogram client
    idle()
    except Exception as e:
        LOGGER.error(f"Error during startup: {e}")
    finally:
        LOGGER.info("Stopping services...")
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
