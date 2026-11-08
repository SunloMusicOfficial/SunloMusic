# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio
from typing import Dict, Optional
from pyrogram import Client
from pyrogram.errors import MessageIdInvalid, MessageNotModified, FloodWait
from sunlomusic.ui.keyboards import keyboards
from sunlomusic.core.logging import logger

class ProgressUpdater:
    def __init__(self, client: Client, player):
        self.client = client
        self.player = player
        self.update_tasks: Dict[int, asyncio.Task] = {}
        self.current_message_ids: Dict[int, int] = {}

    def _build_progress_message(self, track: Dict, queue: list, playlist_unfetched: int = 0) -> str:
        title = track.get('title', 'Unknown')
        req_name = track.get('requested_by', 'Unknown')
        req_id = track.get('requested_by_id')
        if req_id:
            req_mention = f"[{req_name}](tg://user?id={req_id})"
        else:
            req_mention = req_name

        message = f"![🎵](tg://emoji?id=5334665104677941170) **Music Playlist:**\n\n"
        message += f"**1. ![🎸](tg://emoji?id=5222472119295684375) {title}**\n"
        message += f"![🏆](tg://emoji?id=5944970130554359187) **Requested by:** {req_mention}\n\n"

        if queue and len(queue) > 1:
            for i, next_track in enumerate(queue[1:4], start=2):
                next_title = next_track.get('title', 'Unknown')
                if len(next_title) > 50:
                    next_title = next_title[:47] + "..."
                next_name = next_track.get('requested_by', 'Unknown')
                next_id = next_track.get('requested_by_id')
                if next_id:
                    next_mention = f"[{next_name}](tg://user?id={next_id})"
                else:
                    next_mention = next_name
                message += f"**{i}. ![🎸](tg://emoji?id=5222472119295684375) {next_title}**\n"
                message += f"![🏆](tg://emoji?id=5944970130554359187) **Requested by:** {next_mention}\n\n"

            shown = min(len(queue), 4)
            remaining_in_queue = len(queue) - shown
            total_remaining = remaining_in_queue + playlist_unfetched
            if total_remaining > 0:
                message += f"**✨ {total_remaining} tracks still in the playlist.....**"

        return message

    async def _update_loop(self, chat_id: int, message_id: int):
        try:
            logger.info(f"Started progress updater for chat {chat_id}")

            while True:
                try:
                    await asyncio.sleep(30)

                    if self.current_message_ids.get(chat_id) != message_id:
                        logger.info(f"Progress updater for message {message_id} superseded in {chat_id}, stopping")
                        break

                    if not await self.player.is_playing(chat_id):
                        logger.info(f"Stopping progress updater for {chat_id} - not playing")
                        break

                    current_track = await self.player.get_current_track(chat_id)
                    if not current_track:
                        logger.info(f"Stopping progress updater for {chat_id} - no track")
                        break

                    if self.current_message_ids.get(chat_id) != message_id:
                        logger.info(f"Progress updater for message {message_id} superseded in {chat_id}, stopping")
                        break

                    current_position = await self.player.get_current_time(chat_id)
                    duration = int(current_track.get('duration', 0))

                    from sunlomusic.services.queue import queue_manager
                    from sunlomusic.db import db
                    queue = await queue_manager.get_queue(chat_id)
                    playlist_state = queue_manager.get_playlist_state(chat_id)
                    playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0

                    is_paused = await self.player.is_paused(chat_id)
                    is_live = current_track.get('is_live', False)
                    new_message = self._build_progress_message(current_track, queue, playlist_unfetched)

                    settings = await db.get_chat_settings(chat_id)
                    loop_mode = settings.get('loop_mode', 'off')

                    reply_markup = keyboards.player_controls(
                        chat_id,
                        is_paused,
                        current_position,
                        duration,
                        is_live,
                        loop_mode,
                        len(queue),
                        settings.get('autoplay', False)
                    )

                    try:
                        # Try editing photo caption first (since we send photo now)
                        await self.client.edit_message_caption(
                            chat_id=chat_id,
                            message_id=message_id,
                            caption=new_message,
                            reply_markup=reply_markup
                        )
                    except Exception:
                        # Fallback to text edit if it's not a photo
                        await self.client.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=new_message,
                            reply_markup=reply_markup
                        )
                    except MessageNotModified:
                        pass
                    except FloodWait as e:
                        logger.warning(f"FloodWait in {chat_id}: waiting {e.value}s")
                        await asyncio.sleep(e.value)
                    except MessageIdInvalid:
                        logger.warning(f"Message {message_id} no longer exists in {chat_id}, stopping updater")
                        break
                    except Exception as e:
                        logger.error(f"Failed to edit progress message in {chat_id}: {e}")

                except asyncio.CancelledError:
                    logger.info(f"Progress updater cancelled for {chat_id}")
                    break
                except Exception as e:
                    logger.error(f"Error in progress update loop for {chat_id}: {e}")
                    await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"Progress updater crashed for {chat_id}: {e}")
        finally:
            logger.info(f"Progress updater stopped for {chat_id}")

    def start_updates(self, chat_id: int, message_id: int):
        self.current_message_ids[chat_id] = message_id
        if chat_id in self.update_tasks:
            task = self.update_tasks[chat_id]
            if not task.done():
                task.cancel()
            del self.update_tasks[chat_id]
        task = asyncio.create_task(self._update_loop(chat_id, message_id))
        self.update_tasks[chat_id] = task
        logger.info(f"Created progress update task for {chat_id} with message {message_id}")

    def stop_updates(self, chat_id: int):
        self.current_message_ids.pop(chat_id, None)
        if chat_id in self.update_tasks:
            task = self.update_tasks[chat_id]
            if not task.done():
                task.cancel()
            del self.update_tasks[chat_id]
            logger.info(f"Stopped progress updates for {chat_id}")

    def stop_all_updates(self):
        for chat_id in list(self.update_tasks.keys()):
            self.stop_updates(chat_id)

progress_updater = None
