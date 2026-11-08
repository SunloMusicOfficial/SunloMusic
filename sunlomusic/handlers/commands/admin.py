# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import os
import sys

from pyrogram import Client
from pyrogram.types import Message

from sunlomusic.db import db
from sunlomusic.core.config import Config
from sunlomusic.core.logging import logger
from sunlomusic.ui.keyboards import keyboards
from sunlomusic.ui.messages import messages
from sunlomusic.utils.rich import reply_welcome, reply_help


async def start_command(client: Client, message: Message):
    from pyrogram.enums import ChatType

    if message.chat.type == ChatType.PRIVATE and message.from_user:
        user_name = message.from_user.first_name or "Unknown"
        username = message.from_user.username
        await db.save_broadcast_user(message.from_user.id, user_name, username)
        logger.info(f"User {user_name} (ID: {message.from_user.id}) started the bot")

    me = await client.get_me()
    markup = keyboards.start_menu(me.username)
    if not await reply_welcome(message, markup):
        await message.reply_text(messages.start_welcome(), reply_markup=markup)


async def help_command(client: Client, message: Message):
    markup = keyboards.help_menu()
    if not await reply_help(message, markup):
        await message.reply_text(messages.help_message(), reply_markup=markup)


def read_log_tail(max_lines: int = 50, max_chars: int = 3900) -> str:
    log_path = os.path.join(Config.LOGS_DIR, "bot.log")
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
    except Exception:
        return "❌ Failed to read the log file."
    if not lines:
        return "📄 Log file is empty."
    return "".join(lines[-max_lines:])[:max_chars]


async def logs_command(client: Client, message: Message):
    if not message.from_user:
        return

    if message.from_user.id != Config.BOT_OWNER_ID:
        await message.reply_text("❌ **Only the bot owner can view the logs.**")
        return

    log_path = os.path.join(Config.LOGS_DIR, "bot.log")
    try:
        await message.reply_document(
            log_path,
            caption="📄 Bot Logs",
            reply_markup=keyboards.logs_menu()
        )
    except Exception as e:
        logger.error(f"Error sending logs: {e}")
        await message.reply_text(messages.error("Failed to send the log file"))


async def restart_command(client: Client, message: Message):
    if not message.from_user:
        return

    if message.from_user.id != Config.BOT_OWNER_ID:
        await message.reply_text("❌ **Only the bot owner can restart the bot.**")
        return

    status_msg = await message.reply_text("🔄 **Restarting bot...**")
    logger.info(f"Bot restart initiated by owner (ID: {message.from_user.id})")

    try:
        await status_msg.edit_text("✅ **Bot is restarting. Please wait...**")

        import json
        restart_info = {
            'chat_id': status_msg.chat.id,
            'message_id': status_msg.id
        }
        with open('.restart_info.json', 'w') as f:
            json.dump(restart_info, f)

        import bot as bot_module
        if hasattr(bot_module, 'music_bot') and bot_module.music_bot:
            await bot_module.music_bot.stop()

        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logger.error(f"Error during restart: {e}")
        await status_msg.edit_text(f"❌ **Restart failed: {str(e)}**")


async def status_command(client: Client, message: Message, player):
    try:
        total_users = len(await db.get_all_broadcast_users())
        total_groups = len(await db.get_all_broadcast_groups())
        total_songs = await db.get_total_songs_played()

        active_vcs = 0
        ping = None
        cpu_usage = None
        if player and player.tgcalls:
            active_vcs = sum(1 for chat_id in player.tgcalls.streams.keys()
                           if player.tgcalls.streams[chat_id].get("playing", False))
            try:
                ping = await player.tgcalls.get_ping()
                cpu_usage = await player.tgcalls.get_cpu_usage()
            except Exception as diag_err:
                logger.warning(f"Could not read voice-engine diagnostics: {diag_err}")

        status_text = messages.status_message(total_users, total_groups, total_songs, active_vcs, ping, cpu_usage)
        await message.reply_text(status_text)
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await message.reply_text(messages.error("Failed to retrieve bot status"))
