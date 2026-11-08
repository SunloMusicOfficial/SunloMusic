# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram import Client
from pyrogram.types import Message

from SunloMusic.db import db
from SunloMusic.services.queue import queue_manager
from SunloMusic.utils.permissions import permission_checker
from SunloMusic.ui.keyboards import keyboards
from SunloMusic.ui.messages import messages


async def clearplaylist_command(client: Client, message: Message):
    from pyrogram.enums import ChatType

    if message.chat.type == ChatType.PRIVATE:
        me = await client.get_me()
        await message.reply_text(
            messages.dm_not_allowed(),
            reply_markup=keyboards.start_menu(me.username)
        )
        return

    if not await permission_checker.check_admin(client, message, require_admin=True):
        return

    queue = await queue_manager.get_queue(message.chat.id)

    if not queue:
        await message.reply_text("❌ **Your playlist is already empty.**")
        return

    if len(queue) == 1:
        await message.reply_text("❌ **No upcoming tracks to clear. Only the current track is playing.**")
        return

    in_memory_cleared = len(queue) - 1
    playlist_state = queue_manager.get_playlist_state(message.chat.id)
    unloaded_tracks = 0
    if playlist_state:
        unloaded_tracks = max(0, playlist_state.get('total', 0) - playlist_state.get('fetched', 0))
    tracks_cleared = in_memory_cleared + unloaded_tracks
    status_msg = await message.reply_text("🗑️ **Clearing playlist...**")
    success = await queue_manager.clear_upcoming_tracks(message.chat.id)

    if success:
        await status_msg.edit_text(f"✅ **Removed {tracks_cleared} upcoming track(s).**")
    else:
        await status_msg.edit_text("❌ **Failed to clear playlist**")


async def playlist_command(client: Client, message: Message, player):
    from pyrogram.enums import ChatType

    if message.chat.type == ChatType.PRIVATE:
        me = await client.get_me()
        await message.reply_text(
            messages.dm_not_allowed(),
            reply_markup=keyboards.start_menu(me.username)
        )
        return

    queue = await queue_manager.get_queue(message.chat.id)
    if queue:
        current = queue[0]
        is_paused = await player.is_paused(message.chat.id)
        current_time = await player.get_current_time(message.chat.id)
        total_time = int(current.get('duration', 0))
        settings = await db.get_chat_settings(message.chat.id)
        loop_mode = settings.get('loop_mode', 'off')
        playlist_state = queue_manager.get_playlist_state(message.chat.id)
        playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
        playlist_msg = messages.now_playing(current, current.get('requested_by', 'Unknown'), 0, queue, playlist_unfetched)
        msg = await message.reply_text(
            playlist_msg,
            reply_markup=keyboards.player_controls(message.chat.id, is_paused, current_time, total_time, current.get('is_live', False), loop_mode, len(queue), settings.get('autoplay', False))
        )
        player.set_now_playing_message(message.chat.id, msg.id)
        import SunloMusic.ui.progress as ui_progress_updater
        if ui_progress_updater.progress_updater:
            ui_progress_updater.progress_updater.start_updates(message.chat.id, msg.id)
    else:
        await message.reply_text("📄 **Your playlist is currently empty.**")
