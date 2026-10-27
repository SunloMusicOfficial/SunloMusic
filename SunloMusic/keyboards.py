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

def player_keyboard(q) -> InlineKeyboardMarkup:
    pause_btn = InlineKeyboardButton("▶️ RESUME" if q.paused else "⏸ PAUSE", callback_data="cb_pause")
    skip_btn = InlineKeyboardButton("⏭ SKIP", callback_data="cb_skip")
    
    # ✅ AUTO ko LOOP kar diya gaya hai
    loop_text = "🔁 LOOP OFF" if q.loop == 0 else ("🔂 LOOP ONE" if q.loop == 1 else "🔁 LOOP ALL")
    loop_btn = InlineKeyboardButton(loop_text, callback_data="cb_loop")
    stop_btn = InlineKeyboardButton("⏹ STOP", callback_data="cb_stop")
    
    more_btn = InlineKeyboardButton("🎵 MORE", callback_data="cb_more")
    
    return InlineKeyboardMarkup([
        [pause_btn, skip_btn],
        [loop_btn, stop_btn],
        [more_btn]
    ])
