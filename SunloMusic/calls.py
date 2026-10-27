from pytgcalls import PyTgCalls, filters
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded
from SunloMusic.bot import assistant, bot
from SunloMusic.logger import LOGGER

call = PyTgCalls(assistant, cache_duration=100) if assistant else None

async def start_call():
    if call:
        await call.start()
        LOGGER.info("✅ PyTgCalls engine started")

async def play_stream(chat_id: int, url: str, video: bool = False):
    if not call: return False
    if video:
        stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p)
    else:
        stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH)
    try:
        await call.play(chat_id, stream)
        return True
    except Exception:
        try:
            await call.change_stream(chat_id, stream)
            return True
        except Exception as e:
            LOGGER.error(f"VC Error: {e}")
            return False

async def pause_stream(chat_id: int):
    if call: 
        await call.pause(chat_id)  # ✅ Official v2+ method

async def resume_stream(chat_id: int):
    if call: 
        await call.resume(chat_id) # ✅ Official v2+ method

async def stop_stream(chat_id: int):
    if call: 
        await call.leave_call(chat_id)

@(call.on_update(filters.stream_end()) if call else (lambda x: x))
async def stream_end_handler(client, update: StreamEnded): # ✅ Correct Type Hint
    from SunloMusic.queues import get_queue, clear_queue
    chat_id = update.chat_id
    q = get_queue(chat_id)
    
    if q.loop == 1 and q.now_playing:
        await play_stream(chat_id, q.now_playing.url, q.now_playing.video)
        return

    if q.loop == 2 and q.now_playing:
        q.queue.append(q.now_playing)

    q.now_playing = None
    if q.queue:
        nxt = q.queue.pop(0)
        q.now_playing = nxt
        success = await play_stream(chat_id, nxt.url, nxt.video)
        if success:
            try: await bot.send_message(chat_id, f"🎶 <b>Now Playing:</b>\n<b>{nxt.title}</b>\n👤 {nxt.requester}")
            except: pass
    else:
        clear_queue(chat_id)
        try: await bot.send_message(chat_id, "⏹ <b>Queue khatam. Bot ne VC leave kar diya.</b>")
        except: pass
