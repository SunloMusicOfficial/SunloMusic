from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from pyrogram.enums import ButtonStyle  # ✅ Kurigram ka sahi module
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar

def start_keyboard() -> InlineKeyboardMarkup:
    WEB_APP_URL = "https://sunlomusic.onrender.com/app"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ ᴏᴘᴇɴ ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ ✨", web_app=WebAppInfo(url=WEB_APP_URL), style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("🚀 ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ 🚀", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true", style=ButtonStyle.SUCCESS)],
        [
            InlineKeyboardButton("⚙️ ʜᴇʟᴘ", callback_data="help_menu", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT, style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=config.UPDATES_CHANNEL, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠ", url="https://t.me/YO_UR_OFFICIAL_CRUSH", style=ButtonStyle.DANGER)
        ]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 ᴍᴜꜱɪᴄ", callback_data="help_music", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⏯ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="help_controls", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🎛 ᴇꜰꜰᴇᴄᴛꜱ", callback_data="help_effects", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🛡 ᴀᴅᴍɪɴ", callback_data="help_admin", style=ButtonStyle.DANGER)
        ],
        [InlineKeyboardButton("📜 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="all_commands", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="back_start", style=ButtonStyle.DANGER)]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help_menu", style=ButtonStyle.DANGER)]
    ])

def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=8) if q.now_playing else "▭" * 8
    
    timer_btn = InlineKeyboardButton(f"✨ {elapsed_str} {bar} {dur_str} ✨", callback_data="cb_timer", style=ButtonStyle.PRIMARY)
    
    pause_text = "▶️ ʀᴇꜱᴜᴍᴇ" if q.paused else "⏸ ᴘᴀᴜꜱᴇ"
    pause_btn = InlineKeyboardButton(pause_text, callback_data="cb_pause", style=ButtonStyle.SUCCESS if q.paused else ButtonStyle.PRIMARY)
    
    skip_btn = InlineKeyboardButton("⏭ ꜱᴋɪᴘ", callback_data="cb_skip", style=ButtonStyle.PRIMARY)
    
    loop_text = "🔁 ʟᴏᴏᴘ ᴏꜰꜰ" if q.loop == 0 else ("🔂 ʟᴏᴏᴘ ᴏɴᴇ" if q.loop == 1 else "🔁 ʟᴏᴏᴘ ᴀʟʟ")
    loop_btn = InlineKeyboardButton(loop_text, callback_data="cb_loop", style=ButtonStyle.PRIMARY)
    
    stop_btn = InlineKeyboardButton("⏹ ꜱᴛᴏᴘ", callback_data="cb_stop", style=ButtonStyle.DANGER)
    more_btn = InlineKeyboardButton("🎵 ᴍᴏʀᴇ", callback_data="cb_more", style=ButtonStyle.PRIMARY)
    
    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, skip_btn],
        [loop_btn, stop_btn],
        [more_btn]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ǫᴜᴇᴜᴇ", callback_data=f"cb_del_{track_hash}", style=ButtonStyle.DANGER)]
    ])
