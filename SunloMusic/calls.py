import asyncio
import time
import base64
import os
from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded, GroupCallConfig
from pytgcalls.exceptions import NoActiveGroupCall
import SunloMusic.bot as bot_module
from SunloMusic.logger import LOGGER
from SunloMusic.config import config
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail
from SunloMusic.keyboards import player_keyboard

call = None

def cleanup_file(url: str):
    """Deletes downloaded video files to save disk space"""
    if url and os.path.exists(url) and url.endswith(('.mp4', '.webm', '.m4a')):
        try: os.remove(url)
        except: pass

async def update_live_timer(chat_id, msg_id):
    from SunloMusic.queues import get_queue
    while True:
        await asyncio.sleep(5)
        q = get_queue(chat_id)
        if not q.now_playing or q.playing_message_id != msg_id:
            break
        if q.paused: continue
            
        elapsed = int(time.time() - q.start_time - q.total_paused)
        if elapsed >= q.now_playing.duration and q.now_playing.duration > 0:
            break
            
        try:
            dur_str = format_duration(q.now_playing.duration)
            b64_title = base64.urlsafe_b64encode(q.now_playing.title.encode()).decode().strip("=")
            title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
            
            caption = (
                f"<b>🎧🎶 Music Time 🎶🎧</b>\n"
                f"━━━━━━━━━━━━━\n"
                f"🎵 <a href='{title_link}'>{q.now_playing.title}</a>\n"
                f"━━━━━━━━━━━━━\n"
                f"⏱ Duration: {dur_str}\n"
                f"━━━━━━━━━━━━━\n"
                f"🙋‍♂️ Request: <a href='tg://user?id={q.now_playing.requester_id}'>{q.now_playing.requester}</a>\n"
                f"━━━━━━━━━━━━━"
            )
            
            try:
                await bot_module.bot.edit_message_caption(
                    chat_id=chat_id, message_id=msg_id,
                    caption=caption, reply_markup=player_keyboard(q, elapsed)
                )
            except Exception:
                await bot_module.bot.edit_message_text(
                    chat_id=chat_id, message_id=msg_id,
                    text=caption, reply_markup=player_keyboard(q, elapsed)
                )
        except Exception:
            pass

async def start_next_song(chat_id, q):
    from SunloMusic.queues import clear_queue
    
    if q.timer_task: 
        q.timer_task.cancel()
        q.timer_task = None
    
    if q.playing_message_id:
        try: await bot_module.bot.delete_messages(chat_id, q.playing_message_id)
        except: pass
        q.playing_message_id = 0

    # ✅ Cleanup old file
    if q.now_playing:
        cleanup_file(q.now_playing.url)

    q.now_playing = None
    if q.queue:
        nxt = q.queue.pop(0)
        q.now_playing = nxt
        
        if nxt.message_id:
            try: await bot_module.bot.delete_messages(chat_id, nxt.message_id)
            except: pass
            nxt.message_id = 0

        success = await play_stream(chat_id, nxt.url, nxt.video)
        if success:
            q.start_time = time.time()
            q.total_paused = 0
            q.paused = False
            
            thumb = await generate_thumbnail(nxt.thumbnail, nxt.title, format_duration(nxt.duration), nxt.requester)
            dur_str = format_duration(nxt.duration)
            b64_title = base64.urlsafe_b64encode(nxt.title.encode()).decode().strip("=")
            title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
            
            caption = (
                f"<b>🎧🎶 Music Time 🎶🎧</b>\n"
                f"━━━━━━━━━━━━━\n"
                f"🎵 <a href='{title_link}'>{nxt.title}</a>\n"
                f"━━━━━━━━━━━━━\n"
                f"⏱ Duration: {dur_str}\n"
                f"━━━━━━━━━━━━━\n"
                f"🙋‍♂️ Request: <a href='tg://user?id={nxt.requester_id}'>{nxt.requester}</a>\n"
                f"━━━━━━━━━━━━━"
            )
            
            if thumb:
                sent_msg = await bot_module.bot.send_photo(chat_id, thumb, caption=caption, reply_markup=player_keyboard(q, 0))
            else:
                sent_msg = await bot_module.bot.send_message(chat_id, caption, reply_markup=player_keyboard(q, 0))
                
            q.playing_message_id = sent_msg.id
            q.timer_task = asyncio.create_task(update_live_timer(chat_id, sent_msg.id))
        else:
            await bot_module.bot.send_message(chat_id, "❌ <b>Failed to play next song. Skipping...</b>")
            await start_next_song(chat_id, q)
    else:
        try:
            if call: await call.leave_call(chat_id)
        except Exception: pass
        clear_queue(chat_id)
        await bot_module.bot.send_message(chat_id, "⏹ <b>Queue khatam. Assistant ne VC leave kar diya.</b>")

async def stream_end_handler(client, update: StreamEnded):
    from SunloMusic.queues import get_queue
    chat_id = update.chat_id
    q = get_queue(chat_id)
    
    if q.loop == 1 and q.now_playing:
        await play_stream(chat_id, q.now_playing.url, q.now_playing.video)
        q.start_time = time.time()
        q.total_paused = 0
        q.paused = False
        return
        
    if q.loop == 2 and q.now_playing:
        q.queue.append(q.now_playing)
        
    await start_next_song(chat_id, q)

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
    if not call: return False
    
    LOGGER.info(f"🎵 Streaming: {url[:80]}... in {chat_id} (Video: {video})")
    
    if video:
        stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p)
    else:
        stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
        
    try:
        # 60 sec timeout for Video downloads
        await asyncio.wait_for(call.play(chat_id, stream, config=GroupCallConfig(auto_start=True)), timeout=60.0)
        return True
    except Exception as e:
        LOGGER.error(f"❌ PyTgCalls Error: {type(e).__name__} - {e}")
        return False

async def pause_stream(chat_id: int):
    if call: await call.pause(chat_id)
async def resume_stream(chat_id: int):
    if call: await call.resume(chat_id)
async def stop_stream(chat_id: int):
    if call: await call.leave_call(chat_id)
