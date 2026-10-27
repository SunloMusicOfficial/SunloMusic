from pyrogram import filters
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.keyboards import start_keyboard, controls_keyboard

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, m):
    caption = (
        f"<b>🎶 Welcome to {config.BOT_NAME}!</b>\n\n"
        f"Ultra-fast VC Music Bot. Add me to your group and play songs instantly.\n\n"
        f"👨‍💻 <b>Owner:</b> Sakil\n"
        f"📢 <b>Channel:</b> <a href='{config.UPDATES_CHANNEL}'>Vip Sakil Bio</a>"
    )
    if config.START_IMG:
        await m.reply_photo(config.START_IMG, caption=caption, reply_markup=start_keyboard())
    else:
        await m.reply_text(caption, reply_markup=start_keyboard(), disable_web_page_preview=True)

@bot.on_message(filters.command("ping"))
async def ping_cmd(_, m):
    await m.reply_text("🏓 <b>Pong! Bot is alive.</b>")

@bot.on_callback_query(filters.regex("^help_menu"))
async def help_cb(_, cq: CallbackQuery):
    text = (
        "<b>🎧 SunloMusic Commands</b>\n\n"
        "🎵 <b>Music:</b>\n"
        "/play [song] - Play audio\n"
        "/vplay [song] - Play video\n"
        "/song [song] - Get download link\n\n"
        "⏯ <b>Controls:</b>\n"
        "/pause, /resume, /skip, /stop\n"
        "/queue - View current queue\n\n"
        "🛡 <b>Admin:</b>\n"
        "/auth, /unauth (Authorize chat)\n"
        "/broadcast, /stats (Sudo only)"
    )
    await cq.message.edit_text(text)
    await cq.answer()
