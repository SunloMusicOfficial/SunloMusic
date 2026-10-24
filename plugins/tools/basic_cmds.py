import os, sys
from pyrogram import Client, filters
from pyrogram.types import Message
from config.vars import Config

@Client.on_message(filters.command("id"))
async def id_cmd(client: Client, message: Message):
    text = f"👤 **User ID:** `{message.from_user.id}`\n"
    if message.chat.type.name != "PRIVATE":
        text += f"🗣 **Group ID:** `{message.chat.id}`"
    if message.reply_to_message:
        text += f"\n🎯 **Replied User ID:** `{message.reply_to_message.from_user.id}`"
    await message.reply_text(text)

@Client.on_message(filters.command(["reboot", "restart"]) & filters.user(Config.OWNER_ID))
async def reboot_cmd(client: Client, message: Message):
    await message.reply_text("🔄 **Rebooting System... Please wait 5-10 seconds.**")
    os.execl(sys.executable, sys.executable, "-m", "main")
