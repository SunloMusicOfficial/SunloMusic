# Copyright (C) @itsSmartDev

import asyncio
import html
import os
from typing import Optional, Dict
from pyrogram.enums import ParseMode
from SunloMusic.core.config import Config
from SunloMusic.db import db
from SunloMusic.services.queue import queue_manager
from SunloMusic.services.downloader import downloader
from SunloMusic.services.processor import processor
from SunloMusic.utils.auto_join import auto_join_handler
from SunloMusic.core.errors import FloodWaitError, TelegramServerError, StreamOperationTimeout
from SunloMusic.core.logging import logger
from SunloMusic.utils.monitor import monitor_logger
from SunloMusic.ui.keyboards import keyboards
from SunloMusic.ui.messages import messages
import SunloMusic.ui.title as ui_title_updater
import SunloMusic.ui.progress as ui_progress_updater

class PlayerController:
    def __init__(self, tgcalls_manager, bot_client=None):
        self.tgcalls = tgcalls_manager
        self.bot_client = bot_client
        self.current_playing: Dict[int, Dict] = {}
        self.loop_modes: Dict[int, str] = {}
        self.repeat_counts: Dict[int, int] = {}
        self.now_playing_messages: Dict[int, int] = {}
        self.playback_start_time: Dict[int, float] = {}
        self.pause_start_time: Dict[int, float] = {}
        self.total_paused_duration: Dict[int, float] = {}
        self._play_locks: Dict[int, asyncio.Lock] = {}
        self._play_lock_owners: Dict[int, asyncio.Task] = {}
        self._prefetch_tasks: Dict[int, asyncio.Task] = {}
        self._autoplay_prompts: Dict[int, Dict] = {}

        self.tgcalls.set_stream_end_callback(self._on_stream_end)
        self.tgcalls.set_vc_closed_callback(self._on_vc_closed)
        self.tgcalls.set_vc_empty_callback(self._on_vc_empty)

    def set_bot_client(self, bot_client):
        self.bot_client = bot_client

    async def _on_stream_end(self, chat_id: int):
        logger.info(f"Handling stream end for chat {chat_id}")
        await self.play_next(chat_id)

    async def _on_vc_closed(self, chat_id: int, reason: str, actor: Optional[Dict] = None):
        logger.info(f"VC closed callback fired for {chat_id}, reason={reason}")

        if hasattr(ui_progress_updater, 'progress_updater') and ui_progress_updater.progress_updater:
            try:
                ui_progress_updater.progress_updater.stop_updating(chat_id)
            except Exception:
                pass

        await queue_manager.clear_queue(chat_id)

        self.current_playing.pop(chat_id, None)
        self.loop_modes.pop(chat_id, None)
        self.repeat_counts.pop(chat_id, None)
        self.now_playing_messages.pop(chat_id, None)
        self.playback_start_time.pop(chat_id, None)
        self.pause_start_time.pop(chat_id, None)
        self.total_paused_duration.pop(chat_id, None)
        self._cancel_prefetch(chat_id)
        self._cancel_autoplay_prompt(chat_id)

        if not self.bot_client:
            return

        parse_mode = None
        fallback_msg = None
        if reason == "kicked":
            msg = "Music assistant removed from voice chat. Playback stopped."
        elif reason == "empty":
            msg = '<emoji id="5319007286004299794">👋</emoji> <b>Music assistant left the voice chat</b> — no one was listening.'
            parse_mode = ParseMode.HTML
            fallback_msg = "👋 <b>Music assistant left the voice chat</b> — no one was listening."
        elif actor:
            name = html.escape(actor.get('name') or 'an admin')
            uid = actor.get('id')
            if isinstance(uid, int) and uid > 0:
                name = f'<a href="tg://user?id={uid}">{name}</a>'
            msg = f"Voice chat ended by <b>{name}</b>. Playback stopped."
            parse_mode = ParseMode.HTML
        else:
            msg = "Voice chat ended by an admin. Playback stopped."

        try:
            await self.bot_client.send_message(chat_id, msg, parse_mode=parse_mode)
        except Exception as e:
            if fallback_msg:
                try:
                    await self.bot_client.send_message(chat_id, fallback_msg, parse_mode=parse_mode)
                    return
                except Exception as e2:
                    e = e2
            logger.error(f"Failed to send VC terminated message in {chat_id}: {e}")

    async def _on_vc_empty(self, chat_id: int):
        logger.info(f"Auto-leave (empty VC) callback fired for {chat_id}")
        await self._on_vc_closed(chat_id, "empty")

    async def play(self, chat_id: int, track: Dict):
        lock = self._play_locks.setdefault(chat_id, asyncio.Lock())
        task = asyncio.current_task()

        if self._play_lock_owners.get(chat_id) is task:
            # A failed track calls back into play_next -> play from inside this task.
            # asyncio.Lock is not reentrant, so waiting on it here would hang forever.
            await self._play_inner(chat_id, track)
            return

        async with lock:
            self._play_lock_owners[chat_id] = task
            try:
                await self._play_inner(chat_id, track)
            finally:
                self._play_lock_owners.pop(chat_id, None)

    async def _play_inner(self, chat_id: int, track: Dict):
        self._cancel_autoplay_prompt(chat_id)

        settings = await db.get_chat_settings(chat_id)
        is_video = settings.get('mode') == 'video'
        quality = settings.get('quality', '720p')
        audio_quality = settings.get('audio_quality', 'high')
        audio_effect = settings.get('audio_effect', 'none')
        speed = settings.get('playback_speed')

        try:
            file_path = None
            join_success = True
            join_error = None

            if self.bot_client and track.get('type') == 'youtube' and not track.get('is_live', False):
                logger.info(f"Starting parallel auto-join and download for chat {chat_id}")
                raw_info = track.get('_raw_info')

                if is_video:
                    download_coro = downloader.download_video(track['url'], quality, info=raw_info)
                else:
                    download_coro = downloader.download_audio(track['url'], info=raw_info)

                join_coro = auto_join_handler.ensure_user_in_chat(
                    self.bot_client, self.tgcalls.client, chat_id
                )

                (join_result, file_path) = await asyncio.gather(join_coro, download_coro)
                join_success, join_error = join_result

                if not join_success:
                    logger.error(f"Failed to add user client to chat {chat_id}: {join_error}")
                    if join_error:
                        await self._notify_join_failure(chat_id, join_error)
                    try:
                        chat_info = await self.bot_client.get_chat(chat_id)
                        chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                        await monitor_logger.log_error("User Client Join Failed", chat_id, chat_title, join_error)
                    except Exception as log_error:
                        logger.error(f"Failed to log error: {log_error}")
                    if auto_join_handler.is_blocking_error(join_error):
                        logger.warning(f"Assistant cannot join {chat_id} until an admin acts, stopping all playback")
                        await queue_manager.clear_queue(chat_id)
                        await self.stop(chat_id)
                        return
                    await self.play_next(chat_id)
                    return

                logger.info(f"Parallel join+download complete for chat {chat_id}")

            elif self.bot_client:
                logger.info(f"Checking if user client is in chat {chat_id}")
                join_success, join_error = await auto_join_handler.ensure_user_in_chat(
                    self.bot_client, self.tgcalls.client, chat_id
                )
                if not join_success:
                    logger.error(f"Failed to add user client to chat {chat_id}: {join_error}")
                    if join_error:
                        await self._notify_join_failure(chat_id, join_error)
                    try:
                        chat_info = await self.bot_client.get_chat(chat_id)
                        chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                        await monitor_logger.log_error("User Client Join Failed", chat_id, chat_title, join_error)
                    except Exception as log_error:
                        logger.error(f"Failed to log error: {log_error}")
                    if auto_join_handler.is_blocking_error(join_error):
                        logger.warning(f"Assistant cannot join {chat_id} until an admin acts, stopping all playback")
                        await queue_manager.clear_queue(chat_id)
                        await self.stop(chat_id)
                        return
                    await self.play_next(chat_id)
                    return
                logger.info(f"User client confirmed in chat {chat_id}, proceeding with playback")
            old_file_path = self.current_playing.get(chat_id, {}).get('file_path')

            if file_path is None:
                if track.get('type') == 'youtube':
                    if track.get('is_live', False):
                        logger.info(f"Detected live stream in {chat_id}: {track.get('title')}")
                        file_path = await processor.get_stream_url(track['url'], is_video)
                        if not file_path:
                            logger.error(f"Failed to get live stream URL for {track['url']}")
                            await self.play_next(chat_id)
                            return
                    else:
                        raw_info = track.get('_raw_info')
                        if is_video:
                            file_path = await downloader.download_video(track['url'], quality, info=raw_info)
                        else:
                            file_path = await downloader.download_audio(track['url'], info=raw_info)
                elif track.get('type') == 'telegram':
                    file_path = track.get('file_path')
                elif track.get('type') == 'url':
                    file_path = track.get('url')

            if not file_path:
                logger.error(f"Failed to get file path for track in {chat_id}")

                try:
                    chat_info = await self.bot_client.get_chat(chat_id)
                    chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                    await monitor_logger.log_error(
                        "Download Failed",
                        chat_id,
                        chat_title,
                        f"Failed to download: {track.get('title', 'Unknown')}"
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log error: {log_error}")

                msg_id = self.now_playing_messages.get(chat_id)
                if msg_id and self.bot_client:
                    try:
                        await self.bot_client.edit_message_text(
                            chat_id=chat_id,
                            message_id=msg_id,
                            text=f"❌ **Failed to download:** {track.get('title', 'Unknown')}\n\nSkipping to next track..."
                        )
                    except Exception:
                        pass

                await self.play_next(chat_id)
                return

            duration = track.get('duration', 0)
            seek_position = track.get('seek_position', None)
            await self.tgcalls.play_stream(chat_id, file_path, is_video, quality, duration, seek_position, audio_quality, audio_effect, speed)

            track['file_path'] = file_path
            prev = self.current_playing.get(chat_id)
            if not prev or prev.get('url') != track.get('url') or prev.get('title') != track.get('title'):
                self.repeat_counts[chat_id] = 0
            self.current_playing[chat_id] = track
            self.playback_start_time[chat_id] = asyncio.get_running_loop().time()
            self.pause_start_time.pop(chat_id, None)
            self.total_paused_duration[chat_id] = 0

            self._start_prefetch(chat_id)

            logger.info(f"Playing in {chat_id}: {track.get('title')}")

            try:
                chat_info = await self.bot_client.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                requested_by = track.get('requested_by', 'Unknown')
                requested_by_id = track.get('requested_by_id', 0)
                song_url = track.get('url', None)

                await monitor_logger.log_song_played(
                    chat_id,
                    chat_title,
                    track.get('title', 'Unknown'),
                    requested_by,
                    song_url
                )

                await db.increment_songs_played()

                song_title = track.get('title', 'Unknown')
                duration = track.get('duration', 0)
                await db.track_song_play(chat_id, requested_by_id, requested_by, song_title, duration, track.get('thumbnail', ''))
            except Exception as e:
                logger.error(f"Failed to log song played: {e}")

            if ui_progress_updater.progress_updater:
                try:
                    from SunloMusic.ui.messages import messages
                    from SunloMusic.ui.keyboards import keyboards
                    bot_client = ui_progress_updater.progress_updater.client

                    old_msg_id = self.now_playing_messages.get(chat_id)
                    if old_msg_id:
                        try:
                            await bot_client.delete_messages(chat_id, old_msg_id)
                        except Exception:
                            pass

                    queue = await queue_manager.get_queue(chat_id)
                    playlist_state = queue_manager.get_playlist_state(chat_id)
                    playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
                    loop_mode = self.loop_modes.get(chat_id, 'off')
                    initial_position = int(track.get('seek_position', 0))
                    initial_duration = int(track.get('duration', 0))
                    new_text = messages.now_playing(track, track.get('requested_by', 'Unknown'), initial_position, queue, playlist_unfetched)
                    new_markup = keyboards.player_controls(chat_id, False, initial_position, initial_duration, track.get('is_live', False), loop_mode, len(queue), settings.get('autoplay', False))

                    new_msg = await bot_client.send_message(
                        chat_id=chat_id,
                        text=new_text,
                        reply_markup=new_markup
                    )
                    self.now_playing_messages[chat_id] = new_msg.id
                    logger.info(f"Sent new now playing message in {chat_id}")
                except Exception as e:
                    logger.error(f"Failed to update now playing message in {chat_id}: {e}")

            if settings.get('mention_requester', True):
                requested_by_id = track.get('requested_by_id', 0)
                requested_by = track.get('requested_by', 'Unknown')
                if requested_by_id:
                    try:
                        members = await self.tgcalls.get_current_members(chat_id)

                        if members is not None:
                            in_vc = requested_by_id in members
                            logger.info(
                                f"[VC Check] Fresh query for {requested_by_id} in {chat_id}: "
                                f"{'IN VC' if in_vc else 'NOT in VC'} ({len(members)} participants)"
                            )
                        else:
                            in_vc = True
                            logger.info(f"[VC Check] Could not resolve members for {chat_id}, skipping mention for safety")

                        if not in_vc:
                            mention = f"[{requested_by}](tg://user?id={requested_by_id})"
                            await self.bot_client.send_message(
                                chat_id,
                                f"![🎵](tg://emoji?id=5334665104677941170) {mention}, **Now playing your requested track.**"
                            )
                    except Exception as mention_err:
                        logger.error(f"Failed to send mention in {chat_id}: {mention_err}")

            logger.debug(f"title_updater object: {ui_title_updater.title_updater}")
            if ui_title_updater.title_updater:
                try:
                    logger.info(f"Calling title_updater.update_title for {chat_id}")
                    await ui_title_updater.title_updater.update_title(chat_id, track)
                except Exception as e:
                    logger.error(f"Failed to update title in {chat_id}: {e}")
            else:
                logger.warning("title_updater is None, cannot update title")

            if ui_progress_updater.progress_updater and chat_id in self.now_playing_messages:
                message_id = self.now_playing_messages[chat_id]
                ui_progress_updater.progress_updater.start_updates(chat_id, message_id)
                logger.info(f"Started progress updates for {chat_id}")

            if old_file_path and old_file_path != file_path:
                self._cleanup_file(old_file_path)

        except FloodWaitError as e:
            wait_seconds = e.wait_seconds
            logger.warning(f"FLOOD_WAIT {wait_seconds}s after retry in {chat_id}, notifying user and aborting playback")

            try:
                msg_id = self.now_playing_messages.get(chat_id)
                notify_text = (
                    f"⏳ **Telegram Rate Limit**\n\n"
                    f"Please wait **{wait_seconds} seconds** before starting playback again.\n"
                    f"_(Telegram has temporarily limited voice chat joins for this session)_"
                )
                if msg_id and self.bot_client:
                    try:
                        await self.bot_client.edit_message_text(
                            chat_id=chat_id,
                            message_id=msg_id,
                            text=notify_text
                        )
                    except Exception:
                        await self.bot_client.send_message(chat_id, notify_text)
                elif self.bot_client:
                    await self.bot_client.send_message(chat_id, notify_text)
            except Exception as notify_err:
                logger.error(f"Failed to notify about FloodWait in {chat_id}: {notify_err}")

            try:
                chat_info = await self.bot_client.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                await monitor_logger.log_error("Playback Error (FloodWait)", chat_id, chat_title, str(e))
            except Exception:
                pass

            await self.stop(chat_id)

        except PermissionError as e:
            logger.warning(f"Permission issue in {chat_id}: User client not in chat or insufficient permissions")

            try:
                chat_info = await self.bot_client.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                await monitor_logger.log_error("Permission Error", chat_id, chat_title, str(e))
            except Exception as log_error:
                logger.error(f"Failed to log error: {log_error}")

            try:
                if ui_progress_updater.progress_updater and chat_id in self.now_playing_messages:
                    bot_client = ui_progress_updater.progress_updater.client
                    message_id = self.now_playing_messages[chat_id]
                    await bot_client.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=str(e)
                    )
                else:
                    from pyrogram import Client
                    client = self.tgcalls.client
                    await client.send_message(
                        chat_id,
                        str(e)
                    )
            except Exception as notify_error:
                logger.error(f"Failed to notify user about permission error: {notify_error}")
            await self.stop(chat_id)
        except TelegramServerError as e:
            logger.warning(f"Telegram server error during playback in {chat_id}: {e}")

            try:
                msg_id = self.now_playing_messages.get(chat_id)
                if msg_id and self.bot_client:
                    try:
                        await self.bot_client.edit_message_text(
                            chat_id=chat_id,
                            message_id=msg_id,
                            text=str(e)
                        )
                    except Exception:
                        await self.bot_client.send_message(chat_id, str(e))
                elif self.bot_client:
                    await self.bot_client.send_message(chat_id, str(e))
            except Exception as notify_err:
                logger.error(f"Failed to notify about TelegramServerError in {chat_id}: {notify_err}")

            try:
                chat_info = await self.bot_client.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                await monitor_logger.log_error("Playback Error (Telegram Server)", chat_id, chat_title, str(e))
            except Exception:
                pass

            await self.stop(chat_id)
        except StreamOperationTimeout as e:
            logger.error(f"Voice chat operation timed out in {chat_id}: {e}")

            notify_text = (
                "⚠️ **Voice chat is not responding**\n\n"
                "Telegram's voice servers timed out while starting playback. "
                "Playback was stopped to keep the bot responsive. Please try again."
            )
            try:
                msg_id = self.now_playing_messages.get(chat_id)
                if msg_id and self.bot_client:
                    try:
                        await self.bot_client.edit_message_text(chat_id=chat_id, message_id=msg_id, text=notify_text)
                    except Exception:
                        await self.bot_client.send_message(chat_id, notify_text)
                elif self.bot_client:
                    await self.bot_client.send_message(chat_id, notify_text)
            except Exception as notify_err:
                logger.error(f"Failed to notify about StreamOperationTimeout in {chat_id}: {notify_err}")

            try:
                chat_info = await self.bot_client.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                await monitor_logger.log_error("Playback Error (Timeout)", chat_id, chat_title, str(e))
            except Exception:
                pass

            await self.stop(chat_id)
        except Exception as e:
            logger.error(f"Failed to play track in {chat_id}: {e}")

            try:
                chat_info = await self.bot_client.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else str(chat_id)
                await monitor_logger.log_error("Playback Error", chat_id, chat_title, str(e))
            except Exception as log_error:
                logger.error(f"Failed to log error: {log_error}")

            await self.play_next(chat_id)

    async def pause(self, chat_id: int) -> bool:
        try:
            if not await self.is_playing(chat_id):
                return False
            if await self.is_paused(chat_id):
                return None
            await self.tgcalls.pause_stream(chat_id)
            self.pause_start_time[chat_id] = asyncio.get_running_loop().time()
            return True
        except Exception as e:
            logger.error(f"Failed to pause in {chat_id}: {e}")
            return False

    async def resume(self, chat_id: int) -> bool:
        try:
            if not await self.is_playing(chat_id):
                return False
            if not await self.is_paused(chat_id):
                return None
            await self.tgcalls.resume_stream(chat_id)
            pause_started = self.pause_start_time.pop(chat_id, None)
            if pause_started:
                paused_duration = asyncio.get_running_loop().time() - pause_started
                self.total_paused_duration[chat_id] = self.total_paused_duration.get(chat_id, 0) + paused_duration
            return True
        except Exception as e:
            logger.error(f"Failed to resume in {chat_id}: {e}")
            return False

    async def _notify_join_failure(self, chat_id: int, join_error: str):
        """Show why the assistant couldn't join; rich version when available, markdown text as the fallback."""
        msg_id = self.now_playing_messages.get(chat_id)
        rich = getattr(join_error, 'rich_message', None)
        markup = getattr(join_error, 'reply_markup', None)

        if rich is not None:
            try:
                if msg_id:
                    try:
                        await self.bot_client.edit_message_text(chat_id=chat_id, message_id=msg_id, rich_message=rich, reply_markup=markup)
                        return
                    except Exception as edit_error:
                        logger.debug(f"Rich edit of message {msg_id} failed in {chat_id}: {edit_error}")
                await self.bot_client.send_rich_message(chat_id, rich, reply_markup=markup)
                return
            except Exception as rich_error:
                logger.warning(f"Rich join notice failed in {chat_id}, using plain text: {rich_error}")

        if msg_id:
            try:
                await self.bot_client.edit_message_text(chat_id=chat_id, message_id=msg_id, text=str(join_error), reply_markup=markup)
                return
            except Exception:
                pass
        await self.bot_client.send_message(chat_id, str(join_error), reply_markup=markup)

    async def stop(self, chat_id: int) -> bool:
        old_file = self.current_playing.get(chat_id, {}).get('file_path')
        try:
            has_current_track = chat_id in self.current_playing
            is_currently_playing = self.tgcalls.is_playing(chat_id)
            has_stream = chat_id in self.tgcalls.streams

            if not has_current_track and not is_currently_playing and not has_stream:
                logger.info(f"Nothing to stop in {chat_id}")
                return False

            if ui_progress_updater.progress_updater:
                ui_progress_updater.progress_updater.stop_updates(chat_id)

            try:
                await self.tgcalls.stop_stream(chat_id)
            except asyncio.CancelledError:
                pass
            except Exception as stop_err:
                logger.warning(f"stop_stream error in {chat_id} (may have already ended): {stop_err}")

            if chat_id in self.current_playing:
                del self.current_playing[chat_id]

            if chat_id in self.playback_start_time:
                del self.playback_start_time[chat_id]

            self.pause_start_time.pop(chat_id, None)
            self.total_paused_duration.pop(chat_id, None)
            self._cancel_prefetch(chat_id)
            self._cancel_autoplay_prompt(chat_id)

            if chat_id in self.now_playing_messages:
                del self.now_playing_messages[chat_id]

            if old_file:
                self._cleanup_file(old_file)

            logger.info(f"Stopped playback and cleaned up in {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop in {chat_id}: {e}")
            if old_file:
                self._cleanup_file(old_file)
            return False

    async def skip(self, chat_id: int):
        await self.play_next(chat_id)

    async def _maybe_fetch_more_playlist_tracks(self, chat_id: int):
        from SunloMusic.services.queue import queue_manager as qm
        from SunloMusic.services.downloader import downloader

        state = qm.get_playlist_state(chat_id)
        if not state:
            return

        queue = await qm.get_queue(chat_id)
        remaining = len(queue)

        if remaining > 2:
            return

        from SunloMusic.core.config import Config

        total = state['total']
        fetched = state['fetched']
        max_tracks = min(total, Config.MAX_PLAYLIST_TRACKS)

        if fetched >= max_tracks:
            qm.clear_playlist_state(chat_id)
            return

        batch_size = min(10, max_tracks - fetched)
        logger.info(f"Queue low ({remaining} tracks), fetching more from playlist in {chat_id} (fetched={fetched}/{max_tracks})")

        new_tracks = await downloader.get_playlist_batch(state['url'], fetched, batch_size)
        if not new_tracks:
            qm.clear_playlist_state(chat_id)
            return

        for track in new_tracks:
            track['requested_by'] = state['requested_by']
            track['requested_by_id'] = state['requested_by_id']
            await qm.add_track(chat_id, track)

        new_fetched = fetched + len(new_tracks)
        qm.update_playlist_fetched(chat_id, new_fetched)

        if new_fetched >= max_tracks:
            qm.clear_playlist_state(chat_id)

        logger.info(f"Fetched {len(new_tracks)} more tracks for {chat_id}, total fetched={new_fetched}/{total}")

    async def play_next(self, chat_id: int):
        try:
            settings = await db.get_chat_settings(chat_id)
            loop_mode = settings.get('loop_mode', 'off')

            if loop_mode == 'track':
                current = self.current_playing.get(chat_id)
                if current:
                    count = self.repeat_counts.get(chat_id, 0)
                    if count < 5:
                        self.repeat_counts[chat_id] = count + 1
                        logger.info(f"Looping track in {chat_id} (repeat {count + 1}/5)")
                        await self.play(chat_id, current)
                        return
                    else:
                        logger.info(f"Repeat limit reached in {chat_id}, disabling repeat")
                        self.repeat_counts[chat_id] = 0
                        self.loop_modes[chat_id] = 'off'
                        await db.update_chat_settings(chat_id, {'loop_mode': 'off'})

            await self._maybe_fetch_more_playlist_tracks(chat_id)

            next_track = await queue_manager.next_track(chat_id)

            if next_track:
                logger.info(f"Playing next track in {chat_id}: {next_track.get('title')}")
                await self.play(chat_id, next_track)
            elif loop_mode == 'queue':
                queue = await queue_manager.get_queue(chat_id)
                if queue and len(queue) > 0:
                    logger.info(f"Looping queue in {chat_id}")
                    await self.play(chat_id, queue[0])
                else:
                    logger.info(f"Queue ended, stopping playback in {chat_id}")
                    await self.stop(chat_id)
            else:
                if settings.get('autoplay', False):
                    await self._autoplay(chat_id)
                else:
                    logger.info(f"Queue ended, stopping playback in {chat_id}")
                    await queue_manager.clear_queue(chat_id)
                    await self.stop(chat_id)
        except Exception as e:
            logger.error(f"Error in play_next for {chat_id}: {e}")
            await self.stop(chat_id)

    async def set_loop_mode(self, chat_id: int, mode: str):
        if mode in ['off', 'track', 'queue']:
            self.loop_modes[chat_id] = mode
            await db.update_chat_settings(chat_id, {'loop_mode': mode})
            if mode != 'track':
                self.repeat_counts[chat_id] = 0
            logger.info(f"Set loop mode to '{mode}' in {chat_id}")

    async def get_current_track(self, chat_id: int) -> Optional[Dict]:
        return self.current_playing.get(chat_id)

    async def is_playing(self, chat_id: int) -> bool:
        return self.tgcalls.is_playing(chat_id)

    async def is_paused(self, chat_id: int) -> bool:
        return self.tgcalls.is_paused(chat_id)

    async def seek(self, chat_id: int, seconds: int):
        try:
            current = self.current_playing.get(chat_id)
            if not current:
                logger.warning(f"No track to seek in {chat_id}")
                return

            if current.get('is_live'):
                logger.warning(f"Cannot seek in live stream in {chat_id}")
                return

            base_position = int(current.get('seek_position', 0))
            actual_position = await self.get_current_time(chat_id)

            if seconds == 0:
                new_position = 0
                logger.info(f"REPLAY - Restarting track from beginning in {chat_id}")
            else:
                new_position = int(max(0, actual_position + seconds))

            duration = int(current.get('duration', 0))

            logger.info(f"SEEK DEBUG - Chat: {chat_id}")
            logger.info(f"  Track duration: {duration}s")
            logger.info(f"  Base position (last seek): {base_position}s")
            logger.info(f"  Actual current position: {actual_position}s")
            logger.info(f"  Seek offset: {seconds}s")
            logger.info(f"  New position: {new_position}s")
            logger.info(f"  Track: {current.get('title', 'Unknown')}")

            if duration > 0 and new_position >= duration:
                logger.info(f"Seek beyond duration ({new_position}s >= {duration}s), playing next")
                await self.play_next(chat_id)
                return

            logger.info(f"Seeking to position {new_position}s in {chat_id}")

            current['seek_position'] = new_position
            await self.play(chat_id, current)
        except Exception as e:
            logger.error(f"Failed to seek in {chat_id}: {e}")

    async def change_audio_effect(self, chat_id: int, effect: str = None, speed=None) -> bool:
        from SunloMusic.services.effects import normalize_effect, clamp_speed
        updates = {}
        if effect is not None:
            updates['audio_effect'] = normalize_effect(effect)
        if speed is not None:
            updates['playback_speed'] = clamp_speed(speed)
        if updates:
            await db.update_chat_settings(chat_id, updates)

        current = self.current_playing.get(chat_id)
        if not current or current.get('is_live'):
            return False

        actual_position = await self.get_current_time(chat_id)
        current['seek_position'] = int(max(0, actual_position))
        await self.play(chat_id, current)
        return True

    async def set_volume(self, chat_id: int, volume: int):
        try:
            await self.tgcalls.set_volume(chat_id, volume)
            logger.info(f"Set volume to {volume}% in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to set volume in {chat_id}: {e}")
            raise

    async def mute(self, chat_id: int):
        try:
            await self.tgcalls.mute(chat_id)
            logger.info(f"Muted in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to mute in {chat_id}: {e}")
            raise

    async def unmute(self, chat_id: int):
        try:
            await self.tgcalls.unmute(chat_id)
            logger.info(f"Unmuted in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to unmute in {chat_id}: {e}")
            raise

    def set_now_playing_message(self, chat_id: int, message_id: int):
        self.now_playing_messages[chat_id] = message_id

    def get_now_playing_message(self, chat_id: int) -> Optional[int]:
        return self.now_playing_messages.get(chat_id)

    async def get_current_time(self, chat_id: int) -> int:
        if chat_id not in self.current_playing:
            return 0

        current = self.current_playing[chat_id]
        if current.get('is_live'):
            return 0

        base_position = int(current.get('seek_position', 0))
        duration = int(current.get('duration', 0))

        played = await self.tgcalls.get_played_time(chat_id)
        if played is not None:
            position = base_position + played
            if duration > 0:
                position = min(position, duration)
            return max(0, position)

        start_time = self.playback_start_time.get(chat_id, 0)
        if start_time == 0:
            return 0

        now = asyncio.get_running_loop().time()
        total_paused = self.total_paused_duration.get(chat_id, 0)
        pause_started = self.pause_start_time.get(chat_id)
        if pause_started:
            total_paused += now - pause_started

        elapsed = int(now - start_time - total_paused)
        position = base_position + elapsed

        if duration > 0:
            position = min(position, duration)

        return max(0, position)

    def _cleanup_file(self, file_path: str):
        import os
        import tempfile
        try:
            if not file_path:
                return
            abs_path = os.path.abspath(file_path)
            is_download = 'downloads' + os.sep in abs_path or abs_path.endswith('downloads')
            is_temp = abs_path.startswith(tempfile.gettempdir()) or abs_path.startswith('/tmp/')
            if not (is_download or is_temp):
                logger.info(f"Skipping cleanup for file outside downloads/tmp: {abs_path}")
                return
            if os.path.exists(abs_path):
                os.remove(abs_path)
                logger.info(f"Cleaned up file: {abs_path}")
            else:
                logger.warning(f"Cleanup skipped, file not found: {abs_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {e}")

    def _forget_prefetch(self, chat_id: int, task: asyncio.Task):
        if self._prefetch_tasks.get(chat_id) is task:
            self._prefetch_tasks.pop(chat_id, None)

    def _cancel_prefetch(self, chat_id: int):
        task = self._prefetch_tasks.pop(chat_id, None)
        if task and not task.done():
            task.cancel()

    def _start_prefetch(self, chat_id: int):
        if not Config.PREFETCH_ENABLED:
            return

        existing = self._prefetch_tasks.get(chat_id)
        if existing and not existing.done():
            return

        try:
            task = asyncio.create_task(self._prefetch_next(chat_id))
        except RuntimeError:
            return
        self._prefetch_tasks[chat_id] = task
        task.add_done_callback(lambda t: self._forget_prefetch(chat_id, t))

    async def _prefetch_next(self, chat_id: int):
        try:
            queue = await queue_manager.get_queue(chat_id)
            if len(queue) < 2:
                return

            upcoming = queue[1]
            if upcoming.get('type') != 'youtube' or upcoming.get('is_live'):
                return

            settings = await db.get_chat_settings(chat_id)
            if settings.get('mode') == 'video':
                return

            existing = upcoming.get('file_path')
            if existing and os.path.exists(existing):
                return

            title = upcoming.get('title', 'Unknown')
            started = asyncio.get_running_loop().time()
            logger.info(f"Prefetching next track in {chat_id}: {title}")

            path = await downloader.download_audio(upcoming['url'], info=upcoming.get('_raw_info'))
            if path:
                upcoming['file_path'] = path
                logger.info(
                    f"Prefetched {title!r} in {asyncio.get_running_loop().time() - started:.1f}s"
                )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"Prefetch for {chat_id} failed: {e}")

    def _cancel_autoplay_prompt(self, chat_id: int):
        pending = self._autoplay_prompts.pop(chat_id, None)
        task = (pending or {}).get('task')
        if task and not task.done():
            task.cancel()

    def has_pending_autoplay(self, chat_id: int) -> bool:
        return chat_id in self._autoplay_prompts

    async def _edit_autoplay_message(self, chat_id: int, message_id: Optional[int], text: str):
        if not message_id or not self.bot_client:
            return
        try:
            await self.bot_client.edit_message_text(
                chat_id=chat_id, message_id=message_id, text=text
            )
        except Exception as e:
            logger.debug(f"Failed to edit autoplay message in {chat_id}: {e}")

    async def _edit_autoplay_rich(self, chat_id: int, message_id: Optional[int], variants, fallback_text: str, reply_markup=None):
        """Edit the autoplay message into a rich one; plain text if Telegram refuses every variant."""
        if not message_id or not self.bot_client:
            return
        for rich in variants:
            try:
                await self.bot_client.edit_message_text(
                    chat_id=chat_id, message_id=message_id, rich_message=rich, reply_markup=reply_markup
                )
                return
            except Exception as e:
                logger.warning(f"Rich autoplay edit failed in {chat_id}: {e}")
        try:
            await self.bot_client.edit_message_text(
                chat_id=chat_id, message_id=message_id, text=fallback_text, reply_markup=reply_markup
            )
        except Exception as e:
            logger.debug(f"Failed to edit autoplay message in {chat_id}: {e}")

    async def _autoplay(self, chat_id: int):
        if self.has_pending_autoplay(chat_id):
            logger.info(f"Autoplay prompt already pending in {chat_id}, not asking again")
            return

        seed = self.current_playing.get(chat_id)
        seed_title = (seed or {}).get('title', 'Unknown')

        if not self.bot_client or not downloader.track_video_id(seed):
            logger.info(f"Queue ended in {chat_id}, no YouTube track to build autoplay from")
            await queue_manager.clear_queue(chat_id)
            await self.stop(chat_id)
            return

        logger.info(f"Queue ended in {chat_id}, asking whether to autoplay from {seed_title!r}")
        try:
            markup = keyboards.autoplay_prompt(chat_id)
            prompt = None
            for rich in (messages.autoplay_prompt_rich(seed_title, True), messages.autoplay_prompt_rich(seed_title, False)):
                try:
                    prompt = await self.bot_client.send_rich_message(chat_id, rich, reply_markup=markup)
                    break
                except Exception as e:
                    logger.warning(f"Rich autoplay prompt failed in {chat_id}: {e}")
            if prompt is None:
                prompt = await self.bot_client.send_message(
                    chat_id, messages.autoplay_prompt(seed_title), reply_markup=markup
                )
        except Exception as e:
            logger.error(f"Failed to send autoplay prompt in {chat_id}: {e}")
            await queue_manager.clear_queue(chat_id)
            await self.stop(chat_id)
            return

        try:
            task = asyncio.create_task(self._autoplay_timeout(chat_id, prompt.id))
        except RuntimeError:
            task = None

        self._autoplay_prompts[chat_id] = {
            'message_id': prompt.id,
            'seed_title': seed_title,
            'task': task,
        }

    async def _autoplay_timeout(self, chat_id: int, message_id: int):
        try:
            await asyncio.sleep(Config.AUTOPLAY_PROMPT_TIMEOUT)

            pending = self._autoplay_prompts.get(chat_id)
            if not pending or pending.get('message_id') != message_id:
                return

            self._autoplay_prompts.pop(chat_id, None)
            logger.info(f"Autoplay prompt in {chat_id} expired after {Config.AUTOPLAY_PROMPT_TIMEOUT}s")

            await self._edit_autoplay_message(chat_id, message_id, messages.autoplay_expired())
            await queue_manager.clear_queue(chat_id)
            await self.stop(chat_id)
        except asyncio.CancelledError:
            pass

    async def start_autoplay(self, chat_id: int, requested_by: str = "Unknown", requested_by_id: int = 0) -> bool:
        pending = self._autoplay_prompts.pop(chat_id, None)
        task = (pending or {}).get('task')
        if task and not task.done():
            task.cancel()

        message_id = (pending or {}).get('message_id')
        seed = self.current_playing.get(chat_id)
        seed_title = (pending or {}).get('seed_title') or (seed or {}).get('title', 'Unknown')

        if not seed:
            logger.warning(f"Autoplay allowed in {chat_id} but the seed track is gone")
            await self._edit_autoplay_message(chat_id, message_id, messages.autoplay_unavailable())
            await queue_manager.clear_queue(chat_id)
            await self.stop(chat_id)
            return False

        await self._edit_autoplay_message(chat_id, message_id, messages.autoplay_searching())

        tracks = await downloader.get_related_tracks(seed, limit=Config.AUTOPLAY_BATCH_SIZE)

        if not tracks:
            logger.info(f"No related tracks found for {chat_id}, stopping playback")
            await self._edit_autoplay_message(chat_id, message_id, messages.autoplay_unavailable())
            await queue_manager.clear_queue(chat_id)
            await self.stop(chat_id)
            return False

        for track in tracks:
            track['requested_by'] = requested_by
            track['requested_by_id'] = requested_by_id
            await queue_manager.add_track(chat_id, track)

        logger.info(f"Autoplay queued {len(tracks)} related track(s) in {chat_id} from {seed_title!r}")
        await self._edit_autoplay_rich(
            chat_id, message_id,
            (
                messages.autoplay_queued_rich(len(tracks), seed_title, True),
                messages.autoplay_queued_rich(len(tracks), seed_title, False),
            ),
            messages.autoplay_queued(len(tracks), seed_title),
            reply_markup=keyboards.close_only(chat_id),
        )
        await self.play(chat_id, tracks[0])
        return True

    async def decline_autoplay(self, chat_id: int) -> bool:
        pending = self._autoplay_prompts.pop(chat_id, None)
        if not pending:
            return False

        task = pending.get('task')
        if task and not task.done():
            task.cancel()

        await self._edit_autoplay_message(chat_id, pending.get('message_id'), messages.autoplay_declined())
        await queue_manager.clear_queue(chat_id)
        await self.stop(chat_id)
        return True

player_controller = None
