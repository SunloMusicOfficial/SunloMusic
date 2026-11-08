# Copyright (C) @itsSmartDev

import random
from typing import Optional

from pyrogram.errors import FloodWait
from pyrogram.raw import functions, types

from SunloMusic.db import db
from SunloMusic.core.logging import logger
from SunloMusic.ui.messages import messages


class VCMessenger:
    def __init__(self, client):
        self.client = client

    async def welcome(self, chat_id: int, user_id: int):
        settings = await db.get_chat_settings(chat_id)
        if not settings.get('vc_welcome', True):
            logger.debug(f"VC welcome disabled for {chat_id}, not greeting {user_id}")
            return

        name = await self._display_name(user_id)
        await self.send(chat_id, messages.vc_welcome(name))

    async def send(self, chat_id: int, text: str) -> bool:
        try:
            group_call = await self._resolve_call(chat_id)
            if not group_call:
                logger.debug(f"No active group call in {chat_id}, nothing to send")
                return False

            await self.client.invoke(
                functions.phone.SendGroupCallMessage(
                    call=group_call,
                    random_id=random.randint(-(2 ** 63), 2 ** 63 - 1),
                    message=types.TextWithEntities(text=text, entities=[])
                )
            )
            logger.info(f"Sent voice-chat message in {chat_id}: {text!r}")
            return True

        except FloodWait as e:
            logger.warning(f"FloodWait: {e.value}s sending voice-chat message in {chat_id}")
            return False
        except Exception as e:
            await self._log_failure(chat_id, e)
            return False

    async def _log_failure(self, chat_id: int, error: Exception):
        reason = ""
        try:
            group_call = await self._resolve_call(chat_id)
            if group_call:
                info = await self.client.invoke(
                    functions.phone.GetGroupCall(call=group_call, limit=1)
                )
                if not getattr(info.call, "messages_enabled", False):
                    reason = " — voice-chat messages are disabled for this call"
        except Exception as e:
            logger.debug(f"Could not read the group call state for {chat_id}: {e}")

        logger.info(f"Could not post a voice-chat message in {chat_id}{reason}: {error}")

    async def _resolve_call(self, chat_id: int):
        peer = await self.client.resolve_peer(chat_id)

        if isinstance(peer, types.InputPeerChannel):
            full_chat = await self.client.invoke(
                functions.channels.GetFullChannel(channel=peer)
            )
        elif isinstance(peer, types.InputPeerChat):
            full_chat = await self.client.invoke(
                functions.messages.GetFullChat(chat_id=peer.chat_id)
            )
        else:
            return None

        return full_chat.full_chat.call

    async def _display_name(self, user_id: int) -> Optional[str]:
        try:
            user = await self.client.get_users(user_id)
        except Exception as e:
            logger.debug(f"Could not resolve a name for {user_id}: {e}")
            return None

        if not user:
            return None

        return user.first_name or user.username or None
