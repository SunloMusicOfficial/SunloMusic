from pyrogram import filters
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.keyboards import start_keyboard
from SunloMusic.database import add_user

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, m):
    await add_user(m.from_user.id, m.from_user.first_name)
    caption = (
        f"<b>🎶 Welcome to {config.BOT_NAME}!</b>\n\n"
        f"Ultra-fast VC Music Bot. Add me to your group and play songs instantly.\n\n"
        f"👨‍💻 <b>Owner:</b> Sakil\n"
        f"📢 <b>Channel:</b> <a href='{config.UPDATES_CHANNEL}'>Vip Sakil Bio</a>"
    )
    try:
        if config.START_IMG:
            await m.reply_photo(config.START_IMG, caption=caption, reply_markup=start_keyboard())
        else:
            raise Exception("No Image")
    except Exception:
        await m.reply_text(caption, reply_markup=start_keyboard())

@bot.on_message(filters.command(["ping", "help"]))
async def ping_help_cmd(_, m):
    if m.command[0] == "ping":
        await m.reply_text("🏓 <b>Pong! Bot is alive.</b>")
    else:
        await m.reply_text("🎧 <b>Commands:</b>\n\n/play [song]\n/vplay [song]\n/song [song]\n/pause, /resume, /skip, /stop\n/queue\n/auth (Admin)", reply_markup=start_keyboard())

# ✅ Added back help menu callback
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
