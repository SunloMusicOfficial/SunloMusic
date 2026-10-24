import time
from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import db
from config.vars import Config

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

START_TIME = time.time()

@Client.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start = time.time()
    msg = await message.reply_text("🏓 **Pinging...**")
    end = time.time()
    ping_time = round((end - start) * 1000, 2)
    await msg.edit_text(f"🏓 **Pong!**\n⚡ **Latency:** `{ping_time} ms`\n⚙️ **Engine:** SunloMusic Premium")

@Client.on_message(filters.command("stats"))
async def stats_cmd(client: Client, message: Message):
    status = await message.reply_text("📊 **Fetching Global Stats...**")
    
    total_users = await db.users.count_documents({})
    total_groups = await db.groups.count_documents({})
    
    if HAS_PSUTIL:
        cpu = f"{psutil.cpu_percent()}%"
        ram = f"{psutil.virtual_memory().percent}%"
    else:
        cpu = "N/A (Termux)"
        ram = "N/A (Termux)"
    
    uptime_sec = int(time.time() - START_TIME)
    h, rem = divmod(uptime_sec, 3600)
    m, s = divmod(rem, 60)
    uptime = f"{h}h {m}m {s}s"
    
    text = (
        f"📊 **{Config.BOT_NAME} - Global Stats**\n\n"
        f"👥 **Users:** `{total_users}`\n"
        f"🗣 **Groups:** `{total_groups}`\n\n"
        f"💻 **CPU Usage:** `{cpu}`\n"
        f"💾 **RAM Usage:** `{ram}`\n"
        f"⏳ **Uptime:** `{uptime}`"
    )
    await status.edit_text(text)
