import base64
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.keyboards import start_keyboard, help_main_keyboard, help_back_keyboard
from SunloMusic.database import add_user
from SunloMusic.ytdlp import extract_audio
from SunloMusic.decorators import catch_errors

START_CAPTION = (
    "<b>🎶 Welcome to {bot_name}!</b>\n\n"
    "<i>Your ultimate ultra-fast Voice Chat Music Companion.</i>\n\n"
    "✨ <b>Features:</b>\n"
    "• High-Quality Audio & Video Streaming\n"
    "• Zero Lag & 24/7 Uptime\n"
    "• Premium User Interface\n\n"
    "👨‍💻 <b>Developer:</b> <a href='https://t.me/YO_UR_OFFICIAL_CRUSH'>Sakil</a>\n"
    "📢 <b>Updates:</b> <a href='{channel}'>Vip Sakil Bio</a>"
)

@bot.on_message(filters.command("start") & filters.private)
@catch_errors
async def start_cmd(_, m):
    await add_user(m.from_user.id, m.from_user.first_name)
    
    log_text = (
        f"<b>🚀 New User Started Bot!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Name:</b> {m.from_user.mention}\n"
        f"🆔 <b>ID:</b> <code>{m.from_user.id}</code>\n"
        f"🔗 <b>Username:</b> @{m.from_user.username if m.from_user.username else 'None'}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    if config.LOGGER_ID:
        try: await bot.send_message(config.LOGGER_ID, log_text)
        except: pass
    if config.OWNER_ID:
        try: await bot.send_message(config.OWNER_ID, log_text)
        except: pass

    if len(m.command) > 1 and m.command[1].startswith("dl_"):
        b64_query = m.command[1][3:]
        try:
            query = base64.urlsafe_b64decode(b64_query + "=" * (-len(b64_query) % 4)).decode()
            await m.reply_text(
                f"📥 <b>Download Menu</b>\n\nSong: <b>{query}</b>\nChoose format:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎵 Audio", callback_data=f"dla_{b64_query}"), InlineKeyboardButton("🎬 Video", callback_data=f"dlv_{b64_query}")]
                ])
            )
            return
        except Exception: pass
    caption = START_CAPTION.format(bot_name=config.BOT_NAME, channel=config.UPDATES_CHANNEL)
    try:
        if config.START_IMG: await m.reply_photo(config.START_IMG, caption=caption, reply_markup=start_keyboard())
        else: raise Exception()
    except Exception: await m.reply_text(caption, reply_markup=start_keyboard())

@bot.on_message(filters.command(["ping", "help"]))
@catch_errors
async def ping_help_cmd(_, m):
    if m.command[0] == "ping":
        return await m.reply_text("🏓 <b>Pong! System is active.</b>")
    
    # ✅ Better /help — shows help menu directly
    await m.reply_text(
        "<b>❓ SunloMusic Help</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "Choose a category to explore commands:\n\n"
        "💡 Use <code>/allcommand</code> for full list",
        reply_markup=help_main_keyboard()
    )
