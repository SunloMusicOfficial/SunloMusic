# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram.types import InlineKeyboardMarkup, Message

from sunlomusic.core.logging import logger
from sunlomusic.ui.messages import messages


async def _reply(message: Message, variants, reply_markup: InlineKeyboardMarkup, label: str) -> bool:
    for rich in variants:
        try:
            await message.reply_rich(rich, reply_markup=reply_markup)
            return True
        except Exception as e:
            logger.warning(f"Rich {label} reply failed in {message.chat.id}: {e}")
    return False


async def _edit(message: Message, variants, reply_markup: InlineKeyboardMarkup, label: str) -> bool:
    for rich in variants:
        try:
            await message.edit_text(rich_message=rich, reply_markup=reply_markup)
            return True
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                return True
            logger.warning(f"Rich {label} edit failed in {message.chat.id}: {e}")
    return False


def _welcome_variants():
    # custom emoji first, then plain emoji in case Telegram refuses them
    return (messages.start_welcome_rich(True), messages.start_welcome_rich(False))


async def reply_welcome(message: Message, reply_markup: InlineKeyboardMarkup) -> bool:
    """Reply with the rich welcome message. False means the caller should send plain text."""
    return await _reply(message, _welcome_variants(), reply_markup, "welcome")


async def edit_to_welcome(message: Message, reply_markup: InlineKeyboardMarkup) -> bool:
    return await _edit(message, _welcome_variants(), reply_markup, "welcome")


async def reply_help(message: Message, reply_markup: InlineKeyboardMarkup, section: str = None) -> bool:
    """Reply with a rich help page. False means the caller should send plain text."""
    return await _reply(message, (messages.help_rich(section),), reply_markup, "help")


async def edit_to_help(message: Message, reply_markup: InlineKeyboardMarkup, section: str = None) -> bool:
    return await _edit(message, (messages.help_rich(section),), reply_markup, "help")


async def reply_settings(message: Message, reply_markup: InlineKeyboardMarkup) -> bool:
    """Reply with the rich settings header. False means the caller should send plain text."""
    return await _reply(message, (messages.settings_rich(True), messages.settings_rich(False)), reply_markup, "settings")


async def show_settings(message: Message, reply_markup: InlineKeyboardMarkup, plain_text: str):
    """Edit a message into the settings page: rich when possible, plain text otherwise."""
    if not await _edit(message, (messages.settings_rich(True), messages.settings_rich(False)), reply_markup, "settings"):
        await edit_or_resend_text(message, plain_text, reply_markup)


async def edit_or_resend_text(message: Message, text: str, reply_markup: InlineKeyboardMarkup):
    """Edit to plain text; if Telegram refuses (e.g. the message is rich), replace it with a fresh message."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" in str(e):
            return
        logger.warning(f"Text edit failed in {message.chat.id}, resending: {e}")
        chat_id = message.chat.id
        try:
            await message.delete()
        except Exception:
            pass
        await message._client.send_message(chat_id, text, reply_markup=reply_markup)


async def edit_to_playlist_ready(message: Message, loaded: int, total: int, cap_note: str, first_track: str, plain_text: str):
    """Edit into the rich "Playlist Ready" message; plain text if Telegram refuses it."""
    variants = (
        messages.playlist_ready_rich(loaded, total, cap_note, first_track, True),
        messages.playlist_ready_rich(loaded, total, cap_note, first_track, False),
    )
    if not await _edit(message, variants, None, "playlist-ready"):
        try:
            await message.edit_text(plain_text)
        except Exception:
            pass
