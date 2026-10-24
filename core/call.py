from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from core.bot import SunloBot
from utils.logger import LOGGER

# Initialize PyTgCalls for ntgcalls architecture
try:
    sunlo_call = PyTgCalls()
except Exception as e:
    LOGGER.error(f"Error initializing PyTgCalls: {e}")

class CallManager:
    @staticmethod
    async def start():
        try:
            await sunlo_call.start()
            LOGGER.info("🔊 PyTgCalls (ntgcalls engine) started successfully!")
        except Exception as e:
            LOGGER.error(f"Failed to start PyTgCalls: {e}")
