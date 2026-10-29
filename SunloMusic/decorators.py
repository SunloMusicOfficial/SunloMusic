from functools import wraps
from pyrogram import enums
from pyrogram.types import Message, CallbackQuery
from SunloMusic.config import config
from SunloMusic.database import is_sudo, get_chat
from SunloMusic.texts import NO_SUDO_TEXT, NO_ADMIN_TEXT
from SunloMusic.error_handler import log_error_to_group

def catch_errors(func):
    @wraps(func)
    async def wrapper(client, update, *args, **kwargs):
        try: return await func(client, update, *args, **kwargs)
        except Exception as e: await log_error_to_group(update, e)
    return wrapper

def sudo_only(func):
    @wraps(func)
    async def wrapper(client, update, *args, **kwargs):
        user = update.from_user
        if user and (user.id == config.OWNER_ID or user.id in config.sudo_list):
            return await func(client, update, *args, **kwargs)
        if user and await is_sudo(user.id): 
            return await func(client, update, *args, **kwargs)
        
        if isinstance(update, Message): await update.reply_text(NO_SUDO_TEXT)
        elif isinstance(update, CallbackQuery): await update.answer(NO_SUDO_TEXT, show_alert=True)
    return wrapper

def admin_only(func):
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user: return
        
        # ✅ Direct Owner/Sudo check (No DB wait)
        if message.from_user.id == config.OWNER_ID or message.from_user.id in config.sudo_list:
            return await func(client, message, *args, **kwargs)
            
        try:
            if await is_sudo(message.from_user.id): 
                return await func(client, message, *args, **kwargs)
        except: pass
            
        if message.chat.type != enums.ChatType.PRIVATE:
            try:
                member = await message.chat.get_member(message.from_user.id)
                if member.privileges:
                    can_manage = getattr(member.privileges, "can_manage_video_chats", False) or \
                                 getattr(member.privileges, "can_manage_voice_chats", False) or \
                                 member.privileges.can_manage_chat
                    if can_manage: return await func(client, message, *args, **kwargs)
            except Exception: pass
        await message.reply_text(NO_ADMIN_TEXT)
    return wrapper
