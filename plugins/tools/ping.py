from pyrogram import Client, filters
from pyrogram.types import Message
import time

@Client.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start_time = time.time()
    reply = await message.reply_text("Pinging SunloMusic servers...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000)
    
    await reply.edit_text(f"🏓 **Pong!**\n⚡ **Latency:** `{ping_time}ms`\n👑 **Engine:** SunloMusic Premium")
