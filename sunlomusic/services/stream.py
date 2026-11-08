# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio
import time
from typing import Dict, Optional, Callable, Set
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from pytgcalls.types.raw import VideoParameters
from sunlomusic.core.logging import logger
from sunlomusic.services.effects import build_ffmpeg_parameters
from sunlomusic.core.errors import StreamOperationTimeout, FloodWaitError, TelegramServerError

AUDIO_QUALITY_MAP = {
    "studio": AudioQuality.STUDIO,
    "high": AudioQuality.HIGH,
    "medium": AudioQuality.MEDIUM,
    "low": AudioQuality.LOW,
}

# These must stay in step with ``downloader._get_format_selector`` and the
# quality buttons in ``keyboards.quality_menu`` — the download resolution and
# the stream resolution have to agree or ffmpeg rescales every frame.
VIDEO_QUALITY_MAP = {
    "1080p": VideoQuality.FHD_1080p,
    "720p": VideoQuality.HD_720p,
    "480p": VideoQuality.SD_480p,
    "360p": VideoQuality.SD_360p,
}

# The 1080p and above presets are defined at 60fps. A music video gains nothing
# from that and it doubles the raw frame throughput through ffmpeg, so cap it.
MAX_VIDEO_FPS = 30


def resolve_video_parameters(quality: str) -> VideoParameters:
    """Map a chat's ``quality`` setting onto the stream's video parameters.

    ``adjust_by_height=False`` mirrors what ``MediaStream`` does when it is
    handed a ``VideoQuality`` directly. With the native proportion logic that
    means the source aspect ratio is preserved and the stream is never
    upscaled: a 1920x1080 download stays 1920x1080 at the 1080p setting, and a
    portrait source keeps its full height even though that exceeds the preset's
    height. The setting therefore acts as a width cap, not a hard bounding box.
    """
    preset = VIDEO_QUALITY_MAP.get(
        (quality or "720p").lower(), VideoQuality.HD_720p
    )
    width, height, _ = preset.value
    return VideoParameters(
        width, height, frame_rate=MAX_VIDEO_FPS, adjust_by_height=False
    )


JOIN_TIMEOUT = 90
LEAVE_TIMEOUT = 45
CONTROL_TIMEOUT = 20

EMPTY_VC_GRACE = 60


