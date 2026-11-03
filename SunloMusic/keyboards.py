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

# ✅ EXACT PILL SHAPE LAYOUT (Same as MusicGenieX)
def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=7) if q.now_playing else "─" * 7
    
    # 1. Timer Bar (Full Width)
    timer_btn = InlineKeyboardButton(
        f"{elapsed_str}  {bar}○  {dur_str}", 
        callback_data="cb_timer", 
        style=ButtonStyle.PRIMARY
    )
    
    # 2. Control Buttons (3 Columns, Short Text, Auto Round)
    pause_text = "▶️ RESUME" if q.paused else "⏸ PAUSE"
    pause_btn = InlineKeyboardButton(pause_text, callback_data="cb_pause", style=ButtonStyle.SUCCESS if q.paused else ButtonStyle.PRIMARY)
    skip_btn = InlineKeyboardButton("⏭ SKIP", callback_data="cb_skip", style=ButtonStyle.PRIMARY)
    stop_btn = InlineKeyboardButton("⏹ STOP", callback_data="cb_stop", style=ButtonStyle.DANGER)
    
    # 3. Autoplay (Full Width Pill)
    auto_status = "ON" if q.chat_id in AUTO_DJ_CHATS else "OFF"
    auto_btn = InlineKeyboardButton(f"🔄 AUTOPLAY : {auto_status}", callback_data="cb_autoplay", style=ButtonStyle.SUCCESS if q.chat_id in AUTO_DJ_CHATS else ButtonStyle.PRIMARY)
    
    # 4. Owner & Group (2 Columns, Short Text)
    owner_btn = InlineKeyboardButton("👑 OWNER", url="https://t.me/YO_UR_OFFICIAL_CRUSH", style=ButtonStyle.PRIMARY)
    group_btn = InlineKeyboardButton("💖 GROUP", url="https://t.me/SunloMusicOfficial", style=ButtonStyle.PRIMARY)
    
    # 5. Close (Full Width Pill)
    close_btn = InlineKeyboardButton("🗑 CLOSE", callback_data="cb_close", style=ButtonStyle.DANGER)

    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, skip_btn, stop_btn], 
        [auto_btn],
        [owner_btn, group_btn],
        [close_btn]
    ])

def more_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 QUEUE", callback_data="cb_q_show", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🔀 SHUFFLE", callback_data="cb_q_shuffle", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("📁 EXPORT", callback_data="cb_q_export", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⏩ SEEK", callback_data="cb_seek_info", style=ButtonStyle.SUCCESS)
        ],
        [InlineKeyboardButton("🔙 BACK", callback_data="cb_back_player", style=ButtonStyle.DANGER)]
    ])

def settings_keyboard(tts_on: bool, vsearch_on: bool) -> InlineKeyboardMarkup:
    tts_text = "🟢 SUNLO AI: ON" if tts_on else "🔴 SUNLO AI: OFF"
    vs_text = "🟢 VOICE: ON" if vsearch_on else "🔴 VOICE: OFF"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tts_text, callback_data="toggle_tts", style=ButtonStyle.SUCCESS if tts_on else ButtonStyle.DANGER)],
        [InlineKeyboardButton(vs_text, callback_data="toggle_vsearch", style=ButtonStyle.SUCCESS if vsearch_on else ButtonStyle.DANGER)],
        [InlineKeyboardButton("🔙 CLOSE", callback_data="close_settings", style=ButtonStyle.PRIMARY)]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ REMOVE", callback_data=f"cb_del_{track_hash}", style=ButtonStyle.DANGER)]
    ])
