# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from SunloMusic.db import db
from SunloMusic.services.queue import queue_manager
from SunloMusic.ui.keyboards import keyboards
from SunloMusic.ui.messages import messages
from SunloMusic.utils.rich import show_settings
from SunloMusic.utils.permissions import permission_checker
from SunloMusic.core.logging import logger


async def handle_autoplay(client, callback_query, player):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    user_id = user.id if user else 0

    if not player.has_pending_autoplay(chat_id):
        await callback_query.answer("⌛️ This autoplay request has expired.", show_alert=True)
        return

    settings = await db.get_chat_settings(chat_id)
    if settings.get('autoplay_permission', 'everyone') == 'admin':
        is_admin = await permission_checker.is_admin(client, chat_id, user_id)
        is_vc_admin = await db.is_vc_admin(chat_id, user_id)
        if not (is_admin or is_vc_admin):
            await callback_query.answer("❌ Only admins can decide on autoplay.", show_alert=True)
            return

    if data.startswith("autoplay_no_"):
        await callback_query.answer("⏹️ Autoplay skipped")
        await player.decline_autoplay(chat_id)
        return

    await callback_query.answer("🎧 Finding related songs...")
    await player.start_autoplay(
        chat_id,
        requested_by=user.first_name if user else "Unknown",
        requested_by_id=user_id
    )


