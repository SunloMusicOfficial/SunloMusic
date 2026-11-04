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
from SunloMusic.ytdlp import extract_audio, get_autoplay, download_media_file, _convert_media
from SunloMusic.queues import KARAOKE_CHATS, AUTO_DJ_CHATS
from SunloMusic.database import add_recent, get_group_setting
from SunloMusic.lyrics import start_live_karaoke
from richgram import rich_send, rich_edit, rich_esc
from SunloMusic.keyboards import player_buttons

call = None
EMPTY_VC_TIMERS = {}
AUDIO_CONTROLS = {}

def cleanup_file(url: str):
    if url and not url.startswith("http") and os.path.exists(url) and url.endswith(('.mp4', '.webm', '.m4a', '.mp3')):
        try: os.remove(url)
        except: pass

def _build_audio_filters(chat_id: int, effect: str = "none", seek_time: int = 0) -> str | None:
    ctrl = AUDIO_CONTROLS.get(chat_id, {})
    speed = ctrl.get("speed", 1.0)
    volume = ctrl.get("volume", 1.0)
    eq = ctrl.get("eq", "none")
    af_filters = []
    if effect == "bass": af_filters.append("bass=g=10")
    elif effect == "8d": af_filters.append("apulsator=hz=0.1")
    elif effect == "nightcore": af_filters.append("atempo=1.25,asetrate=44100*1.25")
    else:
        if eq != "none":
            eq_map = {"bass": "bass=g=12", "pop": "equalizer=f=1000:width_type=h:width=200:g=5", "rock": "equalizer=f=100:width_type=h:width=200:g=3,equalizer=f=3000:width_type=h:width=200:g=4", "jazz": "equalizer=f=200:width_type=h:width=200:g=2", "vocal": "equalizer=f=2000:width_type=h:width=1000:g=5"}
            if eq in eq_map: af_filters.append(eq_map[eq])
    if speed != 1.0: af_filters.append(f"atempo={speed}")
    if volume != 1.0: af_filters.append(f"volume={volume}")
    params = []
    if seek_time > 0: params.append(f"-ss {seek_time}")
    if af_filters: params.append(f"-af \"{','.join(af_filters)}\"")
    return " ".join(params) if params else None

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
        
        elapsed = int(time.time() - q.start_time - q.total_paused)
        if q.now_playing.duration > 0 and elapsed >= q.now_playing.duration: break
        
        try:
            thumb_url = q.now_playing.thumbnail or "https://i.ibb.co/68xK6Z4/sunlo-premium.jpg"
            b64_title = base64.urlsafe_b64encode(q.now_playing.title.encode()).decode().strip("=")
            title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
            
            card_text = (
                f'<img src="{thumb_url}" style="width: 100%; border-radius: 10px; display: block; margin-bottom: 10px;" />'
                f"<b>🎧🎶 Music Time 🎶🎧</b>\n"
                f"━━━━━━━━━━━━━\n"
                f"🎵 <a href='{title_link}'>{rich_esc(q.now_playing.title)}</a>\n"
                f"━━━━━━━━━━━━━\n"
                f"⏱ Duration: {format_duration(q.now_playing.duration)}\n"
                f"━━━━━━━━━━━━━\n"
                f"🙋‍♂️ Request: <a href='tg://user?id={q.now_playing.requester_id}'>{rich_esc(q.now_playing.requester)}</a>\n"
                f"━━━━━━━━━━━━━"
            )
            buttons = player_buttons(q, elapsed)
            msg = await bot_module.bot.get_messages(chat_id, msg_id)
            await rich_edit(msg, card_text + buttons)
        except Exception as e:
            LOGGER.error(f"Rich Edit Error: {e}")

