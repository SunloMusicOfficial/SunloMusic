from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.config import config

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true"), InlineKeyboardButton("📢 Channel", url=config.UPDATES_CHANNEL)],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu"), InlineKeyboardButton("💬 Support", url=config.SUPPORT_CHAT)]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Music", callback_data="help_music"), InlineKeyboardButton("⏯ Controls", callback_data="help_controls")],
        [InlineKeyboardButton("🛡 Admin", callback_data="help_admin")],
        [InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Help", callback_data="help_menu")]])

def controls_keyboard(loop_status: int = 0) -> InlineKeyboardMarkup:
    loop_text = "🔁 AUTO OFF" if loop_status == 0 else ("🔂 AUTO ONE" if loop_status == 1 else "🔁 AUTO ALL")
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ PAUSE", callback_data="cb_pause"),
            InlineKeyboardButton("⏭ SKIP", callback_data="cb_skip")
        ],
        [
            InlineKeyboardButton(loop_text, callback_data="cb_loop"),
            InlineKeyboardButton("⏹ STOP", callback_data="cb_stop")
        ],
        [
            InlineKeyboardButton("🎵 MORE", callback_data="cb_more")
        ]
    ])
