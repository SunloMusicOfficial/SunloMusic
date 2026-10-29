import asyncio, time, base64, os
from pyrogram import enums
from pyrogram.types import LinkPreviewOptions
from pyrogram.errors import FloodWait
from pytgcalls import PyTgCalls, filters as fl
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded, GroupCallConfig
import SunloMusic.bot as bot_module
from SunloMusic.logger import LOGGER
from SunloMusic.config import config
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail
from SunloMusic.keyboards import player_keyboard
from SunloMusic.ytdlp import extract_audio
from SunloMusic.queues import KARAOKE_CHATS
from SunloMusic.lyrics import start_live_karaoke

call = None
AUTO_DJ_CHATS = set()
EMPTY_VC_TIMERS = {}

def cleanup_file(url: str):
    if url and os.path.exists(url) and url.endswith(('.mp4', '.webm', '.m4a')):
        try: os.remove(url)
        except: pass

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
        
        if q.now_playing.duration <= 0: dur_str = "Live"
        else: dur_str = format_duration(q.now_playing.duration)
            
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
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except: pass
        except: pass

async def start_next_song(chat_id, q):
    from SunloMusic.queues import clear_queue, Track
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
            info = await extract_audio("trending hindi songs 2024")
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
        
        thumb = await generate_thumbnail(chat_id, nxt.thumbnail, nxt.title, format_duration(nxt.duration), nxt.requester)
        dur_str = format_duration(nxt.duration) if nxt.duration > 0 else "Live"
        b64_title = base64.urlsafe_b64encode(nxt.title.encode()).decode().strip("=")
        title_link = f"https://t.me/{config.BOT_USERNAME.strip('@')}?start=dl_{b64_title}"
        caption = f"<b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href='{title_link}'>{nxt.title}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {dur_str}\n━━━━━━━━━━━━━\n🙋‍♂️ Request: <a href='tg://user?id={nxt.requester_id}'>{nxt.requester}</a>\n━━━━━━━━━━━━━"
        
        if thumb: sent_msg = await bot_module.bot.send_photo(chat_id, thumb, caption=caption, reply_markup=player_keyboard(q, 0))
        else: sent_msg = await bot_module.bot.send_message(chat_id, caption, reply_markup=player_keyboard(q, 0), link_preview_options=LinkPreviewOptions(is_disabled=True))
        
        q.playing_message_id = sent_msg.id
        q.timer_task = asyncio.create_task(update_live_timer(chat_id, sent_msg.id))

        if chat_id in KARAOKE_CHATS:
            q.karaoke_task = asyncio.create_task(start_live_karaoke(bot_module.bot, chat_id, nxt.title, nxt.duration, q))
    else:
        try:
            if call: await call.leave_call(chat_id)
        except: pass
        clear_queue(chat_id)
        ghost_text = f"👻 <b>G H O S T E D !</b> 👻\n━━━━━━━━━━━━━━━━━━━\n<i>The queue vanished into thin air...</i>\n━━━━━━━━━━━━━━━━━━━\n📭 <b>STATUS:</b> <code>EMPTY</code>\n🚪 <b>ASSISTANT:</b> <i>DISAPPEARED FROM VC</i>\n━━━━━━━━━━━━━━━━━━━\n<blockquote>Boo! Hope you enjoyed the vibes. 👻</blockquote>"
        try: await bot_module.bot.send_message(chat_id, ghost_text)
        except: pass

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
    if call:
        await call.start()

async def play_stream(chat_id: int, url: str, video: bool = False, effect: str = "none"):
    if not call: return False
    if video and (url.endswith('.m4a') or url.endswith('.mp3')): video = False
    ffmpeg_args = "-af bass=g=10" if effect == "bass" else "-af apulsator=hz=0.1" if effect == "8d" else "-af atempo=1.25,asetrate=44100*1.25" if effect == "nightcore" else None
    if video: stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, ffmpeg_parameters=ffmpeg_args)
    else: stream = MediaStream(media_path=url, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_args)
    try:
        await asyncio.wait_for(call.play(chat_id, stream, config=GroupCallConfig(auto_start=True)), timeout=30.0)
        return True
    except Exception as e:
        if "already" in str(e).lower() or "stream" in str(e).lower(): return True
        return True

async def pause_stream(chat_id: int):
    if call: await call.pause(chat_id)
async def resume_stream(chat_id: int):
    if call: await call.resume(chat_id)
async def stop_stream(chat_id: int):
    if call: await call.leave_call(chat_id)
