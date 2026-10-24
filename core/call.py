from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types import AudioPiped
from core.bot import SunloBot
from core.player import get_next_track, clear_queue
from utils.logger import LOGGER

sunlo_call = PyTgCalls(SunloBot())

class CallManager:
    @staticmethod
    async def start():
        try:
            await sunlo_call.start()
            LOGGER.info("✅ PyTgCalls Audio Engine Started Successfully!")
        except Exception as e:
            LOGGER.error(f"Error starting PyTgCalls: {e}")

@sunlo_call.on_stream_end()
async def on_stream_end(client: PyTgCalls, update: Update):
    chat_id = update.chat_id
    next_track = get_next_track(chat_id)
    
    if next_track:
        try:
            await client.play(
                chat_id,
                AudioPiped(next_track["stream_url"])
            )
            # Yahan aage chalkar hum auto-message bhejenge ki next gaana chal gaya
        except Exception as e:
            LOGGER.error(f"Auto-play next error: {e}")
    else:
        # Agar queue khali hai toh leave kar de
        await client.leave_call(chat_id)
        clear_queue(chat_id)
