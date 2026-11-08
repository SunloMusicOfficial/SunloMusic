# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from SunloMusic.core.config import Config
from SunloMusic.db import db
from SunloMusic.core.logging import logger
import asyncio

async def broadcast_command(client: Client, message: Message):
    if not message.from_user or message.from_user.id != Config.BOT_OWNER_ID:
        return

    if not message.reply_to_message:
        await message.reply_text("Usage: Reply to any message with /broadcast to broadcast it.")
        return

    broadcast_msg = message.reply_to_message

    users = await db.get_all_broadcast_users()
    groups = await db.get_all_broadcast_groups()

    total_targets = len(users) + len(groups)
    status_msg = await message.reply_text(f"Broadcasting to {total_targets} targets...")

    success_count = 0
    failed_count = 0

    for user in users:
        try:
            await broadcast_msg.copy(user['user_id'])
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to broadcast to user {user['user_id']}: {e}")

    for group in groups:
        try:
            await broadcast_msg.copy(group['chat_id'])
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to broadcast to group {group['chat_id']}: {e}")

    await status_msg.edit_text(
        f"Broadcast completed.\n"
        f"Success: {success_count}\n"
        f"Failed: {failed_count}\n"
        f"Total: {total_targets}"
    )

async def auto_broadcast_to_target(client: Client, chat_id: int, message_to_copy: Message):
    if not message_to_copy:
        return

    try:
        await message_to_copy.copy(chat_id)
        logger.info(f"Auto-broadcast sent to {chat_id}")
    except Exception as e:
        logger.error(f"Failed to auto-broadcast to {chat_id}: {e}")

def register_broadcast_handlers(app: Client):
    app.on_message(filters.command("broadcast"))(broadcast_command)
