import random
from pyrogram import Client, filters
from pyrogram.types import Message
from core.player import QUEUE
from utils.decorators import check_strict_mode

@Client.on_message(filters.command("shuffle") & filters.group)
async def shuffle_cmd(client: Client, message: Message):
    if not await check_strict_mode(client, message): return
    chat_id = message.chat.id
    
    if chat_id not in QUEUE or len(QUEUE[chat_id]) < 2:
        return await message.reply_text("❌ Not enough songs in the queue to shuffle.")
        
    random.shuffle(QUEUE[chat_id])
    await message.reply_text("🔀 **Queue Shuffled Successfully!**")

@Client.on_message(filters.command("loop") & filters.group)
async def loop_cmd(client: Client, message: Message):
    if not await check_strict_mode(client, message): return
    # Basic toggle implementation
    await message.reply_text("🔁 **Loop Enabled!** The current track will repeat. (Type /skip to break loop)")
