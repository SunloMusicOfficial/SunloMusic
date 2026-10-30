import asyncio, time, base64, os, random
import aiohttp
from pyrogram import enums
from pyrogram.types import LinkPreviewOptions
from pyrogram.errors import FloodWait
from pytgcalls import PyTgCalls, filters as fl
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded, GroupCallConfig
import SunloMusic.bot as bot_module
from SunloMusic.logger import LOGGER
from SunloMusic.config import config
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail, get_default_thumb
from SunloMusic.keyboards import player_keyboard
from SunloMusic.ytdlp import extract_audio
from SunloMusic.queues import KARAOKE_CHATS, AUTO_DJ_CHATS
from SunloMusic.lyrics import start_live_karaoke

call = None
EMPTY_VC_TIMERS = {}
AUDIO_CONTROLS = {}

def cleanup_file(url: str):
    if url and os.path.exists(url) and url.endswith(('.mp4', '.webm', '.m4a', '.mp3')):
        try: os.remove(url)
        except: pass

def _build_audio_filters(chat_id: int, effect: str = "none") -> str | None:
    ctrl = AUDIO_CONTROLS.get(chat_id, {})
    speed = ctrl.get("speed", 1.0)
    volume = ctrl.get("volume", 1.0)
    eq = ctrl.get("eq", "none")

    filters = []
    if effect == "bass": filters.append("bass=g=10")
    elif effect == "8d": filters.append("apulsator=hz=0.1")
    elif effect == "nightcore": filters.append("atempo=1.25,asetrate=44100*1.25")
    else:
        if eq != "none":
            eq_map = {
                "bass": "bass=g=12",
                "pop": "equalizer=f=1000:width_type=h:width=200:g=5",
                "rock": "equalizer=f=100:width_type=h:width=200:g=3,equalizer=f=3000:width_type=h:width=200:g=4",
                "jazz": "equalizer=f=200:width_type=h:width=200:g=2,equalizer=f=2000:width_type=h:width=200:g=3",
                "vocal": "equalizer=f=2000:width_type=h:width=1000:g=5",
            }
            if eq in eq_map: filters.append(eq_map[eq])
    
    if speed != 1.0: filters.append(f"atempo={speed}")
    if volume != 1.0: filters.append(f"volume={volume}")
    
    return "-af " + ",".join(filters) if filters else None

async def check_empty_vc(chat_id):
    try:
        members = await bot_module.bot.get_chat_members(chat_id, filter=enums.ChatMembersFilter.VOICE_CHAT)
        humans = [m for m in members if not m.user.is_bot]
        if len(humans) == 0:
            if chat_id not in EMPTY_VC_TIMERS: EMPTY_VC_TIMERS[chat_id] = time.time()
            elif time.time() - EMPTY_VC_TIMERS[chat_id] > 180:
                await bot_module.bot.send_message(chat_id, "💤 <b>No humans in VC for 3 minutes. Leaving...</b>")
                await stop_stream(chat_id)
                from SunloMusic.queues import clear_queue
                clear_queue(chat_id)
                if chat_id in EMPTY_VC_TIMERS: del EMPTY_VC_TIMERS[chat_id]
                return True
        else:
            if chat_id in EMPTY_VC_TIMERS: del EMPTY_VC_TIMERS[chat_id]
    except: pass
    return False

async def update_live_timer(chat_id, msg_id):
    from SunloMusic.queues import get_queue
    while True:
        await asyncio.sleep(5)
        q = get_queue(chat_id)
        if not q.now_playing or q.playing_message_id != msg_id: break
        if q.paused: continue
        if await check_empty_vc(chat_id): break
        
        dur_str = "Live" if q.now_playing.duration <= 0 else format_duration(q.now_playing.duration)
        elapsed = int(time.time() - q.start_time - q.total_paused)
        
        if q.now_playing.duration > 0 and elapsed >= q.now_playing.duration: break
        
        try:
            b64_title = base64.urlsafe_b64encode(q.now_playing.title.encode()).decode().strip("=")
            title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
            caption = f"<b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{q.now_playing.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {dur_str}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={q.now_playing.requester_id}'>{q.now_playing.requester}</a>\n━━━━━━━━━━━━━"
            
            try: 
                await bot_module.bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=caption, reply_markup=player_keyboard(q, elapsed))
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except: 
                try: 
                    await bot_module.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=caption, reply_markup=player_keyboard(q, elapsed), link_preview_options=LinkPreviewOptions(is_disabled=True))
                except: pass
        except: pass

async def delayed_leave(chat_id):
    await asyncio.sleep(60) 
    from SunloMusic.queues import get_queue, clear_queue
    q = get_queue(chat_id)
    if not q.now_playing:
        try:
            if call: await call.leave_call(chat_id)
        except: pass
        clear_queue(chat_id)
        ghost_text = f"👻 <b>G H O S T E D !</b> 👻\n━━━━━━━━━━━━━━━━━━━\n<i>The queue vanished into thin air...</i>\n━━━━━━━━━━━━━━━━━━━\n📭 <b>STATUS:</b> <code>EMPTY</code>\n🚪 <b>ASSISTANT:</b> <i>DISAPPEARED FROM VC</i>\n━━━━━━━━━━━━━━━━━━━"
        try: await bot_module.bot.send_message(chat_id, ghost_text)
        except: pass

