from pytgcalls import PyTgCalls, filters
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamType, Update
from SunloMusic.bot import assistant
from SunloMusic.logger import LOGGER

call = PyTgCalls(assistant, cache_duration=100)

async def start_call():
    await call.start()
    LOGGER.info("✅ PyTgCalls engine started")

async def play_stream(chat_id: int, url: str, video: bool = False):
    if video:
        stream = MediaStream(url, video_parameters=VideoQuality.HD_720p, audio_parameters=AudioQuality.HIGH, stream_type=StreamType().pulse_stream)
    else:
        stream = MediaStream(url, audio_parameters=AudioQuality.HIGH, stream_type=StreamType().pulse_stream)
    try:
        await call.play(chat_id, stream)
    except Exception:
        await call.change_stream(chat_id, stream)

async def pause_stream(chat_id: int):
    await call.pause_stream(chat_id)

async def resume_stream(chat_id: int):
    await call.resume_stream(chat_id)

async def stop_stream(chat_id: int):
    await call.leave_call(chat_id)

@call.on_update(filters.stream_end())
async def stream_end_handler(client, update: Update):
    from SunloMusic.queue import get_queue, clear_queue
    chat_id = update.chat_id
    q = get_queue(chat_id)
    q.now_playing = None
    if q.queue:
        nxt = q.queue.pop(0)
        q.now_playing = nxt
        await play_stream(chat_id, nxt.url, nxt.video)
    else:
        clear_queue(chat_id)
