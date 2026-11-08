# Copyright (C) @itsSmartDev

import asyncio
import os
from typing import Dict, Optional, Set

from pyrogram import Client
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.errors import FloodWait, RPCError

from SunloMusic.core.config import Config
from SunloMusic.core.logging import logger
from SunloMusic.db import db
from SunloMusic.services.downloader import downloader

MAX_UPLOAD_BYTES = 2000 * 1024 * 1024  # MTProto allows up to 2 GB (the 50 MB limit is Bot API HTTP only)
DIRECT_AUDIO_EXTS = (".mp3", ".m4a")

SENT = "sent"          # uploaded fresh and delivered
CACHED = "cached"      # delivered from an existing cache entry
NOT_STARTED = "not_started"
MISS = "miss"
TOO_LARGE = "too_large"
FAILED = "failed"


class AudioShare:
    """Sends a track's audio to a user's DM, caching the Telegram file_id so repeats are instant.

    The first request uploads the audio (to CACHE_CHAT_ID when configured, else to the
    requesting user) and stores the resulting file_id in MongoDB. Every later request for
    the same video is a plain send-by-file_id: no download, no upload.
    """

    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
        self._busy: Set[tuple] = set()

    def is_busy(self, user_id: int, video_id: str) -> bool:
        return (user_id, video_id) in self._busy

    async def can_dm(self, client: Client, user_id: int) -> bool:
        """True if the bot is allowed to message this user (they started it and haven't blocked it)."""
        try:
            await client.send_chat_action(user_id, ChatAction.UPLOAD_AUDIO)
            return True
        except FloodWait:
            return True
        except RPCError:
            return False

    @staticmethod
    def _caption(track: Dict) -> str:
        return f"🎵 {track.get('title', 'Unknown')}"

    async def try_cached(self, client: Client, user_id: int, video_id: str, track: Dict) -> str:
        """CACHED on a cache hit, NOT_STARTED if the user can't be messaged, MISS if nothing usable is cached."""
        entry = await db.get_audio_cache(video_id)
        if not entry:
            return MISS
        try:
            await client.send_audio(
                user_id, entry["file_id"], caption=self._caption(track), parse_mode=ParseMode.DISABLED
            )
            return CACHED
        except FloodWait:
            raise
        except RPCError as e:
            if not await self.can_dm(client, user_id):
                return NOT_STARTED
            logger.warning(f"Cached audio for {video_id} unusable ({e}); dropping it and rebuilding")
            await db.delete_audio_cache(video_id)
            return MISS

    async def _transcode(self, src: str, dst: str, track: Dict) -> bool:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", src, "-vn", "-map_metadata", "-1",
            "-metadata", f"title={track.get('title', '')}",
            "-metadata", f"artist={track.get('uploader', '')}",
            "-c:a", "libmp3lame", "-b:a", "192k", dst,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        return await proc.wait() == 0 and os.path.exists(dst)

    async def build_and_send(self, client: Client, user_id: int, video_id: str, track: Dict, requester: str) -> str:
        key = (user_id, video_id)
        self._busy.add(key)
        temp_path = None
        try:
            lock = self._locks.setdefault(video_id, asyncio.Lock())
            async with lock:
                # Someone else may have finished the upload while we waited for the lock.
                status = await self.try_cached(client, user_id, video_id, track)
                if status != MISS:
                    return status

                src = downloader._find_cached_file(video_id)
                if not src:
                    src = await downloader.download_audio(track["url"], info=track.get("_raw_info"))
                if not src:
                    return FAILED

                upload_path = src
                if not src.lower().endswith(DIRECT_AUDIO_EXTS):
                    temp_path = os.path.join(Config.CACHE_DIR, f"dl_{video_id}.mp3")
                    if not await self._transcode(src, temp_path, track):
                        return FAILED
                    upload_path = temp_path

                size = os.path.getsize(upload_path)
                if size > MAX_UPLOAD_BYTES:
                    return TOO_LARGE

                meta = dict(
                    title=track.get("title"),
                    performer=track.get("uploader"),
                    duration=int(track.get("duration") or 0),
                    parse_mode=ParseMode.DISABLED,
                )

                uploaded = None
                if Config.CACHE_CHAT_ID:
                    try:
                        uploaded = await client.send_audio(
                            Config.CACHE_CHAT_ID, upload_path,
                            caption=f"📥 {track.get('title', 'Unknown')}\nRequested by: {requester}",
                            **meta,
                        )
                    except RPCError as e:
                        logger.warning(f"Could not upload to cache chat {Config.CACHE_CHAT_ID}: {e}")

                if uploaded is None:
                    uploaded = await client.send_audio(user_id, upload_path, caption=self._caption(track), **meta)
                    delivered = True
                else:
                    delivered = False

                audio = uploaded.audio
                await db.set_audio_cache(
                    video_id, audio.file_id, audio.file_unique_id,
                    track.get("title"), int(track.get("duration") or 0), size,
                )
                logger.info(f"Cached audio for {video_id} ({size} bytes)")

                if not delivered:
                    await client.send_audio(
                        user_id, audio.file_id, caption=self._caption(track), parse_mode=ParseMode.DISABLED
                    )
                return SENT
        except Exception as e:
            logger.error(f"Download for {video_id} failed: {e}")
            return FAILED
        finally:
            self._busy.discard(key)
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass


audio_share = AudioShare()


async def log_download(client: Client, user, chat, track: Dict, video_id: str, source: str):
    """Post a text entry for a download to the log chat (audio itself only ever goes to the cache chat)."""
    if not Config.LOG_CHAT_ID:
        return
    try:
        name = user.first_name or "Unknown"
        await client.send_message(
            Config.LOG_CHAT_ID,
            f"📥 Music Download\n\n"
            f"Track: {track.get('title', 'Unknown')}\n"
            f"Video ID: {video_id}\n"
            f"User: {name} ({user.id})\n"
            f"Group: {chat.title or 'Unknown'} ({chat.id})\n"
            f"Source: {source}",
            parse_mode=ParseMode.DISABLED,
        )
    except Exception as e:
        logger.warning(f"Could not post download log: {e}")
