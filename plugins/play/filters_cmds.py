from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped
from core.call import sunlo_call
from core.ffmpeg_filters import set_filter, get_filter
from core.player import CURRENT_TRACK

FILTER_BOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔈 Clear", callback_data="fl_clear"),
        InlineKeyboardButton("🔊 Bass", callback_data="fl_bassboost"),
        InlineKeyboardButton("🎧 8D", callback_data="fl_8d")
    ],
    [
        InlineKeyboardButton("⏩ Nightcore", callback_data="fl_nightcore"),
        InlineKeyboardButton("🐌 Slowed", callback_data="fl_slowed")
    ],
    [
        InlineKeyboardButton("🎤 Karaoke (Vocals OFF)", callback_data="fl_karaoke")
    ]
])

@Client.on_message(filters.command("filter") & filters.group)
async def filter_cmd(client: Client, message: Message):
    await message.reply_text("🎛 **Select an Audio Filter to apply Live:**", reply_markup=FILTER_BOARD)

@Client.on_callback_query(filters.regex("^fl_"))
async def filter_callback(client: Client, cq):
    chat_id = cq.message.chat.id
    filter_name = cq.data.split("_")[1]
    
    ffmpeg_params = set_filter(chat_id, filter_name)
    
    if chat_id in CURRENT_TRACK:
        track_url = CURRENT_TRACK[chat_id]["stream_url"]
        try:
            await sunlo_call.change_stream(
                chat_id,
                AudioPiped(track_url, audio_parameters=None, video_parameters=None, ffmpeg_parameters=ffmpeg_params)
            )
            await cq.answer(f"✅ Applied {filter_name.capitalize()} filter live!", show_alert=True)
            await cq.message.edit_text(f"🎛 **Active Filter:** `{filter_name.capitalize()}`\nApplied successfully to the current track.")
        except Exception as e:
            await cq.answer("Error applying filter live.", show_alert=True)
    else:
        await cq.answer(f"✅ Filter set to {filter_name.capitalize()} for next tracks.", show_alert=True)
        await cq.message.edit_text(f"🎛 **Next Track Filter:** `{filter_name.capitalize()}`")
