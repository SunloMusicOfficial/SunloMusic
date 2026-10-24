import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from core.call import sunlo_call
from core.player import clear_queue
from utils.decorators import check_strict_mode

ACTIVE_TIMERS = {}

@Client.on_message(filters.command(["sleep", "sleeptimer"]) & filters.group)
async def sleep_timer_cmd(client: Client, message: Message):
    if not await check_strict_mode(client, message): return
    
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** \nExample:  to stop music after 30 mins.")
        
    try:
        minutes = int(message.command[1])
        if minutes < 1 or minutes > 300:
            return await message.reply_text("❌ Please set a timer between 1 and 300 minutes.")
            
        seconds = minutes * 60
        
        # Agar pehle se koi timer hai toh usko cancel karo
        if chat_id in ACTIVE_TIMERS:
            ACTIVE_TIMERS[chat_id].cancel()
            
        await message.reply_text(f"🌙 **Sleep Timer Set!**\nMusic will automatically stop and bot will leave VC in **{minutes} minutes**.")
        
        # Background task banana timer ke liye
        timer_task = asyncio.create_task(run_sleep_timer(chat_id, seconds, client))
        ACTIVE_TIMERS[chat_id] = timer_task
        
    except ValueError:
        await message.reply_text("❌ Please enter a valid number of minutes.")

async def run_sleep_timer(chat_id: int, seconds: int, client: Client):
    try:
        await asyncio.sleep(seconds)
        # Time khatam hone par
        try:
            await sunlo_call.leave_call(chat_id)
            clear_queue(chat_id)
            await client.send_message(chat_id, "😴 **Sleep Timer Ended!**\nMusic has been stopped and bot has left the VC. Goodnight! 🌙")
        except:
            pass
        if chat_id in ACTIVE_TIMERS:
            del ACTIVE_TIMERS[chat_id]
    except asyncio.CancelledError:
        pass # Agar kisine beech me timer cancel kar diya
