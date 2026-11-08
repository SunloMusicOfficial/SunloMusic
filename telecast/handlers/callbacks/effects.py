# Copyright (C) @itsSmartDev

from SunloMusic.db import db
from SunloMusic.services.effects import normalize_effect, EFFECT_LABELS, clamp_speed
from SunloMusic.ui.keyboards import keyboards


async def handle(client, callback_query, player, user_client, settings):
    data = callback_query.data
    message = callback_query.message
    chat_id = message.chat.id

    if data.startswith("effects_"):
        current = settings.get('audio_effect', 'none')
        speed = settings.get('playback_speed', 1.0)
        await message.edit_reply_markup(
            keyboards.effects_menu(chat_id, current, speed)
        )
        await callback_query.answer()

    elif data.startswith("seteffect_"):
        effect = normalize_effect(data.split("_")[1])
        label = EFFECT_LABELS.get(effect, effect.capitalize())
        try:
            await callback_query.answer(f"🎚 {label}…")
        except Exception:
            pass
        await player.change_audio_effect(chat_id, effect=effect)

        new_settings = await db.get_chat_settings(chat_id)
        try:
            await message.edit_reply_markup(
                keyboards.effects_menu(
                    chat_id,
                    new_settings.get('audio_effect', 'none'),
                    new_settings.get('playback_speed', 1.0),
                )
            )
        except Exception:
            pass

    elif data.startswith("speedmenu_"):
        speed = settings.get('playback_speed', 1.0)
        await message.edit_reply_markup(
            keyboards.speed_menu(chat_id, speed)
        )
        await callback_query.answer()

    elif data.startswith("setspeed_"):
        speed = clamp_speed(data.split("_")[1])
        try:
            await callback_query.answer(f"🚀 Speed {speed:g}x…")
        except Exception:
            pass
        await player.change_audio_effect(chat_id, speed=speed)

        new_settings = await db.get_chat_settings(chat_id)
        try:
            await message.edit_reply_markup(
                keyboards.speed_menu(chat_id, new_settings.get('playback_speed', 1.0))
            )
        except Exception:
            pass
