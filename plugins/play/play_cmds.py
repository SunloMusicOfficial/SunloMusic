from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import AudioPiped
from utils.extractors import fetch_audio_url
from core.call import sunlo_call
from core.player import add_to_queue

@Client.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 **Searching for your song...**")
    
    track_data = await fetch_audio_url(query)
    if not track_data or not track_data["stream_url"]:
        return await status_msg.edit_text("❌ **Song not found or region restricted!**")
        
    chat_id = message.chat.id
    
    # Check if bot is already playing in the call
    try:
        active_call = await sunlo_call.get_call(chat_id)
        if active_call:
            position = add_to_queue(chat_id, track_data)
            return await status_msg.edit_text(f"📝 **Added to Queue at position #{position}**\n🎵 **{track_data['title']}**")
    except:
        pass # Bot call me nahi hai, direct play karega
    
    try:
        await sunlo_call.play(
            chat_id,
            AudioPiped(track_data["stream_url"])
        )
        await status_msg.edit_text(f"▶️ **Started Playing:**\n🎵 **{track_data['title']}**")
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to join Voice Chat!**\nMake sure VC is ON.\nError: `{e}`")
