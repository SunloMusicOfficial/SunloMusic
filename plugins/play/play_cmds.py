from database.mongodb import db
from config.vars import Config
from utils.fsub import check_fsub
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped
from utils.extractors import fetch_audio_url
from utils.metadata import get_url_metadata
from utils.thumbnail import gen_thumb
from core.call import sunlo_call
from core.player import add_to_queue, CURRENT_TRACK
from core.ffmpeg_filters import get_filter
from database.mongodb import db

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

@Client.on_callback_query(filters.regex("^fl_menu$"))
async def fl_menu_cb(client, cq):
    from plugins.play.filters_cmds import FILTER_BOARD
    await cq.message.reply_text("🎛 **Select an Audio Filter:**", reply_markup=FILTER_BOARD)

@Client.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_command(client: Client, message: Message):
    if await db.is_maintenance() and message.from_user.id != Config.OWNER_ID:
        return await message.reply_text("⚙️ **Bot is under maintenance.** Please try again later.")
    if await db.is_blacklisted(message.from_user.id):
        return await message.reply_text("🚫 **You are blacklisted from using this bot.**")
    from utils.telegram_logger import log_play

    if not await check_fsub(client, message): return
    status_msg = await message.reply_text("🔍 **Processing...**")
    await log_play(client, message, message.text)
    
    # 1. Telegram File Support
    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice):
        await status_msg.edit_text("📥 **Downloading Telegram File...**")
        file_path = await message.reply_to_message.download(file_name="cache/")
        track_data = {
            "title": message.reply_to_message.audio.title if message.reply_to_message.audio else "Voice Note",
            "stream_url": file_path,
            "thumbnail": None,
            "original_url": file_path,
            "requested_by": message.from_user.id
        }
    else:
        # 2. Normal YouTube/Spotify Link Support
        if len(message.command) < 2:
            return await status_msg.edit_text("⚠️ **Usage:**  or reply to an audio file.")
            
        query = message.text.split(None, 1)[1]
        
        if "http" in query and ("spotify.com" in query or "apple.com" in query or "jiosaavn.com" in query):
            await status_msg.edit_text("🔄 **Extracting metadata...**")
            meta_title = await get_url_metadata(query)
            if meta_title: query = meta_title
        
        track_data = await fetch_audio_url(query)
        if not track_data or not track_data["stream_url"]:
            return await status_msg.edit_text("❌ **Song not found!**")
            
        track_data["requested_by"] = message.from_user.id

    chat_id = message.chat.id
    title = track_data["title"]
    thumb_path = await gen_thumb(title, track_data.get("thumbnail")) if track_data.get("thumbnail") else None
    
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
        await sunlo_call.play(
            chat_id, 
            AudioPiped(track_data["stream_url"], ffmpeg_parameters=chat_filter)
        )
        CURRENT_TRACK[chat_id] = track_data
        await db.inc_play_count(message.from_user.id)
        
        await status_msg.delete()
        await message.reply_photo(
            photo=thumb_path if thumb_path else "https://via.placeholder.com/1280x720.png?text=SunloMusic",
            caption=f"▶️ **Now Playing:**\n🎵 **{title}**\n👤 **Requested by:** {message.from_user.mention}",
            reply_markup=PLAY_BOARD
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to join VC!**\nError: `{e}`")
