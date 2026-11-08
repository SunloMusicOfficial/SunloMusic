# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import os

from pyrogram import Client
from pyrogram.types import Message, InputMediaPhoto

from SunloMusic.db import db
from SunloMusic.core.logging import logger
from SunloMusic.ui.keyboards import keyboards
from SunloMusic.ui.messages import messages
from SunloMusic.ui.rankings import adapter as rankings_banner
from SunloMusic.ui.rankings.avatars import collect_avatars

_RANK_PERIODS = {"daily": "Daily", "weekly": "Weekly", "global": "Global"}

_rankings_state: dict[int, dict] = {}


async def _delete_rankings_msg(client: Client, chat_id: int, keep_id: int | None = None):
    state = _rankings_state.get(chat_id)
    old_id = state.get("msg_id") if state else None
    if old_id and old_id != keep_id:
        try:
            await client.delete_messages(chat_id, old_id)
        except Exception:
            pass


async def _rank_caption(scope: str) -> str:
    if scope == "global":
        return "🌍 Global Rankings"
    return f"🏆 Group Rankings — {_RANK_PERIODS.get(scope, 'Daily')}"


async def show_rankings(client: Client, message: Message, chat_id: int, scope: str, edit: bool = False):
    scope = scope if scope in _RANK_PERIODS else "daily"
    period = _RANK_PERIODS[scope]
    menu = keyboards.ranking_menu(chat_id, scope)
    caption = await _rank_caption(scope)

    state = _rankings_state.get(chat_id)
    if edit and state and state.get("scope") == scope and state.get("msg_id") == message.id:
        return

    if scope == "global":
        stats = await db.get_global_stats()
    else:
        stats = await db.get_group_stats(chat_id, scope)

    avatars = await collect_avatars(client, stats)
    path = await rankings_banner.generate_rankings_banner(scope, stats, avatars)

    if path:
        try:
            if edit:
                try:
                    await message.edit_media(
                        InputMediaPhoto(path, caption=caption),
                        reply_markup=menu,
                    )
                    _rankings_state[chat_id] = {"msg_id": message.id, "scope": scope}
                except Exception:
                    try:
                        await message.delete()
                    except Exception:
                        pass
                    await _delete_rankings_msg(client, chat_id, keep_id=message.id)
                    sent = await client.send_photo(chat_id, path, caption=caption, reply_markup=menu)
                    _rankings_state[chat_id] = {"msg_id": sent.id, "scope": scope}
            else:
                sent = await client.send_photo(chat_id, path, caption=caption, reply_markup=menu)
                await _delete_rankings_msg(client, chat_id, keep_id=sent.id)
                _rankings_state[chat_id] = {"msg_id": sent.id, "scope": scope}
        finally:
            try:
                os.remove(path)
            except Exception:
                pass
        return

    if scope == "global":
        text = messages.global_ranking_message(stats)
    else:
        text = messages.ranking_message(stats, period)
    if edit:
        try:
            await message.edit_text(text, reply_markup=menu)
            _rankings_state[chat_id] = {"msg_id": message.id, "scope": scope}
        except Exception:
            try:
                await message.delete()
            except Exception:
                pass
            await _delete_rankings_msg(client, chat_id, keep_id=message.id)
            sent = await client.send_message(chat_id, text, reply_markup=menu)
            _rankings_state[chat_id] = {"msg_id": sent.id, "scope": scope}
    else:
        sent = await message.reply_text(text, reply_markup=menu)
        await _delete_rankings_msg(client, chat_id, keep_id=sent.id)
        _rankings_state[chat_id] = {"msg_id": sent.id, "scope": scope}


async def rank_command(client: Client, message: Message):
    from pyrogram.enums import ChatType

    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("❌ This command only works in groups!")
        return

    try:
        await show_rankings(client, message, message.chat.id, "daily", edit=False)
    except Exception as e:
        logger.error(f"Error in rank command: {e}")
        await message.reply_text(messages.error("Failed to retrieve rankings"))


async def ranking_command(client: Client, message: Message):
    await rank_command(client, message)
