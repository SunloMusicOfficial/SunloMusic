import os
import sys
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message
from config.vars import Config
import io

@Client.on_message(filters.command("logs") & filters.user(Config.OWNER_ID))
async def logs_cmd(client: Client, message: Message):
    if os.path.exists("scripts/bot.log"):
        await message.reply_document("scripts/bot.log", caption="🛠 **SunloMusic Server Logs**")
    else:
        await message.reply_text("❌ No log file found.")

@Client.on_message(filters.command("reboot") & filters.user(Config.OWNER_ID))
async def reboot_cmd(client: Client, message: Message):
    await message.reply_text("🔄 **Rebooting SunloMusic Engine...**\nPlease wait 10-15 seconds.")
    os.execl(sys.executable, sys.executable, "-m", "main")

@Client.on_message(filters.command("eval") & filters.user(Config.OWNER_ID))
async def eval_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** ")
        
    code = message.text.split(None, 1)[1]
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    
    try:
        await client.send_message(message.chat.id, f"💻 **Running Code:**\n```python\n{code}\n```")
        exec(f"async def __aexec():\n" + "".join(f"\n {line}" for line in code.split("\n")))
        await locals()["__aexec"]()
    except Exception as e:
        exc = traceback.format_exc()
    
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    evaluation = exc or stderr or stdout or "Success"
    await message.reply_text(f"📤 **Output:**\n```\n{evaluation[:4000]}\n```")
