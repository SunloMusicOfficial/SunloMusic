import sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from SunloMusic.logger import LOGGER, print_banner
from SunloMusic.bot import init_clients, start_bot
from SunloMusic.calls import init_calls, start_call
from SunloMusic.plugins import load_plugins
from SunloMusic.keep_alive import start_keep_alive

async def main():
    print_banner()
    LOGGER.info("🚀 Starting SunloMusic...")
    
    # ✅ CLEAR OLD CACHE (Fixes corrupted .webm files)
    if os.path.exists("cache/downloads"):
        shutil.rmtree("cache/downloads")
        LOGGER.info("🧹 Cleared old downloads cache")
    os.makedirs("cache/downloads", exist_ok=True)
    
    init_clients()
    init_calls()
    
    await start_bot()
    await start_call()
    await start_keep_alive()
    
    load_plugins()
    LOGGER.info("✅ Bot is live and ready!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("🛑 Shutting down...")
