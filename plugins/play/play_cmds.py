import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped
from utils.extractors import fetch_audio_url
from utils.thumbnail import gen_thumb
from core.call import sunlo_call
from core.player import add_to_queue, CURRENT_TRACK
from core.ffmpeg_filters import get_filter

PLAY_BOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⏸ Pause", callback_data="pause_cb"),
        InlineKeyboardButton("▶️ Resume", callback_data="resume_cb"),
        InlineKeyboardButton("⏭ Skip", callback_data="skip_cb")
    ],
    [
        InlineKeyboardButton("⏹ Stop VC", callback_data="stop_cb"),
        InlineKeyboardButton("🎛 Filters", callback_data="fl_menu") # Naya button
    ]
])

@Client.on_callback_query(filters.regex("^fl_menu$"))
async def fl_menu_cb(client, cq):
    from plugins.play.filters_cmds import FILTER_BOARD
    await cq.message.reply_text("🎛 **Select an Audio Filter:**", reply_markup=FILTER_BOARD)

@Client.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 **Searching & Generating Thumbnail...**")
    
    track_data = await fetch_audio_url(query)
    if not track_data or not track_data["stream_url"]:
        return await status_msg.edit_text("❌ **Song not found or restricted!**")
        
    chat_id = message.chat.id
    title = track_data["title"]
    thumb_path = await gen_thumb(title, track_data["thumbnail"])
    
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
        # Get active filter for this group
        chat_filter = get_filter(chat_id)
        
        await sunlo_call.play(
            chat_id, 
            AudioPiped(track_data["stream_url"], ffmpeg_parameters=chat_filter)
        )
        
        # Current track save karna
        CURRENT_TRACK[chat_id] = track_data
        
        await status_msg.delete()
        await message.reply_photo(
            photo=thumb_path if thumb_path else "https://via.placeholder.com/1280x720.png?text=SunloMusic",
            caption=f"▶️ **Now Playing:**\n🎵 **{title}**\n👤 **Requested by:** {message.from_user.mention}",
            reply_markup=PLAY_BOARD
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to join VC!**\nError: `{e}`")
        
    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)