async def handle(client, callback_query, player, user_client, settings):
    data = callback_query.data
    message = callback_query.message
    chat_id = message.chat.id

    if data.startswith("pause_"):
        await player.pause(chat_id)
        await callback_query.answer("⏸️ Paused")

        current = await player.get_current_track(chat_id)
        if current:
            queue = await queue_manager.get_queue(chat_id)
            loop_mode = settings.get('loop_mode', 'off')
            current_time = await player.get_current_time(chat_id)
            total_time = int(current.get('duration', 0))
            await message.edit_reply_markup(keyboards.player_controls(
                chat_id, is_paused=True, current_time=current_time, total_time=total_time,
                is_live=current.get('is_live', False), loop_mode=loop_mode,
                queue_length=len(queue), autoplay=settings.get('autoplay', False)
            ))

    elif data.startswith("resume_"):
        await player.resume(chat_id)
        await callback_query.answer("▶️ Resumed")

        current = await player.get_current_track(chat_id)
        if current:
            queue = await queue_manager.get_queue(chat_id)
            loop_mode = settings.get('loop_mode', 'off')
            current_time = await player.get_current_time(chat_id)
            total_time = int(current.get('duration', 0))
            await message.edit_reply_markup(keyboards.player_controls(
                chat_id, is_paused=False, current_time=current_time, total_time=total_time,
                is_live=current.get('is_live', False), loop_mode=loop_mode,
                queue_length=len(queue), autoplay=settings.get('autoplay', False)
            ))

    elif data.startswith("skip_"):
        try:
            await callback_query.answer("⏭️ Skipping...")
        except:
            pass

        user_name = callback_query.from_user.first_name if callback_query.from_user else "Unknown"
        user_id = callback_query.from_user.id if callback_query.from_user else "Unknown"
        logger.info(f"SKIP BUTTON - User: {user_name} (ID: {user_id}) pressed skip in chat {chat_id}")
        await player.skip(chat_id)

    elif data.startswith("stop_"):
        await player.stop(chat_id)
        await queue_manager.clear_queue(chat_id)
        await callback_query.answer("⏹️ Stopped")
        try:
            await message.delete()
        except Exception:
            pass
        await client.send_message(chat_id, "⏹️ Stopped and left voice chat.")

    elif data.startswith("toggle_repeat_"):
        settings = await db.get_chat_settings(chat_id)
        current_mode = settings.get('loop_mode', 'off')

        new_mode = 'track' if current_mode == 'off' else 'off'

        await player.set_loop_mode(chat_id, new_mode)
        await db.update_chat_settings(chat_id, {'loop_mode': new_mode})

        if new_mode == 'track':
            await callback_query.answer("🔁 Repeat On")
        else:
            await callback_query.answer("🔁 Repeat Off")

    elif data.startswith("loop_"):
        settings = await db.get_chat_settings(chat_id)
        loop_mode = settings.get('loop_mode', 'off')

        await message.edit_text(
            "🔁 **Loop Mode**",
            reply_markup=keyboards.loop_menu(chat_id, loop_mode)
        )

    elif data.startswith("setloop_"):
        mode = data.split("_")[1]
        await player.set_loop_mode(chat_id, mode)
        await db.update_chat_settings(chat_id, {'loop_mode': mode})
        await callback_query.answer(f"Loop: {mode}")

        settings = await db.get_chat_settings(chat_id)
        await show_settings(message, keyboards.settings_menu(chat_id, settings), messages.settings_info(settings))

    elif data.startswith("back_"):
        current = await player.get_current_track(chat_id)
        if current:
            queue = await queue_manager.get_queue(chat_id)
            playlist_state = queue_manager.get_playlist_state(chat_id)
            playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
            settings = await db.get_chat_settings(chat_id)
            loop_mode = settings.get('loop_mode', 'off')
            current_time = await player.get_current_time(chat_id)
            total_time = int(current.get('duration', 0))
            await message.edit_text(
                messages.now_playing(current, current.get('requested_by', 'Unknown'), current_time, queue, playlist_unfetched),
                reply_markup=keyboards.player_controls(
                    chat_id, current_time=current_time, total_time=total_time,
                    is_live=current.get('is_live', False), loop_mode=loop_mode,
                    queue_length=len(queue), autoplay=settings.get('autoplay', False)
                )
            )
        else:
            await message.edit_text("No track playing")
        try:
            await callback_query.answer()
        except Exception:
            pass

    elif data.startswith("rewind_"):
        try:
            await callback_query.answer("⏪ Rewinded 10s")
        except Exception:
            pass
        await player.seek(chat_id, -10)

    elif data.startswith("seek_"):
        try:
            await callback_query.answer("⏩ Seeked 10s")
        except Exception:
            pass
        await player.seek(chat_id, 10)

    elif data.startswith("replay_"):
        try:
            await callback_query.answer("🔁 Replaying from start")
        except Exception:
            pass
        await player.seek(chat_id, 0)

    elif data.startswith("volume_"):
        is_muted = player.tgcalls.is_muted(chat_id)
        await message.edit_text(
            "🔊 **Sound Control**\n\nSelect volume level or an effect:",
            reply_markup=keyboards.volume_menu(chat_id, is_muted=is_muted)
        )

    elif data.startswith("mute_btn_"):
        try:
            await player.mute(chat_id)
            await callback_query.answer("🔇 Muted")

            is_muted = player.tgcalls.is_muted(chat_id)
            await message.edit_text(
                "🔊 **Sound Control**\n\nSelect volume level or an effect:",
                reply_markup=keyboards.volume_menu(chat_id, is_muted=is_muted)
            )
        except Exception as e:
            await callback_query.answer(f"❌ Failed to mute: {str(e)}", show_alert=True)

    elif data.startswith("unmute_btn_"):
        try:
            await player.unmute(chat_id)
            await callback_query.answer("🔊 Unmuted")

            is_muted = player.tgcalls.is_muted(chat_id)
            await message.edit_text(
                "🔊 **Sound Control**\n\nSelect volume level or an effect:",
                reply_markup=keyboards.volume_menu(chat_id, is_muted=is_muted)
            )
        except Exception as e:
            await callback_query.answer(f"❌ Failed to unmute: {str(e)}", show_alert=True)

    elif data.startswith("vol_"):
        volume = int(data.split("_")[1])
        try:
            if player.tgcalls.is_muted(chat_id):
                await player.unmute(chat_id)

            await player.set_volume(chat_id, volume)
            await callback_query.answer(f"🔊 Volume: {volume}%")

            current = await player.get_current_track(chat_id)
            if current:
                queue = await queue_manager.get_queue(chat_id)
                playlist_state = queue_manager.get_playlist_state(chat_id)
                playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
                settings = await db.get_chat_settings(chat_id)
                loop_mode = settings.get('loop_mode', 'off')
                current_time = await player.get_current_time(chat_id)
                total_time = int(current.get('duration', 0))
                await message.edit_text(
                    messages.now_playing(current, current.get('requested_by', 'Unknown'), current_time, queue, playlist_unfetched),
                    reply_markup=keyboards.player_controls(
                        chat_id, current_time=current_time, total_time=total_time,
                        is_live=current.get('is_live', False), loop_mode=loop_mode,
                        queue_length=len(queue), autoplay=settings.get('autoplay', False)
                    )
                )
        except NotImplementedError as e:
            await callback_query.answer(f"⚠️ {str(e)}", show_alert=True)
        except Exception as e:
            await callback_query.answer(f"❌ Failed to set volume: {str(e)}", show_alert=True)

    elif data.startswith("join_"):
        await callback_query.answer("✅ Already in voice chat")

    elif data.startswith("close_"):
        await callback_query.answer()
        await message.delete()

    elif data == "noop":
        await callback_query.answer()
