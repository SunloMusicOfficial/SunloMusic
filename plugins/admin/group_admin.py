from pyrogram import Client, filters
from pyrogram.types import Message
from utils.decorators import is_admin

@Client.on_message(filters.command(["ban", "mute", "unban", "unmute", "pin", "unpin", "purge"]) & filters.group)
async def group_admin_cmds(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ You need admin rights for this!")
        
    cmd = message.command[0]
    
    if cmd == "purge":
        if not message.reply_to_message: return await message.reply_text("Reply to a message to purge from there.")
        await client.delete_messages(message.chat.id, range(message.reply_to_message.id, message.id))
        return await message.reply_text("✅ Messages Purged!", quote=False)
        
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a user to use this command.")
        
    user_id = message.reply_to_message.from_user.id
    try:
        if cmd == "ban":
            await client.ban_chat_member(message.chat.id, user_id)
            await message.reply_text("🔨 **Banned!**")
        elif cmd == "unban":
            await client.unban_chat_member(message.chat.id, user_id)
            await message.reply_text("🤝 **Unbanned!**")
        elif cmd == "pin":
            await message.reply_to_message.pin()
            await message.reply_text("📌 **Pinned!**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
