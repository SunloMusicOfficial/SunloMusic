from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from pyrogram.enums import ButtonStyle
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar

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

def player_keyboard(q, elapsed: int = 0) -> InlineKeyboardMarkup:
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=8) if q.now_playing else "▭" * 8
    
    timer_btn = InlineKeyboardButton(f"✨ {elapsed_str} {bar} {dur_str} ✨", callback_data="cb_timer", style=ButtonStyle.PRIMARY)
    pause_text = "▶️ ʀᴇꜱᴜᴍᴇ" if q.paused else "⏸ ᴘᴀᴜꜱᴇ"
    pause_btn = InlineKeyboardButton(pause_text, callback_data="cb_pause", style=ButtonStyle.SUCCESS)
    loop_text = "🔁 ʟᴏᴏᴘ ᴏꜰꜰ" if q.loop == 0 else ("🔂 ʟᴏᴏᴘ ᴏɴᴇ" if q.loop == 1 else "🔁 ʟᴏᴏᴘ ᴀʟʟ")
    loop_btn = InlineKeyboardButton(loop_text, callback_data="cb_loop", style=ButtonStyle.SUCCESS)
    skip_btn = InlineKeyboardButton("⏭ ꜱᴋɪᴘ", callback_data="cb_skip", style=ButtonStyle.DANGER)
    stop_btn = InlineKeyboardButton("⏹ ꜱᴛᴏᴘ", callback_data="cb_stop", style=ButtonStyle.DANGER)
    more_btn = InlineKeyboardButton("🎵 ᴍᴏʀᴇ", callback_data="cb_more", style=ButtonStyle.PRIMARY)
    
    return InlineKeyboardMarkup([
        [timer_btn],
        [pause_btn, loop_btn],
        [skip_btn, stop_btn],
        [more_btn]
    ])

def more_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 ǫᴜᴇᴜᴇ", callback_data="cb_q_show", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🔀 ꜱʜᴜꜰꜰʟᴇ", callback_data="cb_q_shuffle", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("📁 ᴇxᴘᴏʀᴛ", callback_data="cb_q_export", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⏩ ꜱᴇᴇᴋ ɪɴꜰᴏ", callback_data="cb_seek_info", style=ButtonStyle.SUCCESS)
        ],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴘʟᴀʏᴇʀ", callback_data="cb_back_player", style=ButtonStyle.DANGER)]
    ])

# ✅ UPDATED: SunloMusic AI Text
def settings_keyboard(tts_on: bool, vsearch_on: bool) -> InlineKeyboardMarkup:
    tts_text = "🟢 ꜱᴜɴʟᴏᴍᴜꜱɪᴄ ᴀɪ: ᴏɴ" if tts_on else "🔴 ꜱᴜɴʟᴏᴍᴜꜱɪᴄ ᴀɪ: ᴏꜰꜰ"
    vs_text = "🟢 ᴠᴏɪᴄᴇ ꜱᴇᴀʀᴄʜ: ᴏɴ" if vsearch_on else "🔴 ᴠᴏɪᴄᴇ ꜱᴇᴀʀᴄʜ: ᴏꜰꜰ"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tts_text, callback_data="toggle_tts", style=ButtonStyle.SUCCESS if tts_on else ButtonStyle.DANGER)],
        [InlineKeyboardButton(vs_text, callback_data="toggle_vsearch", style=ButtonStyle.SUCCESS if vsearch_on else ButtonStyle.DANGER)],
        [InlineKeyboardButton("🔙 ᴄʟᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="close_settings", style=ButtonStyle.PRIMARY)]
    ])

def queue_add_keyboard(track_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ǫᴜᴇᴜᴇ", callback_data=f"cb_del_{track_hash}", style=ButtonStyle.DANGER)]
    ])
