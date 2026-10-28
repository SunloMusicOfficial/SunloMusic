from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true"), InlineKeyboardButton("📢 Channel", url=config.UPDATES_CHANNEL)],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu"), InlineKeyboardButton("💬 Support", url=config.SUPPORT_CHAT)]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Music", callback_data="help_music"), InlineKeyboardButton("⏯ Controls", callback_data="help_controls")],
        [InlineKeyboardButton("🎛 Effects", callback_data="help_effects"), InlineKeyboardButton("🛡 Admin", callback_data="help_admin")],
        [InlineKeyboardButton("📜 All Commands", callback_data="all_commands")],
        [InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Help", callback_data="help_menu")]])

def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=8) if q.now_playing else "━" * 8
    timer_btn = InlineKeyboardButton(f"{elapsed_str} 🎵 {bar} {dur_str}", callback_data="cb_timer")
    
    pause_text = "▶️ ʀᴇsᴜᴍᴇ" if q.paused else "⏸️ ᴘᴀᴜsᴇ"
    pause_btn = InlineKeyboardButton(pause_text, callback_data="cb_pause")
    skip_btn = InlineKeyboardButton("⏭️ sᴋɪᴘ", callback_data="cb_skip")
    
    loop_text = "🔁 ʟᴏᴏᴘ ᴏғғ" if q.loop == 0 else ("🔂 ʟᴏᴏᴘ ᴏɴᴇ" if q.loop == 1 else "🔁 ʟᴏᴏᴘ ᴀʟʟ")
    loop_btn = InlineKeyboardButton(loop_text, callback_data="cb_loop")
    stop_btn = InlineKeyboardButton("⏹️ sᴛᴏᴘ", callback_data="cb_stop")
    more_btn = InlineKeyboardButton("🎵 ᴍᴏʀᴇ", callback_data="cb_more")
    
    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, skip_btn],
        [loop_btn, stop_btn],
        [more_btn]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ǫᴜᴇᴜᴇ", callback_data=f"cb_del_{track_hash}")]
    ])
