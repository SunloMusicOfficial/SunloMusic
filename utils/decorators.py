from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, CallbackQuery
from database.mongodb import db

async def is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def check_strict_mode(client, update) -> bool:
    # update can be Message or CallbackQuery
    chat_id = update.message.chat.id if isinstance(update, CallbackQuery) else update.chat.id
    user_id = update.from_user.id
    
    group_data = await db.get_group(chat_id)
    if group_data.get("strict_mode", False):
        admin_status = await is_admin(client, chat_id, user_id)
        if not admin_status:
            msg = "❌ **Strict Mode ON:** Only Admins can control the music!"
            if isinstance(update, CallbackQuery):
                await update.answer(msg, show_alert=True)
            else:
                await update.reply_text(msg)
            return False
    return True
