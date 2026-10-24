import os
from pytgcalls import PyTgCalls
from pytgcalls.types import Update, AudioPiped
from core.bot import SunloBot
from core.player import get_next_track, clear_queue, CURRENT_TRACK, is_autoplay_enabled
from core.ffmpeg_filters import get_filter
from utils.extractors import fetch_related_track
from utils.thumbnail import gen_thumb
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
    chat_filter = get_filter(chat_id)
    
    if next_track:
        # 1. Play next track from queue
        try:
            await client.play(chat_id, AudioPiped(next_track["stream_url"], ffmpeg_parameters=chat_filter))
            CURRENT_TRACK[chat_id] = next_track
            await send_now_playing(chat_id, next_track, "⏭ **Next in Queue:**")
        except Exception as e:
            LOGGER.error(f"Queue play error: {e}")
            
    elif is_autoplay_enabled(chat_id) and chat_id in CURRENT_TRACK:
        # 2. Trigger AI Auto-Play
        last_track_title = CURRENT_TRACK[chat_id]["title"]
        auto_track = await fetch_related_track(last_track_title)
        
        if auto_track:
            try:
                await client.play(chat_id, AudioPiped(auto_track["stream_url"], ffmpeg_parameters=chat_filter))
                CURRENT_TRACK[chat_id] = auto_track
                await send_now_playing(chat_id, auto_track, "🤖 **Auto-Play Triggered:**")
            except Exception as e:
                LOGGER.error(f"Auto-play error: {e}")
        else:
            await client.leave_call(chat_id)
            clear_queue(chat_id)
    else:
        # 3. Queue khali aur Auto-Play OFF
        await client.leave_call(chat_id)
        clear_queue(chat_id)

async def send_now_playing(chat_id: int, track_data: dict, prefix: str):
    try:
        from plugins.play.play_cmds import PLAY_BOARD
        thumb_path = await gen_thumb(track_data["title"], track_data["thumbnail"])
        caption = f"{prefix}\n🎵 **{track_data['title']}**\n💡 **Powered by:** SunloMusic Premium"
        
        await sunlo_call._app.send_photo(
            chat_id=chat_id,
            photo=thumb_path if thumb_path else "https://via.placeholder.com/1280x720.png?text=SunloMusic",
            caption=caption,
            reply_markup=PLAY_BOARD
        )
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
    except Exception as e:
        LOGGER.error(f"Failed to send playing message: {e}")
