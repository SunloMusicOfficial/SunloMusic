from pyrogram import Client, filters
from pyrogram.types import Message
from core.call import sunlo_call
from utils.decorators import check_strict_mode

@Client.on_message(filters.command(["seek", "fwd", "rwd"]) & filters.group)
async def seek_cmd(client: Client, message: Message):
    if not await check_strict_mode(client, message): return
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:**  (For 10 seconds)")
        
    try:
        duration = int(message.command[1])
        chat_id = message.chat.id
        # Note: Proper seeking requires FFmpeg pipe seeking, this is a basic implementation placeholder
        await message.reply_text(f"⏩ **Seeking stream by {duration} seconds...**")
        # await sunlo_call.seek_stream(chat_id, duration) # Requires PyTgCalls v1.0+ seek support
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
