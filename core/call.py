from pytgcalls import PyTgCalls
from pyrogram import Client
from utils.logger import LOGGER

class SunloCall(PyTgCalls):
    def __init__(self, client: Client):
        super().__init__(client)
        self.LOGGER = LOGGER

    async def start(self):
        try:
            await super().start()
            self.LOGGER.info("✅ PyTgCalls Audio Engine Started Successfully!")
        except Exception as e:
            self.LOGGER.error(f"Error starting PyTgCalls: {e}")
