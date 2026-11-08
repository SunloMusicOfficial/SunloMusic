# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from SunloMusic.services.queue import queue_manager
from SunloMusic.services.playlist import playlist_manager
from SunloMusic.ui.keyboards import keyboards
from SunloMusic.ui.messages import messages


async def handle(client, callback_query, player, user_client, settings):
    data = callback_query.data
    message = callback_query.message
    chat_id = message.chat.id

    if data.startswith("queue_"):
        queue = await queue_manager.get_queue(chat_id)
        await message.edit_text(
            messages.queue_list(queue),
            reply_markup=keyboards.queue_navigation(chat_id, 0, max(1, (len(queue) + 9) // 10))
        )

    elif data.startswith("qpage_"):
        parts = data.split("_")
        page = int(parts[1])

        queue = await queue_manager.get_queue(chat_id)
        total_pages = max(1, (len(queue) + 9) // 10)

        await message.edit_text(
            messages.queue_list(queue, page),
            reply_markup=keyboards.queue_navigation(chat_id, page, total_pages)
        )

    elif data.startswith("clearqueue_"):
        await queue_manager.clear_queue(chat_id)
        await callback_query.answer("🗑️ Queue cleared")
        await message.edit_text("Queue cleared")

    elif data.startswith("shuffle_"):
        await queue_manager.shuffle_queue(chat_id)
        await callback_query.answer("🔀 Queue shuffled")

    elif data.startswith("loadpl_"):
        parts = data.split("_", 2)
        playlist_name = parts[1]

        playlist = await playlist_manager.load_playlist(chat_id, playlist_name)
        if playlist:
            await queue_manager.clear_queue(chat_id)
            for track in playlist.get('tracks', []):
                await queue_manager.add_track(chat_id, track)

            await callback_query.answer(f"✅ Loaded {playlist_name}")
        else:
            await callback_query.answer("❌ Failed to load", show_alert=True)

    elif data.startswith("delpl_"):
        parts = data.split("_", 2)
        playlist_name = parts[1]

        if await playlist_manager.delete_playlist(chat_id, playlist_name):
            await callback_query.answer(f"🗑️ Deleted {playlist_name}")

            playlists = await playlist_manager.list_playlists(chat_id)
            await message.edit_reply_markup(keyboards.playlist_menu(chat_id, playlists))
        else:
            await callback_query.answer("❌ Failed to delete", show_alert=True)