class TGCallsManager:
    def __init__(self, client):
        self.client = client
        self.call = None
        self.streams: Dict[int, dict] = {}
        self.on_stream_end_callback: Optional[Callable] = None
        self.on_vc_closed_callback: Optional[Callable] = None
        self._monitor_tasks: Dict[int, asyncio.Task] = {}
        self._end_locks: Dict[int, asyncio.Lock] = {}
        self._vc_members: Dict[int, Set[int]] = {}
        self._vc_join_seen: Dict[int, Set[int]] = {}
        self._aux_tasks: Set[asyncio.Task] = set()
        self._empty_vc_tasks: Dict[int, asyncio.Task] = {}
        self._assistant_id: Optional[int] = None
        self.on_vc_empty_callback: Optional[Callable] = None
        self.on_vc_join_callback: Optional[Callable] = None

    async def initialize(self):
        if not self.call:
            self.call = PyTgCalls(self.client)
            self._register_pytgcalls_handlers()
            await self.call.start()
            logger.info("PyTgCalls initialized successfully")

    def _register_pytgcalls_handlers(self):
        try:
            from pytgcalls import filters as pytgcalls_filters

            @self.call.on_update(pytgcalls_filters.stream_end())
            async def on_stream_end(client, update):
                try:
                    chat_id = update.chat_id
                    if not chat_id or chat_id not in self.streams:
                        return
                    logger.info(f"PyTgCalls stream_end event for chat {chat_id}")
                    if chat_id in self._monitor_tasks:
                        self._monitor_tasks[chat_id].cancel()
                        del self._monitor_tasks[chat_id]
                    await self._fire_stream_end(chat_id)
                except Exception as e:
                    logger.error(f"Error in stream_end handler: {e}")

            logger.info("Registered PyTgCalls stream_end handler")
        except Exception as e:
            logger.warning(f"Could not register stream_end handler: {e}")

        try:
            from pytgcalls import filters as pytgcalls_filters
            from pytgcalls.types import GroupCallParticipant

            @self.call.on_update(pytgcalls_filters.call_participant())
            async def on_participant_update(client, update):
                try:
                    chat_id = update.chat_id
                    user_id = update.participant.user_id
                    action = update.action

                    if action == GroupCallParticipant.Action.JOINED:
                        self._vc_members.setdefault(chat_id, set()).add(user_id)
                        logger.debug(f"[VC Cache] User {user_id} joined VC in {chat_id}")
                        assistant_id = await self._get_assistant_id()
                        if user_id != assistant_id:
                            self._cancel_empty_vc_timer(chat_id)
                            self._notify_vc_join(chat_id, user_id)
                    elif action in (
                        GroupCallParticipant.Action.LEFT,
                        GroupCallParticipant.Action.KICKED,
                    ):
                        self._vc_members.get(chat_id, set()).discard(user_id)
                        logger.debug(f"[VC Cache] User {user_id} left VC in {chat_id}")
                        await self._maybe_schedule_empty_leave(chat_id)
                except Exception as e:
                    logger.error(f"Error in call_participant handler: {e}")

            logger.info("Registered PyTgCalls call_participant handler")
        except Exception as e:
            logger.warning(f"Could not register call_participant handler: {e}")

        try:
            from pytgcalls import filters as pytgcalls_filters
            from pytgcalls.types import ChatUpdate

            @self.call.on_update(
                pytgcalls_filters.chat_update(ChatUpdate.Status.KICKED)
            )
            async def on_kicked(client, update):
                try:
                    chat_id = update.chat_id
                    if chat_id not in self.streams:
                        return
                    logger.info(f"Bot was kicked from VC in {chat_id}")
                    await self._handle_vc_terminated(chat_id, "kicked")
                except Exception as e:
                    logger.error(f"Error in kicked handler: {e}")

            @self.call.on_update(
                pytgcalls_filters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT)
            )
            async def on_closed(client, update):
                try:
                    chat_id = update.chat_id
                    if chat_id not in self.streams:
                        return
                    logger.info(f"VC was closed by admin in {chat_id}")
                    actor = await self._get_vc_end_actor(chat_id)
                    await self._handle_vc_terminated(chat_id, "closed", actor)
                except Exception as e:
                    logger.error(f"Error in closed_voice_chat handler: {e}")

            logger.info("Registered PyTgCalls kicked and closed_voice_chat handlers")
        except Exception as e:
            logger.warning(f"Could not register kicked/closed_voice_chat handlers: {e}")

    def is_user_in_vc(self, chat_id: int, user_id: int) -> Optional[bool]:
        if chat_id not in self._vc_members:
            return None
        return user_id in self._vc_members[chat_id]

    def clear_vc_cache(self, chat_id: int):
        self._vc_members.pop(chat_id, None)
        self._vc_join_seen.pop(chat_id, None)

    def _notify_vc_join(self, chat_id: int, user_id: int):
        if not self.on_vc_join_callback or chat_id not in self.streams:
            return
        seen = self._vc_join_seen.setdefault(chat_id, set())
        if user_id in seen:
            return
        seen.add(user_id)
        task = asyncio.create_task(self._run_vc_join_callback(chat_id, user_id))
        self._aux_tasks.add(task)
        task.add_done_callback(self._aux_tasks.discard)

    async def _run_vc_join_callback(self, chat_id: int, user_id: int):
        try:
            await self.on_vc_join_callback(chat_id, user_id)
        except Exception as e:
            logger.error(f"Error in on_vc_join_callback for {chat_id}: {e}")

    async def _get_assistant_id(self) -> Optional[int]:
        if self._assistant_id is None:
            try:
                me = await self.client.get_me()
                self._assistant_id = me.id
            except Exception as e:
                logger.warning(f"Could not resolve assistant id: {e}")
        return self._assistant_id

    def _count_real_listeners(self, chat_id: int) -> int:
        members = self._vc_members.get(chat_id, set())
        return len([m for m in members if m != self._assistant_id])

    async def _maybe_schedule_empty_leave(self, chat_id: int):
        if chat_id not in self.streams:
            return
        await self._get_assistant_id()
        if self._count_real_listeners(chat_id) > 0:
            return
        # The cache said "empty" — confirm against Telegram before arming the timer.
        if await self._refresh_has_listeners(chat_id):
            return
        if chat_id in self._empty_vc_tasks and not self._empty_vc_tasks[chat_id].done():
            return
        logger.info(
            f"VC in {chat_id} has no listeners — auto-leaving in {EMPTY_VC_GRACE}s "
            f"unless someone rejoins"
        )
        self._empty_vc_tasks[chat_id] = asyncio.create_task(self._empty_vc_timer(chat_id))

    async def _refresh_has_listeners(self, chat_id: int) -> bool:
        """Re-sync the member cache from Telegram; True if a non-assistant is present.

        The event-driven cache misses members who were already in the call before
        the assistant joined (or whose JOINED update was dropped), so one person
        leaving made the cache look empty while another was still listening.
        If the query fails we assume someone is present (never leave on doubt).
        """
        members = await self.get_current_members(chat_id)
        if members is None:
            return True
        self._vc_members[chat_id] = members
        listeners = [m for m in members if m != self._assistant_id]
        return bool(listeners)

    def _cancel_empty_vc_timer(self, chat_id: int):
        task = self._empty_vc_tasks.pop(chat_id, None)
        if task and not task.done():
            task.cancel()
            logger.info(f"Cancelled pending empty-VC auto-leave for {chat_id} (listener present)")

    async def _empty_vc_timer(self, chat_id: int):
        try:
            await asyncio.sleep(EMPTY_VC_GRACE)
            if chat_id not in self.streams:
                return
            if self._count_real_listeners(chat_id) > 0 or await self._refresh_has_listeners(chat_id):
                logger.info(f"Empty-VC timer fired for {chat_id} but a listener is present — staying")
                return
            logger.info(f"Empty-VC grace elapsed for {chat_id} — stopping and leaving")
            self._empty_vc_tasks.pop(chat_id, None)
            await self.stop_stream(chat_id)
            if self.on_vc_empty_callback:
                try:
                    await self.on_vc_empty_callback(chat_id)
                except Exception as e:
                    logger.error(f"Error in on_vc_empty_callback for {chat_id}: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in empty-VC timer for {chat_id}: {e}")
        finally:
            self._empty_vc_tasks.pop(chat_id, None)

    async def prime_vc_cache(self, chat_id: int):
        if not self.call:
            return
        try:
            participants = await self._await_op(
                self.call.get_participants(chat_id), CONTROL_TIMEOUT, "get_participants", chat_id
            )
            if participants is None:
                return
            members = {p.user_id for p in participants}
            self._vc_members[chat_id] = members
            logger.info(f"[VC Cache] Primed {len(members)} participants in {chat_id}")
        except Exception as e:
            logger.warning(f"Could not prime VC cache for {chat_id}: {e}")

    async def get_current_members(self, chat_id: int) -> Optional[Set[int]]:
        """Freshly query the current voice-chat participants (bypasses the cache).

        The event-driven ``_vc_members`` cache can go stale (a JOINED update missed,
        or primed before a listener's presence registered), which made the mention
        logic flag a user who is actually already in the call. This queries Telegram
        directly via the user client instead.

        Returns a set of user IDs currently in the call, or ``None`` on failure
        (call ended / no active call / MTProto error) so callers can skip safely.
        """
        try:
            members: Set[int] = set()
            async for member in self.client.get_call_members(chat_id):
                if member.chat and not member.is_left:
                    members.add(member.chat.id)
            return members
        except Exception as e:
            logger.warning(f"Could not fetch current VC members for {chat_id}: {e}")
            return None

    async def get_played_time(self, chat_id: int) -> Optional[int]:
        if not self.call or chat_id not in self.streams:
            return None
        try:
            played = await self._await_op(
                self.call.time(chat_id), CONTROL_TIMEOUT, "time", chat_id
            )
            if played is None or played < 0:
                return None
            return int(played)
        except Exception as e:
            logger.debug(f"get_played_time unavailable for {chat_id}: {e}")
            return None

    async def get_ping(self) -> Optional[float]:
        if not self.call:
            return None
        try:
            return float(self.call.ping)
        except Exception as e:
            logger.debug(f"ping unavailable: {e}")
            return None

    async def get_cpu_usage(self) -> Optional[float]:
        if not self.call:
            return None
        try:
            return float(await self.call.cpu_usage)
        except Exception as e:
            logger.debug(f"cpu_usage unavailable: {e}")
            return None

    async def _get_vc_end_actor(self, chat_id: int) -> Optional[Dict]:
        if not self.client:
            return None
        try:
            from pyrogram.raw.functions.channels import GetAdminLog
            from pyrogram.raw.types import (
                ChannelAdminLogEventsFilter,
                ChannelAdminLogEventActionDiscardGroupCall,
                InputChannel,
                InputPeerChannel,
            )
        except ImportError:
            return None

        try:
            peer = await self.client.resolve_peer(chat_id)
        except Exception as e:
            logger.debug(f"Could not resolve {chat_id} for VC end lookup: {e}")
            return None
        if not isinstance(peer, InputPeerChannel):
            return None

        channel = InputChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)
        for attempt in range(3):
            try:
                result = await self.client.invoke(
                    GetAdminLog(
                        channel=channel,
                        q="",
                        max_id=0,
                        min_id=0,
                        limit=20,
                        events_filter=ChannelAdminLogEventsFilter(group_call=True),
                    )
                )
            except Exception as e:
                logger.debug(f"VC end actor unavailable in {chat_id}: {e}")
                return None

            for event in result.events:
                if not isinstance(event.action, ChannelAdminLogEventActionDiscardGroupCall):
                    continue
                if time.time() - event.date > 90:
                    continue
                name = next(
                    (u.first_name for u in result.users if u.id == event.user_id), None
                )
                if not name:
                    try:
                        name = (await self.client.get_users(event.user_id)).first_name
                    except Exception:
                        name = None
                if name:
                    logger.info(f"VC in {chat_id} was ended by {name} ({event.user_id})")
                    return {'id': event.user_id, 'name': name}
                return None

            if attempt < 2:
                await asyncio.sleep(0.6)
        return None

    async def _handle_vc_terminated(self, chat_id: int, reason: str, actor: Optional[str] = None):
        self._cancel_empty_vc_timer(chat_id)
        if chat_id in self._monitor_tasks:
            self._monitor_tasks[chat_id].cancel()
            del self._monitor_tasks[chat_id]
        self.streams.pop(chat_id, None)
        self._end_locks.pop(chat_id, None)
        self.clear_vc_cache(chat_id)
        logger.info(f"VC terminated ({reason}) in {chat_id} — state cleaned up")
        if self.on_vc_closed_callback:
            try:
                await self.on_vc_closed_callback(chat_id, reason, actor)
            except Exception as e:
                logger.error(f"Error in on_vc_closed_callback for {chat_id}: {e}")

    def set_stream_end_callback(self, callback: Callable):
        self.on_stream_end_callback = callback

    def set_vc_closed_callback(self, callback: Callable):
        self.on_vc_closed_callback = callback

    def set_vc_empty_callback(self, callback: Callable):
        self.on_vc_empty_callback = callback

    def set_vc_join_callback(self, callback: Callable):
        self.on_vc_join_callback = callback

    async def get_call(self) -> PyTgCalls:
        if not self.call:
            await self.initialize()
        return self.call

    async def _await_op(self, coro, timeout: int, op_name: str, chat_id: int):
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(
                f"PyTgCalls '{op_name}' timed out after {timeout}s in {chat_id} — "
                f"aborting to avoid blocking the event loop"
            )
            raise StreamOperationTimeout(
                f"{op_name} timed out after {timeout}s in {chat_id}"
            ) from None

    async def play_stream(self, chat_id: int, path: str, video: bool = False, quality: str = "720p", duration: int = 0, seek_position: int = None, audio_quality: str = "high", audio_effect: str = "none", speed=None):
        call = await self.get_call()

        try:
            ffmpeg_params = build_ffmpeg_parameters(audio_effect, speed, seek_position)
            audio_params = AUDIO_QUALITY_MAP.get((audio_quality or "high").lower(), AudioQuality.HIGH)

            common = {"audio_parameters": audio_params}
            if ffmpeg_params:
                common["ffmpeg_parameters"] = ffmpeg_params

            if video:
                video_params = resolve_video_parameters(quality)
                stream = MediaStream(
                    path, video_parameters=video_params, **common
                )
                logger.info(
                    f"Video stream for {chat_id}: requested '{quality}' -> "
                    f"{video_params.width}x{video_params.height}"
                    f"@{video_params.frame_rate}"
                )
            else:
                stream = MediaStream(path, video_flags=MediaStream.Flags.IGNORE, **common)

            if seek_position and seek_position > 0:
                logger.info(f"Seeking to {seek_position}s via ffmpeg_parameters for {path}")
            if (audio_effect and audio_effect != "none") or speed:
                logger.info(f"Applying audio effect '{audio_effect}' speed={speed} in {chat_id}")

            _join_retries = 3
            _join_backoff = [2, 4]
            for _attempt in range(1, _join_retries + 1):
                try:
                    await self._await_op(call.play(chat_id, stream), JOIN_TIMEOUT, "play", chat_id)
                    break
                except Exception as play_exc:
                    exc_str = str(play_exc)
                    if "FLOOD_WAIT" in exc_str or "flood_wait" in exc_str.lower():
                        import re
                        match = re.search(r'(\d+)', exc_str)
                        wait_seconds = int(match.group(1)) if match else 30
                        wait_seconds = min(wait_seconds, 120)
                        logger.warning(f"FLOOD_WAIT {wait_seconds}s on JoinGroupCall in {chat_id}, waiting before retry")
                        await asyncio.sleep(wait_seconds + 1)
                        await self._await_op(call.play(chat_id, stream), JOIN_TIMEOUT, "play", chat_id)
                        logger.info(f"Retry after FLOOD_WAIT succeeded for {chat_id}")
                        break
                    elif "after 10 retries" in exc_str or "after_10_retries" in exc_str.lower():
                        if _attempt < _join_retries:
                            wait = _join_backoff[_attempt - 1]
                            logger.warning(f"JoinGroupCall transient failure (attempt {_attempt}/{_join_retries}) in {chat_id}, retrying in {wait}s")
                            await asyncio.sleep(wait)
                            continue
                        else:
                            logger.error(f"JoinGroupCall failed after {_join_retries} bot-level retries in {chat_id}")
                            raise TelegramServerError(
                                "❌ Unable to start playback.\nTelegram voice servers are busy.\nPlease try again in a few seconds."
                            ) from None
                    else:
                        raise

            self.streams[chat_id] = {
                "playing": True,
                "paused": False,
                "duration": duration,
                "start_time": asyncio.get_running_loop().time()
            }

            prime_task = asyncio.create_task(self.prime_vc_cache(chat_id))
            self._aux_tasks.add(prime_task)
            prime_task.add_done_callback(self._aux_tasks.discard)

            effective_duration = duration
            if seek_position and seek_position > 0 and duration > 0:
                effective_duration = max(1, duration - seek_position)

            if effective_duration > 0 and self.on_stream_end_callback:
                if chat_id in self._monitor_tasks:
                    self._monitor_tasks[chat_id].cancel()
                    logger.info(f"Cancelled stale monitor task for {chat_id}")
                task = asyncio.create_task(self._monitor_stream(chat_id, effective_duration))
                self._monitor_tasks[chat_id] = task

            logger.info(f"Started playing in {chat_id}")
        except Exception as e:
            import traceback
            error_message = str(e)

            if "CHAT_ADMIN_REQUIRED" in error_message:
                logger.error(f"No active voice chat found in {chat_id} or user client cannot join")
                raise PermissionError("❌ No active video chat found.\nPlease start the video chat, then try.") from None

            if "FLOOD_WAIT" in error_message or "flood_wait" in error_message.lower():
                import re
                match = re.search(r'(\d+)', error_message)
                wait_seconds = int(match.group(1)) if match else 30
                logger.error(f"FLOOD_WAIT {wait_seconds}s persists after retry in {chat_id}")
                raise FloodWaitError(wait_seconds) from None

            logger.error(f"Failed to play stream in {chat_id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def _fire_stream_end(self, chat_id: int):
        if chat_id not in self._end_locks:
            self._end_locks[chat_id] = asyncio.Lock()
        lock = self._end_locks[chat_id]
        if lock.locked():
            return
        async with lock:
            if chat_id not in self.streams or not self.streams[chat_id].get("playing"):
                return
            self.streams[chat_id]["playing"] = False
            logger.info(f"Stream ended for chat {chat_id}")
            if self.on_stream_end_callback:
                try:
                    await self.on_stream_end_callback(chat_id)
                except Exception as e:
                    logger.error(f"Error in stream end callback for {chat_id}: {e}")
            self._end_locks.pop(chat_id, None)

    async def _monitor_stream(self, chat_id: int, duration: int):
        logger.info(f"Stream monitor started for {chat_id} (duration: {duration}s)")
        poll = 2
        played = 0.0
        try:
            while True:
                await asyncio.sleep(poll)
                stream = self.streams.get(chat_id)
                if not stream or not stream.get("playing"):
                    logger.info(f"Stream monitor ended but stream already stopped in {chat_id}")
                    return
                if stream.get("paused"):
                    continue
                played += poll
                if played >= duration + 2:
                    logger.info(f"Stream monitor firing end for {chat_id}")
                    await self._fire_stream_end(chat_id)
                    return
        except asyncio.CancelledError:
            logger.info(f"Stream monitor cancelled for {chat_id}")
        except Exception as e:
            logger.error(f"Error monitoring stream in {chat_id}: {e}")

    async def pause_stream(self, chat_id: int):
        call = await self.get_call()
        try:
            await self._await_op(call.pause(chat_id), CONTROL_TIMEOUT, "pause", chat_id)
            if chat_id in self.streams:
                self.streams[chat_id]["paused"] = True
            logger.info(f"Paused stream in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to pause stream in {chat_id}: {e}")
            raise

    async def resume_stream(self, chat_id: int):
        call = await self.get_call()
        try:
            await self._await_op(call.resume(chat_id), CONTROL_TIMEOUT, "resume", chat_id)
            if chat_id in self.streams:
                self.streams[chat_id]["paused"] = False
            logger.info(f"Resumed stream in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to resume stream in {chat_id}: {e}")
            raise

    async def stop_stream(self, chat_id: int):
        self._cancel_empty_vc_timer(chat_id)
        if chat_id in self._monitor_tasks:
            self._monitor_tasks[chat_id].cancel()
            del self._monitor_tasks[chat_id]
            logger.info(f"Cancelled monitor task on stop for {chat_id}")
        call = await self.get_call()
        try:
            await self._await_op(call.leave_call(chat_id), LEAVE_TIMEOUT, "leave_call", chat_id)
            logger.info(f"Stopped stream and left voice chat in {chat_id}")
        except Exception as e:
            logger.warning(f"leave_call error in {chat_id} (stream may have already ended): {e}")
        finally:
            if chat_id in self.streams:
                del self.streams[chat_id]
            self._end_locks.pop(chat_id, None)
            self.clear_vc_cache(chat_id)

    def is_playing(self, chat_id: int) -> bool:
        return self.streams.get(chat_id, {}).get("playing", False)

    def is_paused(self, chat_id: int) -> bool:
        return self.streams.get(chat_id, {}).get("paused", False)

    async def set_volume(self, chat_id: int, volume: int):
        if chat_id not in self.streams or not self.streams[chat_id].get("playing"):
            raise RuntimeError(f"No active stream in {chat_id} to set volume")
        call = await self.get_call()
        try:
            await self._await_op(call.change_volume_call(chat_id, volume), CONTROL_TIMEOUT, "change_volume_call", chat_id)
            logger.info(f"Set volume to {volume}% in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to set volume in {chat_id}: {e}")
            raise

    def is_muted(self, chat_id: int) -> bool:
        return self.streams.get(chat_id, {}).get("muted", False)

    async def mute(self, chat_id: int):
        call = await self.get_call()
        try:
            await self._await_op(call.mute(chat_id), CONTROL_TIMEOUT, "mute", chat_id)
            if chat_id in self.streams:
                self.streams[chat_id]["muted"] = True

            logger.info(f"Muted in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to mute in {chat_id}: {e}")
            raise

    async def unmute(self, chat_id: int):
        call = await self.get_call()
        try:
            await self._await_op(call.unmute(chat_id), CONTROL_TIMEOUT, "unmute", chat_id)
            if chat_id in self.streams:
                self.streams[chat_id]["muted"] = False

            logger.info(f"Unmuted in {chat_id}")
        except Exception as e:
            logger.error(f"Failed to unmute in {chat_id}: {e}")
            raise

    async def cleanup(self):
        for task in self._monitor_tasks.values():
            task.cancel()
        self._monitor_tasks.clear()
        for task in self._empty_vc_tasks.values():
            task.cancel()
        self._empty_vc_tasks.clear()
        for task in list(self._aux_tasks):
            task.cancel()
        self._aux_tasks.clear()
        self._end_locks.clear()
        if self.call:
            for chat_id in list(self.streams.keys()):
                try:
                    await self._await_op(self.call.leave_call(chat_id), LEAVE_TIMEOUT, "leave_call", chat_id)
                except Exception:
                    pass
            self.streams.clear()
            logger.info("TGCalls manager cleaned up")
