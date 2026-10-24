from pyrogram import Client, filters
from pyrogram.types import Message
from core.call import sunlo_call
from utils.decorators import check_strict_mode

@Client.on_message(filters.command(["vol", "volume"]) & filters.group)
async def volume_cmd(client: Client, message: Message):
    if not await check_strict_mode(client, message): return
    
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    try:
        vol = int(message.command[1])
        if vol < 1 or vol > 200:
            return await message.reply_text("❌ Volume must be between 1 and 200.")
            
        chat_id = message.chat.id
        await sunlo_call.change_volume_call(chat_id, vol)
        
        # Volume progress bar generator (UI)
        filled = round(vol / 20)
        empty = 10 - filled
        bar = "▬" * filled + "🔘" + "▭" * empty
        
        await message.reply_text(f"🔊 **Volume Adjusted to {vol}%**\n{bar}")
        
    except ValueError:
        await message.reply_text("❌ Please enter a valid number.")
    except Exception as e:
        await message.reply_text("❌ **Nothing is playing to adjust volume.**")
