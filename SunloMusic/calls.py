from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded
from pytgcalls.exceptions import NoActiveGroupCall, UnMuteNeeded
from SunloMusic.bot import assistant, bot
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
            try: await bot.send_message(chat_id, f"🎶 <b>Now Playing:</b>\n<b>{nxt.title}</b>\n👤 {nxt.requester}")
            except: pass
    else:
        clear_queue(chat_id)
        try: await bot.send_message(chat_id, "⏹ <b>Queue khatam. Bot ne VC leave kar diya.</b>")
        except: pass

def init_calls():
    global call
    if assistant:
        call = PyTgCalls(assistant, cache_duration=100)
        call.on_update(fl.stream_end())(stream_end_handler)

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
        # ✅ FIX: video_flags=IGNORE zaroori hai taaki audio stream crash na ho
        stream = MediaStream(
            media_path=url,
            audio_parameters=AudioQuality.HIGH,
            video_flags=MediaStream.Flags.IGNORE,
        )
        
    try:
        # Ghost session cleanup (agar pehle se koi stream atka hai)
        try: await call.leave_call(chat_id)
        except: pass
        
        await call.play(chat_id, stream, auto_start=True)
        return True
    except UnMuteNeeded:
        LOGGER.warning("⚠️ Assistant muted. Trying to unmute...")
        try:
            await call.unmute(chat_id)
            await call.play(chat_id, stream, auto_start=True)
            return True
        except Exception as e:
            LOGGER.error(f"❌ Unmute failed: {e}")
            return False
    except NoActiveGroupCall:
        LOGGER.error("❌ No active Voice Chat found (Supergroup required).")
        return False
    except Exception as e:
        LOGGER.error(f"❌ PyTgCalls Error: {type(e).__name__} - {e}")
        return False

async def pause_stream(chat_id: int):
    if call: await call.pause(chat_id)

async def resume_stream(chat_id: int):
    if call: await call.resume(chat_id)

async def stop_stream(chat_id: int):
    if call: await call.leave_call(chat_id)
