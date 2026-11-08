# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio

from SunloMusic.core.logging import logger
from SunloMusic.services.downloader import downloader
from SunloMusic.services.audio_share import (
    audio_share, log_download, SENT, CACHED, NOT_STARTED, TOO_LARGE,
)


async def handle(client, callback_query, player):
    """Download button: DM the current track's audio to whoever tapped it (any user, not just admins)."""
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    track = player.current_playing.get(chat_id)
    video_id = downloader.track_video_id(track)

    if not track or not video_id or track.get("is_live"):
        await callback_query.answer("❌ Download isn't available for this track.", show_alert=True)
        return

    me = await client.get_me()
    start_alert = f"📥 Start the bot first, then tap Download again.\n\nOpen @{me.username} and press Start."

    if audio_share.is_busy(user.id, video_id):
        await callback_query.answer("⏳ Already preparing this track for you.", show_alert=True)
        return

    chat = callback_query.message.chat

    def log(source: str):
        asyncio.create_task(log_download(client, user, chat, track, video_id, source))

    status = await audio_share.try_cached(client, user.id, video_id, track)
    if status == CACHED:
        await callback_query.answer("✅ Sent to your DM")
        log("Cache hit")
        return
    if status == NOT_STARTED:
        await callback_query.answer(start_alert, show_alert=True)
        return

    # Cache miss: make sure we can DM them before spending time on a download.
    if not await audio_share.can_dm(client, user.id):
        await callback_query.answer(start_alert, show_alert=True)
        return

    # The download can outlast Telegram's callback window, so answer first.
    await callback_query.answer("📥 Preparing your download… I'll send it to your DM.")
    status = await audio_share.build_and_send(client, user.id, video_id, track, user.first_name or "Unknown")

    if status in (SENT, CACHED):
        log("First download (uploaded to cache)" if status == SENT else "Cache hit")
        return
    reason = (
        "This track is too large to send (limit is 2 GB)."
        if status == TOO_LARGE
        else "Sorry, I couldn't prepare that track. Please try again in a moment."
    )
    try:
        await client.send_message(user.id, f"❌ {reason}")
    except Exception as e:
        logger.debug(f"Could not tell {user.id} the download failed: {e}")
