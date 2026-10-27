import asyncio
from SunloMusic.logger import LOGGER, print_banner
from SunloMusic.bot import start_bot
from SunloMusic.calls import start_call
from SunloMusic.plugins import load_plugins

async def main():
    print_banner()
    await start_bot()
    await start_call()
    load_plugins()
    LOGGER.info("✅ Bot is live!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
