from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    WebAppInfo, KeyboardButtonStyle
)
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar

def start_keyboard() -> InlineKeyboardMarkup:
    WEB_APP_URL = "https://sunlomusic.onrender.com/app"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ ᴏᴘᴇɴ ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ ✨", web_app=WebAppInfo(url=WEB_APP_URL), style=KeyboardButtonStyle(bg_primary=True))],
        [InlineKeyboardButton("🚀 ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ 🚀", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true", style=KeyboardButtonStyle(bg_success=True))],
        [
            InlineKeyboardButton("⚙️ ʜᴇʟᴘ", callback_data="help_menu", style=KeyboardButtonStyle(bg_primary=True)),
            InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT, style=KeyboardButtonStyle(bg_primary=True))
        ],
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=config.UPDATES_CHANNEL, style=KeyboardButtonStyle(bg_primary=True)),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠ", url="https://t.me/YO_UR_OFFICIAL_CRUSH", style=KeyboardButtonStyle(bg_danger=True))
        ]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 ᴍᴜꜱɪᴄ", callback_data="help_music", style=KeyboardButtonStyle(bg_primary=True)),
            InlineKeyboardButton("⏯ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="help_controls", style=KeyboardButtonStyle(bg_primary=True))
        ],
        [
            InlineKeyboardButton("🎛 ᴇꜰꜰᴇᴄᴛꜱ", callback_data="help_effects", style=KeyboardButtonStyle(bg_success=True)),
            InlineKeyboardButton("🛡 ᴀᴅᴍɪɴ", callback_data="help_admin", style=KeyboardButtonStyle(bg_danger=True))
        ],
        [InlineKeyboardButton("📜 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="all_commands", style=KeyboardButtonStyle(bg_success=True))],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="back_start", style=KeyboardButtonStyle(bg_danger=True))]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help_menu", style=KeyboardButtonStyle(bg_danger=True))]
    ])

def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=8) if q.now_playing else "▭" * 8
    
    timer_btn = InlineKeyboardButton(f"✨ {elapsed_str} {bar} {dur_str} ✨", callback_data="cb_timer", style=KeyboardButtonStyle(bg_primary=True))
    
    pause_text = "▶️ ʀᴇꜱᴜᴍᴇ" if q.paused else "⏸ ᴘᴀᴜꜱᴇ"
    pause_btn = InlineKeyboardButton(pause_text, callback_data="cb_pause", style=KeyboardButtonStyle(bg_success=True) if q.paused else KeyboardButtonStyle(bg_primary=True))
    
    skip_btn = InlineKeyboardButton("⏭ ꜱᴋɪᴘ", callback_data="cb_skip", style=KeyboardButtonStyle(bg_primary=True))
    
    loop_text = "🔁 ʟᴏᴏᴘ ᴏꜰꜰ" if q.loop == 0 else ("🔂 ʟᴏᴏᴘ ᴏɴᴇ" if q.loop == 1 else "🔁 ʟᴏᴏᴘ ᴀʟʟ")
    loop_btn = InlineKeyboardButton(loop_text, callback_data="cb_loop", style=KeyboardButtonStyle(bg_primary=True))
    
    stop_btn = InlineKeyboardButton("⏹ ꜱᴛᴏᴘ", callback_data="cb_stop", style=KeyboardButtonStyle(bg_danger=True))
    more_btn = InlineKeyboardButton("🎵 ᴍᴏʀᴇ", callback_data="cb_more", style=KeyboardButtonStyle(bg_primary=True))
    
    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, skip_btn],
        [loop_btn, stop_btn],
        [more_btn]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ǫᴜᴇᴜᴇ", callback_data=f"cb_del_{track_hash}", style=KeyboardButtonStyle(bg_danger=True))]
    ])
