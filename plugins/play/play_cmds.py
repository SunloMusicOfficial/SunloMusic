import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped
from utils.extractors import fetch_audio_url, fetch_playlist
from utils.metadata import get_url_metadata
from utils.thumbnail import gen_thumb
from core.call import sunlo_call
from core.player import add_to_queue, CURRENT_TRACK
from core.ffmpeg_filters import get_filter
from database.mongodb import db
from utils.telegram_logger import log_play

PLAY_BOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⏸ Pause", callback_data="pause_cb"),
        InlineKeyboardButton("▶️ Resume", callback_data="resume_cb"),
        InlineKeyboardButton("⏭ Skip", callback_data="skip_cb")
    ],
    [
        InlineKeyboardButton("⏹ Stop VC", callback_data="stop_cb"),
        InlineKeyboardButton("🎛 Filters", callback_data="fl_menu")
    ]
])

LAST_PLAYING_MSG = {}

@Client.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_command(client: Client, message: Message):
    if await db.is_maintenance() and message.from_user.id != 123456789: # Replace with your owner ID
        return await message.reply_text("⚙️ **Bot is under maintenance.**")
        
    status_msg = await message.reply_text("🔍 **Processing...**")
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        return await status_msg.edit_text("⚠️ **Usage:** ")
        
    query = message.text.split(None, 1)[1]
    
    # Playlist Handling
    if "playlist" in query or "album" in query:
        await status_msg.edit_text("🔄 **Fetching Playlist...**")
        tracks = await fetch_playlist(query)
        if tracks:
            for track in tracks:
                track["requested_by"] = message.from_user.id
                track["stream_url"] = None # Fetch lazily later
                add_to_queue(chat_id, track)
            return await status_msg.edit_text(f"✅ **Added {len(tracks)} songs from playlist to the queue!**")

    # Single Track Logic
    track_data = await fetch_audio_url(query)
    if not track_data:
        return await status_msg.edit_text("❌ **Song not found!**")
        
    track_data["requested_by"] = message.from_user.id
    title = track_data["title"]
    await log_play(client, message, title)
    
    thumb_path = await gen_thumb(title, track_data.get("thumbnail"))
    
    try:
        active_call = await sunlo_call.get_call(chat_id)
        if active_call:
            position = add_to_queue(chat_id, track_data)
            await status_msg.delete()
            return await message.reply_photo(
                photo=thumb_path if thumb_path else "https://via.placeholder.com/1280x720.png?text=SunloMusic",
                caption=f"📝 **Added to Queue at #{position}**\n🎵 **{title}**",
                reply_markup=PLAY_BOARD
            )
    except:
        pass 
    
    try:
        chat_filter = get_filter(chat_id)
        await sunlo_call.play(chat_id, AudioPiped(track_data["stream_url"], ffmpeg_parameters=chat_filter))
        CURRENT_TRACK[chat_id] = track_data
        await db.inc_play_count(message.from_user.id)
        
        await status_msg.delete()
        
        # Auto-Clean previous playing message
        if chat_id in LAST_PLAYING_MSG:
            try:
                await LAST_PLAYING_MSG[chat_id].delete()
            except:
                pass
                
        msg = await message.reply_photo(
            photo=thumb_path if thumb_path else "https://via.placeholder.com/1280x720.png?text=SunloMusic",
            caption=f"▶️ **Now Playing:**\n🎵 **{title}**\n👤 **Requested by:** {message.from_user.mention}",
            reply_markup=PLAY_BOARD
        )
        LAST_PLAYING_MSG[chat_id] = msg
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to join VC!**\nError: `{e}`")