async def start_next_song(chat_id, q):
    from SunloMusic.queues import Track
    from SunloMusic.database import add_recent
    if q.timer_task: q.timer_task.cancel(); q.timer_task = None
    if q.karaoke_task: q.karaoke_task.cancel(); q.karaoke_task = None
    if q.playing_message_id:
        try: await bot_module.bot.delete_messages(chat_id, q.playing_message_id)
        except: pass
        q.playing_message_id = 0
    if q.now_playing: cleanup_file(q.now_playing.url)

    q.now_playing = None
    
    if not q.queue and chat_id in AUTO_DJ_CHATS:
        try:
            queries = ["trending hindi songs 2024", "top bollywood hits", "arijit singh best songs", "lofi hindi chill", "punjabi top hits"]
            info = await extract_audio(random.choice(queries))
            if info: q.queue.append(Track(info["title"], info["url"], info["duration"], info["thumbnail"], "Auto-DJ", 0))
        except: pass

    if q.queue:
        nxt = q.queue.pop(0)
        q.now_playing = nxt
        if nxt.message_id:
            try: await bot_module.bot.delete_messages(chat_id, nxt.message_id)
            except: pass
            nxt.message_id = 0

        await play_stream(chat_id, nxt.url, nxt.video)
        q.start_time = time.time(); q.total_paused = 0; q.paused = False; q.votes = set()
        
        try:
            await add_recent(chat_id, {"title": nxt.title, "url": nxt.url, "duration": nxt.duration, "thumbnail": nxt.thumbnail, "requester": nxt.requester, "requester_id": nxt.requester_id, "video": nxt.video})
        except: pass
        
        thumb = await generate_thumbnail(chat_id, nxt.thumbnail, nxt.title, format_duration(nxt.duration), nxt.requester)
        dur_str = format_duration(nxt.duration) if nxt.duration > 0 else "Live"
        b64_title = base64.urlsafe_b64encode(nxt.title.encode()).decode().strip("=")
        title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
        caption = f"<b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{nxt.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {dur_str}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={nxt.requester_id}'>{nxt.requester}</a>\n━━━━━━━━━━━━━"
        
        sent_msg = None
        if thumb:
            try: sent_msg = await bot_module.bot.send_photo(chat_id, thumb, caption=caption, reply_markup=player_keyboard(q, 0))
            except Exception: pass
            
        if not sent_msg:
            local_thumb = get_default_thumb()
            if local_thumb:
                try: sent_msg = await bot_module.bot.send_photo(chat_id, local_thumb, caption=caption, reply_markup=player_keyboard(q, 0))
                except Exception: pass
                
        if not sent_msg:
            sent_msg = await bot_module.bot.send_message(chat_id, caption, reply_markup=player_keyboard(q, 0), link_preview_options=LinkPreviewOptions(is_disabled=True))
            
        q.playing_message_id = sent_msg.id
        try: await sent_msg.pin(disable_notification=True)
        except: pass
        q.timer_task = asyncio.create_task(update_live_timer(chat_id, sent_msg.id))
        if chat_id in KARAOKE_CHATS: q.karaoke_task = asyncio.create_task(start_live_karaoke(bot_module.bot, chat_id, nxt.title, nxt.duration, q))
    else:
        asyncio.create_task(delayed_leave(chat_id))

async def stream_end_handler(client, update: StreamEnded):
    from SunloMusic.queues import get_queue
    chat_id = update.chat_id
    q = get_queue(chat_id)
    if q.loop == 1 and q.now_playing:
        await play_stream(chat_id, q.now_playing.url, q.now_playing.video)
        q.start_time = time.time(); q.total_paused = 0; q.paused = False
        return
    if q.loop == 2 and q.now_playing: q.queue.append(q.now_playing)
    await start_next_song(chat_id, q)

def init_calls():
    global call
    if bot_module.assistant:
        call = PyTgCalls(bot_module.assistant, cache_duration=100)
        call.on_update(fl.stream_end())(stream_end_handler)

async def start_call():
    if call: await call.start()

async def play_stream(chat_id: int, url: str, video: bool = False, effect: str = "none"):
    if not call: return False
    if video and (url.endswith('.m4a') or url.endswith('.mp3')): video = False
    
    ffmpeg_args = _build_audio_filters(chat_id, effect)
    
    if video: stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, ffmpeg_parameters=ffmpeg_args)
    else: stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_args)
    
    try:
        LOGGER.info(f"🎵 Attempting to play URL directly: {url[:80]}")
        await asyncio.wait_for(call.play(chat_id, stream, config=GroupCallConfig(auto_start=True)), timeout=20.0)
        return True
    except Exception as e:
        # ✅ Log the error properly
        LOGGER.error(f"Direct Play error: {type(e).__name__} - {str(e)}")
        
        if "http" in url:
            LOGGER.info("⚠️ Direct link failed! Attempting local download fallback...")
            try:
                os.makedirs("cache/downloads", exist_ok=True)
                file_path = f"cache/downloads/{abs(hash(url))}.m4a"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            with open(file_path, "wb") as f: f.write(await resp.read())
                                
                if os.path.exists(file_path):
                    if video: stream2 = MediaStream(media_path=file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720P, ffmpeg_parameters=ffmpeg_args)
                    else: stream2 = MediaStream(media_path=file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_args)
                    
                    await asyncio.wait_for(call.play(chat_id, stream2, config=GroupCallConfig(auto_start=True)), timeout=30.0)
                    return True
            except Exception as download_err:
                LOGGER.error(f"Download fallback failed: {download_err}")
                
        return True

async def pause_stream(chat_id: int):
    if call: await call.pause(chat_id)
async def resume_stream(chat_id: int):
    if call: await call.resume(chat_id)
async def stop_stream(chat_id: int):
    if call: await call.leave_call(chat_id)