async def start_next_song(chat_id, q):
    from SunloMusic.queues import Track, clear_queue
    if q.timer_task: q.timer_task.cancel(); q.timer_task = None
    if q.karaoke_task: q.karaoke_task.cancel(); q.karaoke_task = None
    if q.playing_message_id:
        try: await bot_module.bot.delete_messages(chat_id, q.playing_message_id)
        except: pass
        q.playing_message_id = 0
    if q.now_playing: cleanup_file(q.now_playing.url)

    last_video_id = getattr(q.now_playing, "video_id", None) if q.now_playing else None
    q.now_playing = None
    
    # ✅ SHRUTI AUTOPLAY INTEGRATION
    if not q.queue and chat_id in AUTO_DJ_CHATS and last_video_id:
        try:
            LOGGER.info(f"🎵 Fetching Autoplay for {last_video_id}...")
            autoplay_tracks = await get_autoplay(last_video_id)
            if autoplay_tracks:
                track = autoplay_tracks[0]
                info = await extract_audio(f"https://youtube.com/watch?v={track['video_id']}")
                if info:
                    q.queue.append(Track(info["title"], info["url"], info["duration"], info["thumbnail"], "Auto-DJ", 0))
                    # Set video_id for next autoplay loop
                    q.queue[0].video_id = info.get("video_id")
        except Exception as e: 
            LOGGER.error(f"Auto-DJ error: {e}")

    if q.queue:
        nxt = q.queue.pop(0)
        q.now_playing = nxt
        if nxt.message_id:
            try: await bot_module.bot.delete_messages(chat_id, nxt.message_id)
            except: pass
            nxt.message_id = 0

        from SunloMusic.plugins.voice import speak_in_vc
        if await get_group_setting(chat_id, "tts", False):
            await speak_in_vc(chat_id, f"Agla gaana, {nxt.title}")

        await play_stream(chat_id, nxt.url, nxt.video)
        q.start_time = time.time(); q.total_paused = 0; q.paused = False; q.votes = set()
        
        try:
            await add_recent(chat_id, {"title": nxt.title, "url": nxt.url, "duration": nxt.duration, "thumbnail": nxt.thumbnail, "requester": nxt.requester, "requester_id": nxt.requester_id, "video": nxt.video})
        except: pass
        
        thumb_url = nxt.thumbnail or "https://i.ibb.co/68xK6Z4/sunlo-premium.jpg"
        b64_title = base64.urlsafe_b64encode(nxt.title.encode()).decode().strip("=")
        title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
        
        card_text = (
            f'<img src="{thumb_url}" style="width: 100%; border-radius: 10px; display: block; margin-bottom: 10px;" />'
            f"<b>🎧🎶 Music Time 🎶🎧</b>\n"
            f"━━━━━━━━━━━━━\n"
            f"🎵 <a href='{title_link}'>{rich_esc(nxt.title)}</a>\n"
            f"━━━━━━━━━━━━━\n"
            f"⏱ Duration: {format_duration(nxt.duration)}\n"
            f"━━━━━━━━━━━━━\n"
            f"🙋‍♂️ Request: <a href='tg://user?id={nxt.requester_id}'>{rich_esc(nxt.requester)}</a>\n"
            f"━━━━━━━━━━━━━"
        )
        buttons = player_buttons(q, 0)
        try:
            sent_msg = await rich_send(bot_module.bot, chat_id, card_text + buttons)
            q.playing_message_id = sent_msg.id
            try: await sent_msg.pin(disable_notification=True)
            except: pass
            q.timer_task = asyncio.create_task(update_live_timer(chat_id, sent_msg.id))
        except Exception as e:
            LOGGER.error(f"Rich Send Next Error: {e}")

        if chat_id in KARAOKE_CHATS: 
            q.karaoke_task = asyncio.create_task(start_live_karaoke(bot_module.bot, chat_id, nxt.title, nxt.duration, q))
    else:
        if await get_group_setting(chat_id, "tts", False):
            await speak_in_vc(chat_id, "Queue khatam ho gayi hai, main VC se nikal raha hu. Dhanyawad!")
        try:
            if call: await call.leave_call(chat_id)
        except: pass
        clear_queue(chat_id)
        ghost_text = f"👻 <b>G H O S T E D !</b> 👻\n━━━━━━━━━━━━━━━━━━━\n<i>The queue vanished into thin air...</i>\n━━━━━━━━━━━━━━━━━━━\n📭 <b>STATUS:</b> <code>EMPTY</code>\n🚪 <b>ASSISTANT:</b> <i>DISAPPEARED FROM VC</i>\n━━━━━━━━━━━━━━━━━━━"
        try: await bot_module.bot.send_message(chat_id, ghost_text)
        except: pass

async def stream_end_handler(client, update: StreamEnded):
    from SunloMusic.queues import get_queue
    chat_id = update.chat_id
    q = get_queue(chat_id)
    if getattr(q, "is_playing_tts", False):
        q.is_playing_tts = False
        return
    if not q.now_playing: return
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

async def play_stream(chat_id: int, url: str, video: bool = False, effect: str = "none", seek_time: int = 0):
    if not call: return False
    if not url.startswith("http") and not os.path.exists(url):
        LOGGER.error(f"❌ File not found before playing: {url}")
        return False
    if video and (url.endswith('.m4a') or url.endswith('.mp3')): video = False
    ffmpeg_args = _build_audio_filters(chat_id, effect, seek_time)
    if video: stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, ffmpeg_parameters=ffmpeg_args)
    else: stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_args)
    try:
        LOGGER.info(f"🎵 Attempting to play URL directly: {url[:80]}")
        await asyncio.wait_for(call.play(chat_id, stream, config=GroupCallConfig(auto_start=True)), timeout=120.0) 
        return True
    except Exception as e:
        err_str = str(e)
        LOGGER.error(f"Direct Play error: {type(e).__name__} - {err_str}")
        if "INTERDC_X_CALL_ERROR" in err_str or "INTERDC_X_CALL_RICH_ERROR" in err_str:
            LOGGER.info("⚠️ Telegram Server Error (DC). Retrying in 5s...")
            await asyncio.sleep(5)
            try:
                await asyncio.wait_for(call.play(chat_id, stream, config=GroupCallConfig(auto_start=True)), timeout=120.0)
                return True
            except Exception as e2: LOGGER.error(f"Retry failed: {e2}")
        return True

async def pause_stream(chat_id: int):
    if call:
        try: await call.pause(chat_id)
        except: pass

async def resume_stream(chat_id: int):
    if call:
        try: await call.resume(chat_id)
        except: pass

async def stop_stream(chat_id: int):
    if call:
        try: await call.leave_call(chat_id)
        except Exception: pass
