import os
import sys
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from config.vars import Config

@Client.on_message(filters.command("update") & filters.user(Config.OWNER_ID))
async def update_cmd(client: Client, message: Message):
    status = await message.reply_text("🔄 **Pulling updates from GitHub...**")
    try:
        # Run git pull
        process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if b"Already up to date." in stdout:
            return await status.edit_text("✅ **Bot is already up to date!**")
            
        await status.edit_text("✅ **Update successfully pulled! Restarting engine...**")
        os.execl(sys.executable, sys.executable, "-m", "main")
    except Exception as e:
        await status.edit_text(f"❌ **Update Failed:** `{e}`")
