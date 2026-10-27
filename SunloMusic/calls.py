from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded, GroupCallConfig
from pytgcalls.exceptions import NoActiveGroupCall
import SunloMusic.bot as bot_module
from SunloMusic.logger import LOGGER

call = None

async def stream_end_handler(client, update: StreamEnded):
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
            try: await bot_module.bot.send_message(chat_id, f"🎶 <b>Now Playing:</b>\n<b>{nxt.title}</b>\n👤 {nxt.requester}")
            except: pass
    else:
        clear_queue(chat_id)
        try: await bot_module.bot.send_message(chat_id, "⏹ <b>Queue khatam. Bot ne VC leave kar diya.</b>")
        except: pass

def init_calls():
    global call
    if bot_module.assistant:
        call = PyTgCalls(bot_module.assistant, cache_duration=100)
        call.on_update(fl.stream_end())(stream_end_handler)
    else:
        LOGGER.error("❌ Assistant not initialized in bot.py")

async def start_call():
    if call:
        await call.start()
        LOGGER.info("✅ PyTgCalls engine started")

async def play_stream(chat_id: int, url: str, video: bool = False):
    if not call: 
        LOGGER.error("❌ PyTgCalls call object is None")
        return False
    
    LOGGER.info(f"🎵 Attempting to play URL: {url[:80]}... in {chat_id}")
    
    if video:
        stream = MediaStream(
            media_path=url,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.HD_720p,
        )
    else:
        stream = MediaStream(
            media_path=url,
            audio_parameters=AudioQuality.HIGH,
            video_flags=MediaStream.Flags.IGNORE,
        )
        
    try:
        try: await call.leave_call(chat_id)
        except: pass
        
        # ✅ PyTgCalls v3.0.0 ke liye sahi syntax
        await call.play(chat_id, stream, config=GroupCallConfig(auto_start=True))
        return True
    except NoActiveGroupCall:
        LOGGER.error("❌ No active Voice Chat found (Supergroup required).")
        return False
    except Exception as e:
        error_msg = str(e).lower()
        if "mute" in error_msg or "unmute" in error_msg:
            LOGGER.warning(f"⚠️ Mute-related error detected: {e}. Trying to unmute...")
            try:
                await call.unmute(chat_id)
                await call.play(chat_id, stream, config=GroupCallConfig(auto_start=True))
                return True
            except Exception as e2:
                LOGGER.error(f"❌ Unmute failed: {e2}")
                return False
        LOGGER.error(f"❌ PyTgCalls Error: {type(e).__name__} - {e}")
        return False

async def pause_stream(chat_id: int):
    if call: await call.pause(chat_id)

async def resume_stream(chat_id: int):
    if call: await call.resume(chat_id)

async def stop_stream(chat_id: int):
    if call: await call.leave_call(chat_id)
