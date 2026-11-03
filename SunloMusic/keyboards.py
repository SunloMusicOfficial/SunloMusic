from richgram import rich_button, rich_button_row
from SunloMusic.config import config
from SunloMusic.formatters import format_duration, make_progress_bar
from SunloMusic.queues import AUTO_DJ_CHATS

# ✅ Rich Message Buttons (Gol Shape)
def player_buttons(q, elapsed: int = 0):
    dur_str = format_duration(q.now_playing.duration) if q.now_playing else "00:00"
    elapsed_str = format_duration(elapsed)
    bar = make_progress_bar(elapsed, q.now_playing.duration, length=7) if q.now_playing else "─" * 7
    
    # Timer Bar (Full Width)
    timer_row = rich_button_row(
        rich_button(f"{elapsed_str}  {bar}○  {dur_str}", callback_data="cb_timer", style="primary")
    )
    
    # Line 2: Pause | Autoplay
    pause_btn = rich_button("▶️ RESUME" if q.paused else "⏸️ PAUSE", callback_data="cb_pause", style="success" if q.paused else "primary")
    auto_btn = rich_button(f"🔄 AUTOPLAY: {'ON' if q.chat_id in AUTO_DJ_CHATS else 'OFF'}", callback_data="cb_autoplay", style="success" if q.chat_id in AUTO_DJ_CHATS else "primary")
    row2 = rich_button_row(pause_btn, auto_btn)
    
    # Line 3: Skip | Stop
    skip_btn = rich_button("⏭️ SKIP", callback_data="cb_skip", style="primary")
    stop_btn = rich_button("⏹️ STOP", callback_data="cb_stop", style="danger")
    row3 = rich_button_row(skip_btn, stop_btn)
    
    # Line 4: More Control (Full Width)
    more_btn = rich_button_row(rich_button("🎛 MORE CONTROL", callback_data="cb_more", style="success"))
    
    return timer_row + row2 + row3 + more_btn

# ✅ Start Menu Buttons (Optional, if you want Rich there too)
def start_buttons():
    return (
        rich_button_row(rich_button("✨ OPEN PREMIUM MENU ✨", callback_data="start_menu", style="success")) +
        rich_button_row(rich_button("🚀 ADD ME TO GROUP 🚀", url=f"https://t.me/{config.BOT_USERNAME.strip('@')}?startgroup=true", style="primary")) +
        rich_button_row(
            rich_button("⚙️ HELP", callback_data="help_menu", style="primary"),
            rich_button("💬 SUPPORT", url=config.SUPPORT_CHAT, style="success")
        ) +
        rich_button_row(
            rich_button("📢 UPDATES", url=config.UPDATES_CHANNEL, style="danger"),
            rich_button("👨‍💻 DEV", url="https://t.me/YO_UR_OFFICIAL_CRUSH", style="success")
        )
    )
