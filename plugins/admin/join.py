from pyrogram import Client, filters
from pyrogram.types import Message
from utils.decorators import is_admin
from core.call import sunlo_call

@Client.on_message(filters.command(["join", "userbotjoin"]) & filters.group)
async def join_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only admins can invite the assistant!")
        
    status = await message.reply_text("🔄 **Inviting Assistant to the group...**")
    try:
        # Assuming Assistant is initialized inside sunlo_call
        assistant = sunlo_call._app 
        chat = await client.get_chat(message.chat.id)
        
        if chat.username:
            await assistant.join_chat(chat.username)
        else:
            invite_link = await client.export_chat_invite_link(message.chat.id)
            await assistant.join_chat(invite_link)
            
        await status.edit_text("✅ **Assistant successfully joined the group!**")
    except Exception as e:
        await status.edit_text(f"❌ Failed to join: {e}\nTry adding the assistant manually.")
