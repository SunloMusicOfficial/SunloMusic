from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded, GroupCallConfig
from pytgcalls.exceptions import NoActiveGroupCall
import SunloMusic.bot as bot_module
from SunloMusic.logger import LOGGER
import base64

call = None

async def stream_end_handler(client, update: StreamEnded):
    from SunloMusic.queues import get_queue, clear_queue
    from SunloMusic.keyboards import player_keyboard
    from SunloMusic.formatters import format_duration
    from SunloMusic.thumbnails import generate_thumbnail
    from SunloMusic.plugins.play import update_live_timer
    from SunloMusic.config import config
    import time
    import asyncio
    
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
            try:
                q.start_time = time.time()
                q.total_paused = 0
                q.paused = False
                
                thumb = await generate_thumbnail(nxt.thumbnail, nxt.title, format_duration(nxt.duration), nxt.requester)
                dur_str = format_duration(nxt.duration)
                
                b64_title = base64.urlsafe_b64encode(nxt.title.encode()).decode().strip("=")
                title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
                
                caption = (
                    f"<b>🎧🎶 Music Time 🎶🎧</b>\n\n"
                    f"🎵 <a href='{title_link}'>{nxt.title}</a>\n"
                    f"⏱ <b>Duration:</b> {dur_str}\n"
                    f"👤 <b>Request:</b> <a href='tg://user?id={nxt.requester_id}'>{nxt.requester}</a>"
                )
                
                if thumb:
                    sent_msg = await bot_module.bot.send_photo(chat_id, thumb, caption=caption, reply_markup=player_keyboard(q, 0))
                else:
                    sent_msg = await bot_module.bot.send_message(chat_id, caption, reply_markup=player_keyboard(q, 0))
                    
                q.playing_message_id = sent_msg.id
                
                if q.timer_task:
                    q.timer_task.cancel()
                q.timer_task = asyncio.create_task(update_live_timer(chat_id, sent_msg.id))
                
            except Exception as e:
                LOGGER.error(f"Error sending auto-play message: {e}")
    else:
        if q.timer_task:
            q.timer_task.cancel()
        try:
            if call: await call.leave_call(chat_id)
        except Exception as e:
            LOGGER.error(f"Error leaving VC: {e}")
            
        clear_queue(chat_id)
        try: 
            await bot_module.bot.send_message(chat_id, "⏹ <b>Queue khatam. Assistant ne VC leave kar diya.</b>")
        except: 
            pass

def init_calls():
    global call
    if bot_module.assistant:
        call = PyTgCalls(bot_module.assistant, cache_duration=100)
        call.on_update(fl.stream_end())(stream_end_handler)
    else:
        LOGGER.error("❌ Assistant not initialized")

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
        stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p)
    else:
        stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
        
    try:
        try: await call.leave_call(chat_id)
        except: pass
        await call.play(chat_id, stream, config=GroupCallConfig(auto_start=True))
        return True
    except NoActiveGroupCall:
        LOGGER.error("❌ No active Voice Chat found.")
        return False
    except Exception as e:
        error_msg = str(e).lower()
        if "mute" in error_msg or "unmute" in error_msg:
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
