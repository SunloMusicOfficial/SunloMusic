from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import AudioPiped
from utils.extractors import fetch_audio_url
from core.call import sunlo_call

@Client.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 **Searching for your song...**")
    
    # 1. Get Audio Data
    track_data = await fetch_audio_url(query)
    if not track_data or not track_data["stream_url"]:
        return await status_msg.edit_text("❌ **Song not found or region restricted!**")
        
    chat_id = message.chat.id
    stream_url = track_data["stream_url"]
    title = track_data["title"]
    
    # 2. Play in Voice Chat
    try:
        await sunlo_call.play(
            chat_id,
            AudioPiped(stream_url)
        )
        await status_msg.edit_text(f"▶️ **Started Playing:**\n🎵 **{title}**")
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to join Voice Chat!**\nMake sure I have admin rights and VC is ON.\nError: ")
