import sys
import os
# Path fix: taaki direct "python SunloMusic" chalane par imports work karein
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from SunloMusic.logger import LOGGER, print_banner
from SunloMusic.bot import start_bot
from SunloMusic.calls import start_call
from SunloMusic.plugins import load_plugins
from SunloMusic.keep_alive import start_keep_alive

async def main():
    print_banner()
    LOGGER.info("🚀 Starting SunloMusic...")
    
    await start_bot()
    await start_call()
    await start_keep_alive() # Start web server & pinger
    
    load_plugins()
    LOGGER.info("✅ Bot is live and ready!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("🛑 Shutting down...")
