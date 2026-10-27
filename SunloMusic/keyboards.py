from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.config import config

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true"),
            InlineKeyboardButton("📢 Channel", url=config.UPDATES_CHANNEL)
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help_menu"),
            InlineKeyboardButton("💬 Support", url=config.SUPPORT_CHAT)
        ]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Music", callback_data="help_music"),
            InlineKeyboardButton("⏯ Controls", callback_data="help_controls")
        ],
        [
            InlineKeyboardButton("🛡 Admin", callback_data="help_admin")
        ],
        [
            InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")
        ]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Help", callback_data="help_menu")]
    ])

def controls_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸", callback_data="cb_pause"),
            InlineKeyboardButton("▶️", callback_data="cb_resume"),
            InlineKeyboardButton("⏭", callback_data="cb_skip"),
            InlineKeyboardButton("⏹", callback_data="cb_stop")
        ],
        [
            InlineKeyboardButton("🔁 Loop", callback_data="cb_loop"),
            InlineKeyboardButton("📋 Queue", callback_data="cb_queue"),
            InlineKeyboardButton("❌ Close", callback_data="cb_close")
        ]
    ])
