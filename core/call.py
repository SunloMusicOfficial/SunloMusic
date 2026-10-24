from pytgcalls import PyTgCalls
from core.bot import SunloBot
from utils.logger import LOGGER

# Ek dummy client assign karenge jo baad me main.py me update hoga
sunlo_call = PyTgCalls(SunloBot())

class CallManager:
    @staticmethod
    async def start():
        try:
            await sunlo_call.start()
            LOGGER.info("✅ PyTgCalls Audio Engine Started Successfully!")
        except Exception as e:
            LOGGER.error(f"Error starting PyTgCalls: {e}")
