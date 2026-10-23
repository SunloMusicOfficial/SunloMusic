from pyrogram import Client
from config.vars import Config
from utils.logger import LOGGER

class SunloBot(Client):
    def __init__(self):
        super().__init__(
            name="SunloMusic",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins"),
            sleep_threshold=15
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        self.LOGGER.info(f"Bot successfully started as @{self.me.username}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER.info("Bot stopped.")
