from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import AudioPiped
from utils.extractors import fetch_audio_url
from core.call import sunlo_call

@Client.on_message(filters.command("cplay") & filters.group)
async def cplay_cmd(client: Client, message: Message):
    if not message.chat.type.name in ["CHANNEL", "SUPERGROUP"]:
        return await message.reply_text("⚠️ This command is for Channels!")
        
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:**  (Link channel to a group to type this)")
        
    query = message.text.split(None, 1)[1]
    status = await message.reply_text("🔍 **Searching for Channel Stream...**")
    
    track = await fetch_audio_url(query)
    if not track: return await status.edit_text("❌ Song not found!")
    
    try:
        # Assuming message is sent in discussion group linked to channel
        channel_id = message.chat.id # Needs proper channel ID extraction in production
        await sunlo_call.play(channel_id, AudioPiped(track["stream_url"]))
        await status.edit_text(f"▶️ **Started Playing in Channel:**\n🎵 **{track['title']}**")
    except Exception as e:
        await status.edit_text(f"❌ Error playing in channel: {e}")
