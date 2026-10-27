from functools import wraps
from pyrogram.types import Message, CallbackQuery
from SunloMusic.database import is_sudo, get_chat
from SunloMusic.texts import NO_SUDO_TEXT, NO_ADMIN_TEXT, NO_AUTH_TEXT

def sudo_only(func):
    @wraps(func)
    async def wrapper(client, update, *args, **kwargs):
        user = update.from_user
        if user and await is_sudo(user.id): return await func(client, update, *args, **kwargs)
        if isinstance(update, Message): await update.reply_text(NO_SUDO_TEXT)
        elif isinstance(update, CallbackQuery): await update.answer(NO_SUDO_TEXT, show_alert=True)
    return wrapper

def admin_only(func):
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if message.chat.type.name not in ("PRIVATE",):
            member = await message.chat.get_member(message.from_user.id)
            if member.privileges and (member.privileges.can_manage_voice_chats or member.privileges.can_manage_chat):
                return await func(client, message, *args, **kwargs)
            elif await is_sudo(message.from_user.id):
                return await func(client, message, *args, **kwargs)
        await message.reply_text(NO_ADMIN_TEXT)
    return wrapper

def auth_required(func):
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        chat = await get_chat(message.chat.id)
        if chat.get("auth") or await is_sudo(message.from_user.id):
            return await func(client, message, *args, **kwargs)
        await message.reply_text(NO_AUTH_TEXT)
    return wrapper
