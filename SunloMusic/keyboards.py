from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar

# ✅ Safe Import for Colorful Buttons (Kurigram/Pyrogrammod)
try:
    from pyrogram.types import KeyboardButtonStyle
except ImportError:
    KeyboardButtonStyle = None

def start_keyboard() -> InlineKeyboardMarkup:
    WEB_APP_URL = "https://sunlomusic.onrender.com/app"
    
    # ✅ Safe check: Agar library support karti hai tabhi style lagao
    style_primary = KeyboardButtonStyle(bg_primary=True) if KeyboardButtonStyle else None
    style_success = KeyboardButtonStyle(bg_success=True) if KeyboardButtonStyle else None
    style_danger = KeyboardButtonStyle(bg_danger=True) if KeyboardButtonStyle else None
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ ᴏᴘᴇɴ ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ ✨", web_app=WebAppInfo(url=WEB_APP_URL), style=style_primary)],
        [InlineKeyboardButton("🚀 ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ 🚀", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true", style=style_success)],
        [
            InlineKeyboardButton("⚙️ ʜᴇʟᴘ", callback_data="help_menu", style=style_primary),
            InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT, style=style_primary)
        ],
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=config.UPDATES_CHANNEL, style=style_primary),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠ", url="https://t.me/YO_UR_OFFICIAL_CRUSH", style=style_danger)
        ]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    style_primary = KeyboardButtonStyle(bg_primary=True) if KeyboardButtonStyle else None
    style_success = KeyboardButtonStyle(bg_success=True) if KeyboardButtonStyle else None
    style_danger = KeyboardButtonStyle(bg_danger=True) if KeyboardButtonStyle else None

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 ᴍᴜꜱɪᴄ", callback_data="help_music", style=style_primary),
            InlineKeyboardButton("⏯ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="help_controls", style=style_primary)
        ],
        [
            InlineKeyboardButton("🎛 ᴇꜰꜰᴇᴄᴛꜱ", callback_data="help_effects", style=style_success),
            InlineKeyboardButton("🛡 ᴀᴅᴍɪɴ", callback_data="help_admin", style=style_danger)
        ],
        [InlineKeyboardButton("📜 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="all_commands", style=style_success)],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="back_start", style=style_danger)]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    style_danger = KeyboardButtonStyle(bg_danger=True) if KeyboardButtonStyle else None
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help_menu", style=style_danger)]
    ])

def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=8) if q.now_playing else "▭" * 8
    
    style_primary = KeyboardButtonStyle(bg_primary=True) if KeyboardButtonStyle else None
    style_success = KeyboardButtonStyle(bg_success=True) if KeyboardButtonStyle else None
    style_danger = KeyboardButtonStyle(bg_danger=True) if KeyboardButtonStyle else None
    
    timer_btn = InlineKeyboardButton(f"✨ {elapsed_str} {bar} {dur_str} ✨", callback_data="cb_timer", style=style_primary)
    
    pause_text = "▶️ ʀᴇꜱᴜᴍᴇ" if q.paused else "⏸ ᴘᴀᴜꜱᴇ"
    pause_btn = InlineKeyboardButton(pause_text, callback_data="cb_pause", style=style_success if q.paused else style_primary)
    
    skip_btn = InlineKeyboardButton("⏭ ꜱᴋɪᴘ", callback_data="cb_skip", style=style_primary)
    
    loop_text = "🔁 ʟᴏᴏᴘ ᴏꜰꜰ" if q.loop == 0 else ("🔂 ʟᴏᴏᴘ ᴏɴᴇ" if q.loop == 1 else "🔁 ʟᴏᴏᴘ ᴀʟʟ")
    loop_btn = InlineKeyboardButton(loop_text, callback_data="cb_loop", style=style_primary)
    
    stop_btn = InlineKeyboardButton("⏹ ꜱᴛᴏᴘ", callback_data="cb_stop", style=style_danger)
    more_btn = InlineKeyboardButton("🎵 ᴍᴏʀᴇ", callback_data="cb_more", style=style_primary)
    
    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, skip_btn],
        [loop_btn, stop_btn],
        [more_btn]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    style_danger = KeyboardButtonStyle(bg_danger=True) if KeyboardButtonStyle else None
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ǫᴜᴇᴜᴇ", callback_data=f"cb_del_{track_hash}", style=style_danger)]
    ])
