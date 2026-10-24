from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongodb import db
from config.vars import Config

@Client.on_message(filters.command("maintenance") & filters.user(Config.OWNER_ID))
async def maintenance_cmd(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.reply_text("⚠️ **Usage:**  or ")
        
    status = message.command[1] == "on"
    await db.set_maintenance(status)
    await message.reply_text(f"⚙️ **Maintenance Mode set to:** {'ON 🔴' if status else 'OFF 🟢'}")

@Client.on_message(filters.command(["blacklist", "unblacklist"]) & filters.user(Config.OWNER_ID))
async def blacklist_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a user's message to blacklist them.")
        
    user_id = message.reply_to_message.from_user.id
    cmd = message.command[0]
    
    if cmd == "blacklist":
        await db.blacklist_user(user_id, True)
        await message.reply_text(f"🚫 **User Blacklisted!** They can no longer use the bot.")
    else:
        await db.blacklist_user(user_id, False)
        await message.reply_text(f"✅ **User Unblacklisted!**")
