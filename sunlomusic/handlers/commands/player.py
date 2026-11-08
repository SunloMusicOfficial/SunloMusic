# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from sunlomusic.db import db
from sunlomusic.services.queue import queue_manager
from sunlomusic.services.downloader import downloader
from sunlomusic.utils.rich import edit_to_playlist_ready
from sunlomusic.utils.permissions import permission_checker
from sunlomusic.utils.validators import validators
from sunlomusic.ui.keyboards import keyboards
from sunlomusic.ui.messages import messages
from sunlomusic.core.logging import logger
from sunlomusic.core.config import Config


async def play_command(client: Client, message: Message, player, tgcalls):
    from pyrogram.enums import ChatType

    if message.chat.type == ChatType.PRIVATE:
        me = await client.get_me()
        await message.reply_text(
            messages.dm_not_allowed(),
            reply_markup=keyboards.start_menu(me.username)
        )
        return

    if not await permission_checker.check_admin(client, message):
        return

    query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if message.reply_to_message:
        from sunlomusic.services.processor import processor
        status_msg = await message.reply_text("📥 **Processing Telegram file...**")
        file_info = await processor.download_telegram_file(client, message.reply_to_message)

        if file_info and 'error' in file_info:
            if file_info['error'] == 'unsupported':
                await status_msg.edit_text("❌ **Only audio and video files are supported.**")
            else:
                await status_msg.edit_text(messages.error("Unable to process that file. Please try another file."))
            return

        if file_info:
            file_duration = file_info.get('duration', 0) or 0
            if file_duration > Config.MAX_TRACK_DURATION:
                hours = Config.MAX_TRACK_DURATION // 3600
                dur_h = int(file_duration // 3600)
                dur_m = int((file_duration % 3600) // 60)
                await status_msg.edit_text(
                    f"⏱️ **Track Too Long**\n\n"
                    f"![🎸](tg://emoji?id=5222472119295684375) {file_info.get('title', 'This file')}\n"
                    f"⌛️ **Duration:** {dur_h}h {dur_m}m\n"
                    f"⚠️ **Limit:** {hours}h max\n\n"
                    f"Please choose a shorter track."
                )
                return
            track = {
                'type': 'telegram',
                'file_path': file_info['file_path'],
                'title': file_info['title'],
                'duration': file_info['duration'],
                'uploader': file_info['performer'],
                'requested_by': message.from_user.first_name if message.from_user else "Unknown",
                'requested_by_id': message.from_user.id if message.from_user else 0
            }
            await queue_manager.add_track(message.chat.id, track)

            if not await player.is_playing(message.chat.id):
                current = await queue_manager.get_current_track(message.chat.id)
                if current:
                    try:
                        await status_msg.edit_text("![🚀](tg://emoji?id=5429440296867886716) **Almost there… Starting playback!**")
                    except Exception:
                        pass
                    player.set_now_playing_message(message.chat.id, status_msg.id)
                    try:
                        await player.play(message.chat.id, current)
                    except Exception as play_err:
                        logger.error(f"Error starting playback in {message.chat.id}: {play_err}")
                        try:
                            await status_msg.edit_text(messages.error(str(play_err)))
                        except Exception:
                            await message.reply_text(messages.error(str(play_err)))
            else:
                queue = await queue_manager.get_queue(message.chat.id)
                current = await player.get_current_track(message.chat.id)
                is_paused = await player.is_paused(message.chat.id)
                current_time = await player.get_current_time(message.chat.id)
                total_time = int(current.get('duration', 0)) if current else 0
                is_live = current.get('is_live', False) if current else False
                settings = await db.get_chat_settings(message.chat.id)
                loop_mode = settings.get('loop_mode', 'off')
                playlist_state = queue_manager.get_playlist_state(message.chat.id)
                playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
                try:
                    await status_msg.delete()
                except Exception:
                    pass
                old_np_id = player.get_now_playing_message(message.chat.id)
                _thumb = current.get('thumbnail') if current else None
                _caption = messages.now_playing(current, current.get('requested_by', 'Unknown'), current_time, queue, playlist_unfetched)
                _kb = keyboards.player_controls(message.chat.id, is_paused, current_time, total_time, is_live, loop_mode, len(queue), settings.get('autoplay', False))
                
                if _thumb and _thumb.startswith("http"):
                    try:
                        msg = await message.reply_photo(
                            photo=_thumb,
                            caption=_caption,
                            reply_markup=_kb
                        )
                    except Exception as e:
                        logger.error(f"Thumbnail send failed: {e}")
                        msg = await message.reply_text(_caption, reply_markup=_kb)
                else:
                    msg = await message.reply_text(_caption, reply_markup=_kb)
                if old_np_id and old_np_id != msg.id:
                    try:
                        await client.delete_messages(message.chat.id, old_np_id)
                    except Exception:
                        pass
                player.set_now_playing_message(message.chat.id, msg.id)
                import sunlomusic.ui.progress as ui_progress_updater
                if ui_progress_updater.progress_updater:
                    ui_progress_updater.progress_updater.start_updates(message.chat.id, msg.id)
        else:
            await status_msg.edit_text(messages.error("Unable to process that file. Please try another file."))
        return

    if not query:
        await message.reply_text("❌ **I need a song name or YouTube link to play.**")
        return

    source_type, source_value = validators.detect_source(query)

    try:
        status_msg = await message.reply_text("![🔎](tg://emoji?id=5258396243666681152) **Searching your song… hold on!**")

        if source_type == 'url' and not validators.is_youtube_url(source_value):
            await status_msg.edit_text("❌ **Only YouTube links are supported for playback.**")
            return

        if source_type == 'youtube' and downloader.is_playlist_url(source_value):
            if not await permission_checker.can_use_playlist(client, message):
                try:
                    await status_msg.delete()
                except Exception:
                    pass
                return

            await status_msg.edit_text("📋 **Loading playlist… fetching first tracks!**")

            playlist_info = await downloader.get_playlist_info(source_value)
            if not playlist_info or not playlist_info.get('entries'):
                await status_msg.edit_text(messages.error("Could not load playlist. Make sure it is public."))
                return

            total = min(playlist_info['total'], Config.MAX_PLAYLIST_TRACKS)
            batch_size = 10
            first_batch = await downloader.get_playlist_batch(source_value, 0, batch_size)

            if not first_batch:
                await status_msg.edit_text(messages.error("Could not load any tracks from playlist."))
                return

            requester = message.from_user.first_name if message.from_user else "Unknown"
            requester_id = message.from_user.id if message.from_user else 0

            for track in first_batch:
                track['requested_by'] = requester
                track['requested_by_id'] = requester_id
                await queue_manager.add_track(message.chat.id, track)

            loaded = len(first_batch)
            queue_manager.set_playlist_state(
                message.chat.id, source_value, total, loaded, requester, requester_id
            )

            original_total = playlist_info['total']
            cap_note = " (limit)" if original_total > Config.MAX_PLAYLIST_TRACKS else ""
            first_track_title = first_batch[0].get('title', 'Unknown') if first_batch else 'Unknown'
            first_track_artist = first_batch[0].get('uploader', '') if first_batch else ''
            if first_track_artist and first_track_artist != 'Unknown':
                first_track_line = f"{first_track_artist} — {first_track_title}"
            else:
                first_track_line = first_track_title
            await edit_to_playlist_ready(
                status_msg, loaded, total, cap_note, first_track_line,
                f"🎧 **Playlist Ready**\n\n"
                f"• Added to queue: **{loaded} tracks**\n"
                f"• Playlist contains: **{total} tracks{cap_note}**\n\n"
                f"▶️ **First Track:**\n{first_track_line}",
            )

            if not await player.is_playing(message.chat.id):
                current = await queue_manager.get_current_track(message.chat.id)
                if current:
                    player.set_now_playing_message(message.chat.id, status_msg.id)
                    await player.play(message.chat.id, current)
            return

        if source_type == 'search':
            metadata = await downloader.search_one(source_value)
        else:
            metadata = await downloader.get_metadata(source_value)

        if not metadata:
            await status_msg.edit_text(messages.error("No results found. Try a different link or search term."))
            return

        track_duration = metadata.get('duration', 0) or 0
        if not metadata.get('is_live', False) and track_duration > Config.MAX_TRACK_DURATION:
            hours = Config.MAX_TRACK_DURATION // 3600
            dur_h = int(track_duration // 3600)
            dur_m = int((track_duration % 3600) // 60)
            await status_msg.edit_text(
                f"⏱️ **Track Too Long**\n\n"
                f"![🎸](tg://emoji?id=5222472119295684375) {metadata.get('title', 'This track')}\n"
                f"⌛️ **Duration:** {dur_h}h {dur_m}m\n"
                f"⚠️ **Limit:** {hours}h max\n\n"
                f"Please choose a shorter track."
            )
            return

        track = {
            'type': 'youtube',
            'url': metadata['url'],
            'title': metadata['title'],
            'duration': metadata['duration'],
            'uploader': metadata['uploader'],
            'thumbnail': metadata['thumbnail'],
            'is_live': metadata.get('is_live', False),
            'requested_by': message.from_user.first_name if message.from_user else "Unknown",
            'requested_by_id': message.from_user.id if message.from_user else 0,
            '_raw_info': metadata.get('_raw_info'),
        }

        if await player.is_playing(message.chat.id):
            current = await player.get_current_track(message.chat.id)
            current_video_id = downloader.track_video_id(current) if current else None
            if current_video_id and current_video_id == downloader.track_video_id(track):
                logger.info(f"Refused duplicate play of '{track['title']}' in {message.chat.id} (already playing)")
                await status_msg.edit_text(
                    f"🔁 **Already Playing**\n\n"
                    f"![🎸](tg://emoji?id=5222472119295684375) {track['title']}\n\n"
                    f"⚠️ **This music is already playing in the voice chat.**"
                )
                return

        await queue_manager.add_track(message.chat.id, track)

        if not await player.is_playing(message.chat.id):
            current = await queue_manager.get_current_track(message.chat.id)
            if current:
                try:
                    await status_msg.edit_text("![🚀](tg://emoji?id=5429440296867886716) **Almost there… Starting playback!**")
                except Exception:
                    pass
                player.set_now_playing_message(message.chat.id, status_msg.id)
                try:
                    await player.play(message.chat.id, current)
                except Exception as play_err:
                    logger.error(f"Error starting playback in {message.chat.id}: {play_err}")
                    try:
                        await status_msg.edit_text(messages.error(str(play_err)))
                    except Exception:
                        await message.reply_text(messages.error(str(play_err)))
        else:
            queue = await queue_manager.get_queue(message.chat.id)
            current = await player.get_current_track(message.chat.id)
            is_paused = await player.is_paused(message.chat.id)
            current_time = await player.get_current_time(message.chat.id)
            total_time = int(current.get('duration', 0)) if current else 0
            is_live = current.get('is_live', False) if current else False
            settings = await db.get_chat_settings(message.chat.id)
            loop_mode = settings.get('loop_mode', 'off')
            playlist_state = queue_manager.get_playlist_state(message.chat.id)
            playlist_unfetched = (playlist_state['total'] - playlist_state['fetched']) if playlist_state else 0
            try:
                await status_msg.delete()
            except Exception:
                pass
            old_np_id = player.get_now_playing_message(message.chat.id)
            msg = await message.reply_text(
                messages.now_playing(current, current.get('requested_by', 'Unknown'), current_time, queue, playlist_unfetched),
                reply_markup=keyboards.player_controls(message.chat.id, is_paused, current_time, total_time, is_live, loop_mode, len(queue), settings.get('autoplay', False))
            )
            if old_np_id and old_np_id != msg.id:
                try:
                    await client.delete_messages(message.chat.id, old_np_id)
                except Exception:
                    pass
            player.set_now_playing_message(message.chat.id, msg.id)
            import sunlomusic.ui.progress as ui_progress_updater
            if ui_progress_updater.progress_updater:
                ui_progress_updater.progress_updater.start_updates(message.chat.id, msg.id)

    except Exception as e:
        logger.error(f"Error in play command: {e}")
        try:
            await status_msg.edit_text(messages.error(str(e)))
        except Exception:
            await message.reply_text(messages.error(str(e)))


async def pause_command(client: Client, message: Message, player):
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

    result = await player.pause(message.chat.id)
    if result is True:
        await message.reply_text("![⏸️](tg://emoji?id=6111404923637733475) **Playback paused.**")
    elif result is None:
        await message.reply_text("⏸️ **Playback is already paused.**")
    else:
        await message.reply_text("❌ **There is no active track at the moment.**")


async def resume_command(client: Client, message: Message, player):
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

    result = await player.resume(message.chat.id)
    if result is True:
        await message.reply_text("![▶️](tg://emoji?id=5850346984501680054) **Playback resumed.**")
    elif result is None:
        await message.reply_text("▶️ **Music is already playing.**")
    else:
        await message.reply_text("❌ **There is no active track at the moment.**")


async def skip_command(client: Client, message: Message, player):
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

    if not await player.is_playing(message.chat.id):
        await message.reply_text("❌ **No music in queue**")
        return

    user_name = message.from_user.first_name if message.from_user else "Unknown"
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info(f"SKIP COMMAND - User: {user_name} (ID: {user_id}) skipped in chat {message.chat.id}")
    status_msg = await message.reply_text("![⏭️](tg://emoji?id=6111707078881975618) **Skipping to next track...**")
    await player.skip(message.chat.id)
    try:
        await status_msg.edit_text(
            '<emoji id="6111707078881975618">⏭️</emoji> <b>Skipped to the next track.</b>',
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        await status_msg.edit_text("⏭️ **Skipped to the next track.**")


async def stop_command(client: Client, message: Message, player):
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

    status_msg = await message.reply_text("🛑 **Stopping playback...**")
    if await player.stop(message.chat.id):
        await queue_manager.clear_queue(message.chat.id)
        await status_msg.edit_text("![🚫](tg://emoji?id=5280803324273115630) **Player stopped and voice chat left.**")
    else:
        await status_msg.edit_text("🛑 **The player is not running right now.**")


async def seek_command(client: Client, message: Message, player):
    if not await permission_checker.check_admin(client, message, require_admin=True):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ **Usage: /seek <seconds>**")
        return

    try:
        seconds = int(args[1])
        if seconds > 0:
            status_msg = await message.reply_text(f"⏩ **Seeking forward...**")
        elif seconds < 0:
            status_msg = await message.reply_text(f"⏪ **Rewinding...**")
        else:
            status_msg = await message.reply_text(f"🔁 **Restarting...**")

        await player.seek(message.chat.id, seconds)

        if seconds > 0:
            await status_msg.edit_text(f"⏩ **Seeked forward {seconds}s**")
        elif seconds < 0:
            await status_msg.edit_text(f"⏪ **Rewinded {abs(seconds)}s**")
        else:
            await status_msg.edit_text(f"🔁 **Restarted from the beginning.**")
    except ValueError:
        await message.reply_text("❌ **Invalid seconds value**")


async def rewind_command(client: Client, message: Message, player):
    if not await permission_checker.check_admin(client, message, require_admin=True):
        return

    args = message.text.split()
    if len(args) < 2:
        seconds = 10
    else:
        try:
            seconds = int(args[1])
        except ValueError:
            await message.reply_text("❌ **Invalid seconds value**")
            return

    status_msg = await message.reply_text(f"⏪ **Rewinding {seconds}s...**")
    await player.seek(message.chat.id, -seconds)
    await status_msg.edit_text(f"⏪ **Rewinded {seconds}s**")


async def mute_command(client: Client, message: Message, player):
    if not await permission_checker.check_admin(client, message, require_admin=True):
        return

    try:
        await player.mute(message.chat.id)
        await message.reply_text("![🔇](tg://emoji?id=5408916593780470262) **Voice chat muted successfully.**")
    except Exception as e:
        logger.error(f"Error in mute command: {e}")
        await message.reply_text(messages.error(str(e)))


async def unmute_command(client: Client, message: Message, player):
    if not await permission_checker.check_admin(client, message, require_admin=True):
        return

    try:
        await player.unmute(message.chat.id)
        await message.reply_text("![🔊](tg://emoji?id=5260325873688518261) **Voice chat unmuted.**")
    except Exception as e:
        logger.error(f"Error in unmute command: {e}")
        await message.reply_text(messages.error(str(e)))