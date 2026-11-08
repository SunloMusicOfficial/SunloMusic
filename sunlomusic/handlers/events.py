# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram import Client, filters
from pyrogram.types import Message
from sunlomusic.db import db
from sunlomusic.core.logging import logger
from sunlomusic.utils.monitor import monitor_logger

async def on_bot_added_to_group(client: Client, message: Message):
    if not message.new_chat_members:
        return

    bot_info = await client.get_me()

    for member in message.new_chat_members:
        if member.id == bot_info.id:
            chat_title = message.chat.title or "Unknown Group"
            member_count = await message.chat.get_members_count() if hasattr(message.chat, 'get_members_count') else None

            await db.save_broadcast_group(message.chat.id, chat_title)
            logger.info(f"Bot added to group: {chat_title} (ID: {message.chat.id})")

            await monitor_logger.log_group_added(message.chat.id, chat_title, member_count)

async def on_bot_removed_from_group(client: Client, message: Message):
    if not message.left_chat_member:
        return

    bot_info = await client.get_me()

    if message.left_chat_member.id == bot_info.id:
        chat_title = message.chat.title or "Unknown Group"
        logger.info(f"Bot removed from group: {chat_title} (ID: {message.chat.id})")

        await monitor_logger.log_group_removed(message.chat.id, chat_title)

def register_event_handlers(app: Client):
    app.on_message(filters.new_chat_members)(on_bot_added_to_group)
    app.on_message(filters.left_chat_member)(on_bot_removed_from_group)
