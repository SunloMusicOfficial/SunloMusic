# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from sunlomusic.db import db
from sunlomusic.utils.permissions import permission_checker
from sunlomusic.ui.keyboards import keyboards
from sunlomusic.ui.messages import messages
from sunlomusic.utils.rich import show_settings


async def handle(client, callback_query, player, user_client, settings):
    data = callback_query.data
    message = callback_query.message
    chat_id = message.chat.id

    if data.startswith("settings_"):
        settings = await db.get_chat_settings(chat_id)
        await show_settings(message, keyboards.settings_menu(chat_id, settings), messages.settings_info(settings))

    elif data.startswith("toggle_mode_"):
        settings = await db.get_chat_settings(chat_id)
        new_mode = "video" if settings.get('mode') == "audio" else "audio"
        await db.update_chat_settings(chat_id, {'mode': new_mode})
        await callback_query.answer(f"Mode: {new_mode}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_autoplay_perm_"):
        settings = await db.get_chat_settings(chat_id)
        current_perm = settings.get('autoplay_permission', 'everyone')
        new_perm = 'admin' if current_perm == 'everyone' else 'everyone'
        await db.update_chat_settings(chat_id, {'autoplay_permission': new_perm})
        label = "Admin Only" if new_perm == 'admin' else "Everyone"
        await callback_query.answer(f"Autoplay Permission: {label}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_vc_welcome_"):
        settings = await db.get_chat_settings(chat_id)
        new_welcome = not settings.get('vc_welcome', True)
        await db.update_chat_settings(chat_id, {'vc_welcome': new_welcome})
        await callback_query.answer(f"VC Welcome: {'Enabled' if new_welcome else 'Disabled'}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_autoplay_"):
        settings = await db.get_chat_settings(chat_id)
        new_autoplay = not settings.get('autoplay', False)
        await db.update_chat_settings(chat_id, {'autoplay': new_autoplay})
        await callback_query.answer(f"Autoplay: {'ON' if new_autoplay else 'OFF'}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_title_"):
        settings = await db.get_chat_settings(chat_id)
        current_title_update = settings.get('title_update', False)
        new_title_update = not current_title_update

        if new_title_update:
            if not user_client:
                await callback_query.answer("User client not available", show_alert=True)
                return

            has_permission, error_msg = await permission_checker.can_edit_group_call_title(user_client, chat_id)

            if not has_permission:
                await callback_query.answer(f"Cannot enable: {error_msg}", show_alert=True)
                return

            await db.update_chat_settings(chat_id, {'title_update': True})
            await callback_query.answer("Title Update: Enabled")
        else:
            await db.update_chat_settings(chat_id, {'title_update': False})
            await callback_query.answer("Title Update: Disabled")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_admin_"):
        settings = await db.get_chat_settings(chat_id)
        new_admin_only = not settings.get('admin_only', False)
        await db.update_chat_settings(chat_id, {'admin_only': new_admin_only})
        await callback_query.answer(f"Admin Only: {'Enabled' if new_admin_only else 'Disabled'}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_shuffle_"):
        settings = await db.get_chat_settings(chat_id)
        new_shuffle = not settings.get('shuffle_mode', False)
        await db.update_chat_settings(chat_id, {'shuffle_mode': new_shuffle})
        await callback_query.answer(f"Shuffle Mode: {'Enabled' if new_shuffle else 'Disabled'}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_mention_"):
        settings = await db.get_chat_settings(chat_id)
        new_mention = not settings.get('mention_requester', True)
        await db.update_chat_settings(chat_id, {'mention_requester': new_mention})
        await callback_query.answer(f"Mention Requester: {'Enabled' if new_mention else 'Disabled'}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_playlist_perm_"):
        settings = await db.get_chat_settings(chat_id)
        current_perm = settings.get('playlist_permission', 'everyone')
        new_perm = 'admin' if current_perm == 'everyone' else 'everyone'
        await db.update_chat_settings(chat_id, {'playlist_permission': new_perm})
        label = "Admin Only" if new_perm == 'admin' else "Everyone"
        await callback_query.answer(f"Playlist Loading: {label}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("toggle_autoreply_"):
        settings = await db.get_chat_settings(chat_id)
        new_auto_reply = not settings.get('auto_reply', False)
        await db.update_chat_settings(chat_id, {'auto_reply': new_auto_reply})
        await callback_query.answer(f"Auto Reply: {'Enabled' if new_auto_reply else 'Disabled'}")

        settings = await db.get_chat_settings(chat_id)
        await message.edit_reply_markup(keyboards.settings_menu(chat_id, settings))

    elif data.startswith("quality_") and not data.startswith("setquality_"):
        await message.edit_text(
            "📺 **Select Quality**",
            reply_markup=keyboards.quality_menu(chat_id)
        )

    elif data.startswith("setquality_"):
        quality = data.split("_")[1]
        await db.update_chat_settings(chat_id, {'quality': quality})
        await callback_query.answer(f"Quality: {quality}")

        settings = await db.get_chat_settings(chat_id)
        await show_settings(message, keyboards.settings_menu(chat_id, settings), messages.settings_info(settings))

    elif data.startswith("audioquality_"):
        settings = await db.get_chat_settings(chat_id)
        current = settings.get('audio_quality', 'high')
        await message.edit_text(
            "🎵 **Select Audio Quality**\n\nHigher quality uses more bandwidth.",
            reply_markup=keyboards.audio_quality_menu(chat_id, current)
        )

    elif data.startswith("setaudioquality_"):
        audio_quality = data.split("_")[1]
        await db.update_chat_settings(chat_id, {'audio_quality': audio_quality})
        await callback_query.answer(f"Audio Quality: {audio_quality.capitalize()} (applies to the next track)")

        settings = await db.get_chat_settings(chat_id)
        await show_settings(message, keyboards.settings_menu(chat_id, settings), messages.settings_info(settings))
