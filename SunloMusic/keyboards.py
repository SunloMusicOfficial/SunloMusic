from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from pyrogram.enums import ButtonStyle
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar
from SunloMusic.queues import AUTO_DJ_CHATS

def start_keyboard() -> InlineKeyboardMarkup:
    WEB_APP_URL = "https://sunlomusic.onrender.com/app"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ ᴏᴘᴇɴ ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ ✨", web_app=WebAppInfo(url=WEB_APP_URL), style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("🚀 ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ 🚀", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true", style=ButtonStyle.PRIMARY)],
        [
            InlineKeyboardButton("⚙️ ʜᴇʟᴘ", callback_data="help_menu", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT, style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=config.UPDATES_CHANNEL, style=ButtonStyle.DANGER),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠ", url="https://t.me/YO_UR_OFFICIAL_CRUSH", style=ButtonStyle.SUCCESS)
        ]
    ])

def help_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 ᴍᴜꜱɪᴄ", callback_data="help_music", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⏯ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="help_controls", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("🎛 ᴇꜰꜰᴇᴄᴛꜱ", callback_data="help_effects", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🛡 ᴀᴅᴍɪɴ", callback_data="help_admin", style=ButtonStyle.DANGER)
        ],
        [InlineKeyboardButton("📜 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="all_commands", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_start", style=ButtonStyle.DANGER)]
    ])

def help_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help_menu", style=ButtonStyle.DANGER)]
    ])

# ✅ Clean & Colorful Premium Player
def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    
    # Clean Progress Bar
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=7) if q.now_playing else "▭" * 7
    
    timer_btn = InlineKeyboardButton(
        f"✨ {elapsed_str} {bar} {dur_str} ✨", 
        callback_data="cb_timer", 
        style=ButtonStyle.PRIMARY
    )
    
    pause_text = "🔵 ʀᴇꜱᴜᴍᴇ" if q.paused else "🟡 ᴘᴀᴜꜱᴇ"
    pause_btn = InlineKeyboardButton(pause_text, callback_data="cb_pause", style=ButtonStyle.SUCCESS if q.paused else ButtonStyle.PRIMARY)
    
    skip_btn = InlineKeyboardButton("🔵 ꜱᴋɪᴘ", callback_data="cb_skip", style=ButtonStyle.PRIMARY)
    
    loop_status = "ᴏɴ" if q.loop > 0 else "ᴏꜰꜰ"
    loop_btn = InlineKeyboardButton(f"🟢 ʟᴏᴏᴘ: {loop_status}", callback_data="cb_loop", style=ButtonStyle.SUCCESS if q.loop > 0 else ButtonStyle.PRIMARY)
    
    auto_status = "ᴏɴ" if q.chat_id in AUTO_DJ_CHATS else "ᴏꜰꜰ"
    auto_btn = InlineKeyboardButton(f"🟢 ᴀᴜᴛᴏ: {auto_status}", callback_data="cb_autoplay", style=ButtonStyle.SUCCESS if q.chat_id in AUTO_DJ_CHATS else ButtonStyle.PRIMARY)
    
    more_btn = InlineKeyboardButton("🟣 ᴍᴏʀᴇ", callback_data="cb_more", style=ButtonStyle.PRIMARY)
    
    stop_btn = InlineKeyboardButton("🔴 ᴄʟᴏꜱᴇ", callback_data="cb_stop", style=ButtonStyle.DANGER)

    # 2-Column Layout
    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, skip_btn],
        [loop_btn, auto_btn],
        [more_btn, stop_btn]
    ])

def more_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 ǫᴜᴇᴜᴇ", callback_data="cb_q_show", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🔵 ꜱʜᴜꜰꜰʟᴇ", callback_data="cb_q_shuffle", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🟡 ᴇxᴘᴏʀᴛ", callback_data="cb_q_export", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🟣 ꜱᴇᴇᴋ ɪɴꜰᴏ", callback_data="cb_seek_info", style=ButtonStyle.PRIMARY)
        ],
        [InlineKeyboardButton("🔴 ʙᴀᴄᴋ ᴛᴏ ᴘʟᴀʏᴇʀ", callback_data="cb_back_player", style=ButtonStyle.DANGER)]
    ])

def settings_keyboard(tts_on: bool, vsearch_on: bool) -> InlineKeyboardMarkup:
    tts_text = "🟢 ꜱᴜɴʟᴏ ᴀɪ: ᴏɴ" if tts_on else "🔴 ꜱᴜɴʟᴏ ᴀɪ: ᴏꜰꜰ"
    vs_text = "🟢 ᴠᴏɪᴄᴇ ꜱᴇᴀʀᴄʜ: ᴏɴ" if vsearch_on else "🔴 ᴠᴏɪᴄᴇ ꜱᴇᴀʀᴄʜ: ᴏꜰꜰ"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tts_text, callback_data="toggle_tts", style=ButtonStyle.SUCCESS if tts_on else ButtonStyle.DANGER)],
        [InlineKeyboardButton(vs_text, callback_data="toggle_vsearch", style=ButtonStyle.SUCCESS if vsearch_on else ButtonStyle.DANGER)],
        [InlineKeyboardButton("🔵 ᴄʟᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="close_settings", style=ButtonStyle.PRIMARY)]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ǫᴜᴇᴜᴇ", callback_data=f"cb_del_{track_hash}", style=ButtonStyle.DANGER)]
    ])
