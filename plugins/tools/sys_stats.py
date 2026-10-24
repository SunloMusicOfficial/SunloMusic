import time
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message
from config.vars import Config

# Bot ka start time record karne ke liye
START_TIME = time.time()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

@Client.on_message(filters.command(["stats", "sysinfo"]))
async def stats_cmd(client: Client, message: Message):
    uptime = get_readable_time((time.time() - START_TIME))
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    
    stats_text = (
        f"📊 **SunloMusic System Stats**\n\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"🖥 **CPU Usage:** `{cpu}%`\n"
        f"💾 **RAM Usage:** `{ram}%`\n"
        f"💿 **Disk Usage:** `{disk}%`\n\n"
        f"👑 **Powered By:** {Config.BOT_NAME} Engine"
    )
    
    await message.reply_text(stats_text)
