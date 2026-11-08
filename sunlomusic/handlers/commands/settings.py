# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram import Client
from pyrogram.types import Message

from SunloMusic.db import db
from SunloMusic.utils.permissions import permission_checker
from SunloMusic.ui.keyboards import keyboards
from SunloMusic.ui.messages import messages
from SunloMusic.utils.rich import reply_settings
from SunloMusic.core.logging import logger


async def settings_command(client: Client, message: Message):
    from pyrogram.enums import ChatType

    if message.chat.type == ChatType.PRIVATE:
        me = await client.get_me()
        await message.reply_text(
            messages.dm_not_allowed(),
            reply_markup=keyboards.start_menu(me.username)
        )
        return

    settings = await db.get_chat_settings(message.chat.id)
    markup = keyboards.settings_menu(message.chat.id, settings)
    if not await reply_settings(message, markup):
        await message.reply_text(messages.settings_info(settings), reply_markup=markup)


async def vcadmin_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_admin = await permission_checker.is_admin(client, message.chat.id, message.from_user.id)
    if not is_admin:
        await message.reply_text("❌ **Only group admins can grant VC admin permissions.**")
        return

    target_user = None
    target_user_id = None
    target_user_name = "Unknown"

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
        target_user_id = target_user.id
        target_user_name = target_user.first_name or "Unknown"
    else:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("❌ **Usage:**\n• Reply to a user with /vcadmin\n• /vcadmin @username\n• /vcadmin <user_id>")
            return

        identifier = args[1]
        if identifier.startswith("@"):
            username = identifier[1:]
            try:
                target_user = await client.get_users(username)
                target_user_id = target_user.id
                target_user_name = target_user.first_name or username
            except:
                await message.reply_text(f"❌ **User @{username} not found.**")
                return
        else:
            try:
                target_user_id = int(identifier)
                try:
                    target_user = await client.get_users(target_user_id)
                    target_user_name = target_user.first_name or "Unknown"
                except:
                    target_user_name = f"User {target_user_id}"
            except ValueError:
                await message.reply_text("❌ **Invalid user ID. Please use a valid numeric ID.**")
                return

    if target_user_id:
        await db.add_vc_admin(message.chat.id, target_user_id, target_user_name)
        await message.reply_text(f"✅ **{target_user_name} now has voice chat control permissions.**")
        logger.info(f"VC Admin granted: User {target_user_name} (ID: {target_user_id}) in chat {message.chat.id}")


async def vcunadmin_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_admin = await permission_checker.is_admin(client, message.chat.id, message.from_user.id)
    if not is_admin:
        await message.reply_text("❌ **Only group admins can revoke VC admin permissions.**")
        return

    target_user = None
    target_user_id = None
    target_user_name = "Unknown"

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
        target_user_id = target_user.id
        target_user_name = target_user.first_name or "Unknown"
    else:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("❌ **Usage:**\n• Reply to a user with /vcunadmin\n• /vcunadmin @username\n• /vcunadmin <user_id>")
            return

        identifier = args[1]
        if identifier.startswith("@"):
            username = identifier[1:]
            try:
                target_user = await client.get_users(username)
                target_user_id = target_user.id
                target_user_name = target_user.first_name or username
            except:
                await message.reply_text(f"❌ **User @{username} not found.**")
                return
        else:
            try:
                target_user_id = int(identifier)
                try:
                    target_user = await client.get_users(target_user_id)
                    target_user_name = target_user.first_name or "Unknown"
                except:
                    target_user_name = f"User {target_user_id}"
            except ValueError:
                await message.reply_text("❌ **Invalid user ID. Please use a valid numeric ID.**")
                return

    if target_user_id:
        await db.remove_vc_admin(message.chat.id, target_user_id)
        await message.reply_text(f"✅ **Voice chat permissions removed from {target_user_name}.**")
        logger.info(f"VC Admin revoked: User {target_user_name} (ID: {target_user_id}) in chat {message.chat.id}")
