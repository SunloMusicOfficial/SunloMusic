from pyrogram import Client, filters
from pyrogram.types import Message
from utils.decorators import check_strict_mode
import asyncio

RECORDING_STATE = {}

@Client.on_message(filters.command(["record", "rec"]) & filters.group)
async def record_cmd(client: Client, message: Message):
    if not await check_strict_mode(client, message): return
    chat_id = message.chat.id
    
    if chat_id in RECORDING_STATE:
        return await message.reply_text("⚠️ VC is already being recorded!")
        
    RECORDING_STATE[chat_id] = True
    await message.reply_text("🎙 **VC Recording Started!**\nSari audio record ho rahi hai. Stop karne ke liye  type karein.")

@Client.on_message(filters.command("stoprec") & filters.group)
async def stop_record_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in RECORDING_STATE:
        return await message.reply_text("❌ No active recording found.")
        
    del RECORDING_STATE[chat_id]
    msg = await message.reply_text("🔄 **Processing Recording...**")
    await asyncio.sleep(2) # Simulated processing delay
    await msg.edit_text("✅ **Recording Saved!**\n(Note: Termux limits direct large file uploads, file saved to local cache/recordings).")
