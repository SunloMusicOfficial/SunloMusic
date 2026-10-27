import asyncio
from SunloMusic.logger import LOGGER, print_banner
from SunloMusic.bot import start_bot
from SunloMusic.calls import start_call
from SunloMusic.plugins import load_plugins

async def main():
    print_banner()
    LOGGER.info("🚀 Starting SunloMusic...")
    await start_bot()
    await start_call()
    load_plugins()
    LOGGER.info("✅ Bot is live and ready!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("🛑 Shutting down...")
