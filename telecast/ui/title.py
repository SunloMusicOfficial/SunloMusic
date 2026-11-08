# Copyright (C) @itsSmartDev

import asyncio
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.raw import functions, types
from SunloMusic.db import db
from SunloMusic.core.config import Config
from SunloMusic.core.logging import logger

class TitleUpdater:
    def __init__(self, client):
        self.client = client
        self.update_tasks = {}

    async def update_title(self, chat_id: int, track: dict):
        settings = await db.get_chat_settings(chat_id)

        if not settings.get('title_update', False):
            logger.info(f"Title update disabled for {chat_id}")
            return

        try:
            title = track.get('title', 'Unknown Track')
            template = settings.get('title_template', Config.TITLE_UPDATE_TEMPLATE)

            new_title = template.format(
                title=title[:30],
                uploader=track.get('uploader', 'Unknown')[:20],
                duration=self._format_duration(track.get('duration', 0))
            )

            peer = await self.client.resolve_peer(chat_id)

            group_call = None
            if isinstance(peer, types.InputPeerChannel):
                full_chat = await self.client.invoke(
                    functions.channels.GetFullChannel(channel=peer)
                )
                group_call = full_chat.full_chat.call
            elif isinstance(peer, types.InputPeerChat):
                full_chat = await self.client.invoke(
                    functions.messages.GetFullChat(chat_id=peer.chat_id)
                )
                group_call = full_chat.full_chat.call

            if not group_call:
                logger.warning(f"No active group call in {chat_id}")
                return

            await self.client.invoke(
                functions.phone.EditGroupCallTitle(
                    call=group_call,
                    title=new_title
                )
            )
            logger.info(f"Updated voice chat title in {chat_id} to: {new_title}")

        except FloodWait as e:
            logger.warning(f"FloodWait: sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
        except ChatAdminRequired:
            logger.warning(f"Bot is not admin in chat {chat_id}, cannot update title")
        except Exception as e:
            logger.error(f"Failed to update title in {chat_id}: {e}")

    async def start_auto_update(self, chat_id: int, player_controller):
        if chat_id in self.update_tasks:
            return

        async def update_loop():
            while chat_id in self.update_tasks:
                try:
                    current_track = await player_controller.get_current_track(chat_id)
                    if current_track:
                        await self.update_title(chat_id, current_track)
                    await asyncio.sleep(300)
                except Exception as e:
                    logger.error(f"Error in title update loop for {chat_id}: {e}")
                    break

        task = asyncio.create_task(update_loop())
        self.update_tasks[chat_id] = task

    async def stop_auto_update(self, chat_id: int):
        if chat_id in self.update_tasks:
            task = self.update_tasks[chat_id]
            task.cancel()
            del self.update_tasks[chat_id]

    def _format_duration(self, seconds: int) -> str:
        if seconds == 0:
            return "Live"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

title_updater = None
