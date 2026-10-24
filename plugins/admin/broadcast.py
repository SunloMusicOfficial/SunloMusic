import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import AudioPiped
from core.call import sunlo_call
from utils.extractors import fetch_audio_url
from config.vars import Config

@Client.on_message(filters.command("gcastplay") & filters.user(Config.OWNER_ID))
async def gcast_play_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🌐 **Preparing Global Broadcast...**\nFetching track...")
    
    track_data = await fetch_audio_url(query)
    if not track_data:
        return await status_msg.edit_text("❌ Track not found.")
        
    stream_url = track_data["stream_url"]
    title = track_data["title"]
    
    # Active calls nikalna
    active_calls = sunlo_call.active_calls
    if not active_calls:
        return await status_msg.edit_text("⚠️ Bot is not playing in any Voice Chat currently.")
        
    success_count = 0
    await status_msg.edit_text(f"📡 **Broadcasting:** \nTo {len(active_calls)} active Voice Chats...")
    
    for chat_id in active_calls:
        try:
            await sunlo_call.play(chat_id, AudioPiped(stream_url))
            success_count += 1
            # Optional: Send text in that group
            await client.send_message(chat_id, f"📡 **Global Bot Radio Activated**\n🎵 **Master Broadcast:** {title}\n👑 **Initiated by:** Owner")
            await asyncio.sleep(0.5) # Flood wait bachane ke liye
        except Exception as e:
            pass
            
    await status_msg.edit_text(f"✅ **Global Broadcast Successful!**\n🎵 **Track:** {title}\n📡 **Streamed in:** {success_count} groups.")
