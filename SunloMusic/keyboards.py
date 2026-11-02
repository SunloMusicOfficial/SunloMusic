from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar

# Agar tumhara Pyrogram version 'style' support karta hai (Kurigram/Pyrogrammod)
# toh ye direct kaam karega. Agar error aaye toh check karna ki tumhara
# Pyrogram version update hai ya nahi.

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true",
                style="success"
            )
        ],
        [
            InlineKeyboardButton(
                "⚙️ ʜᴇʟᴘ",
                callback_data="help_menu",
                style="primary"
            ),
            InlineKeyboardButton(
                "💬 ꜱᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_CHAT,
                style="primary"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 ᴜᴘᴅᴀᴛᴇꜱ",
                url=config.UPDATES_CHANNEL,
                style="primary"
            ),
            InlineKeyboardButton(
                "👨‍💻 ᴅᴇᴠ",
                url="https://t.me/YO_UR_OFFICIAL_CRUSH",
                style="primary"
            )
        ]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 ᴍᴜꜱɪᴄ", callback_data="help_music", style="primary"),
            InlineKeyboardButton("⏯ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="help_controls", style="primary")
        ],
        [
            InlineKeyboardButton("🎛 ᴇꜰꜰᴇᴄᴛꜱ", callback_data="help_effects", style="primary"),
            InlineKeyboardButton("🛡 ᴀᴅᴍɪɴ", callback_data="help_admin", style="primary")
        ],
        [
            InlineKeyboardButton("📜 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="all_commands", style="success")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="back_start", style="danger")
        ]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help_menu", style="danger")
        ]
    ])

def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=8) if q.now_playing else "▭" * 8
    
    timer_btn = InlineKeyboardButton(
        f"✨ {elapsed_str} {bar} {dur_str}",
        callback_data="cb_timer",
        style="primary"
    )
    
    pause_text = "▶️ ʀᴇꜱᴜᴍᴇ" if q.paused else "⏸ ᴘᴀᴜꜱᴇ"
    pause_btn = InlineKeyboardButton(
        pause_text,
        callback_data="cb_pause",
        style="success" if q.paused else "primary"
    )
    skip_btn = InlineKeyboardButton(
        "⏭ ꜱᴋɪᴘ",
        callback_data="cb_skip",
        style="primary"
    )
    
    loop_text = "🔁 ʟᴏᴏᴘ ᴏꜰꜰ" if q.loop == 0 else ("🔂 ʟᴏᴏᴘ ᴏɴᴇ" if q.loop == 1 else "🔁 ʟᴏᴏᴘ ᴀʟʟ")
    loop_btn = InlineKeyboardButton(
        loop_text,
        callback_data="cb_loop",
        style="primary"
    )
    stop_btn = InlineKeyboardButton(
        "⏹ ꜱᴛᴏᴘ",
        callback_data="cb_stop",
        style="danger"
    )
    more_btn = InlineKeyboardButton(
        "🎵 ᴍᴏʀᴇ",
        callback_data="cb_more",
        style="primary"
    )
    
    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, skip_btn],
        [loop_btn, stop_btn],
        [more_btn]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "❌ ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ǫᴜᴇᴜᴇ",
                callback_data=f"cb_del_{track_hash}",
                style="danger"
            )
        ]
    ])
