from pyrogram import filters
from pyrogram.types import CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.keyboards import start_keyboard, help_main_keyboard, help_back_keyboard
from SunloMusic.database import add_user

# ✅ Yahan 'Sakil' ko clickable link banaya gaya hai
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

HELP_MENU_CAPTION = (
    "<b>🎧 SunloMusic — Help & Guide</b>\n\n"
    "<blockquote>Explore the commands below to master the bot. Choose a category to view detailed guides.</blockquote>"
)

HELP_MUSIC = (
    "<b>🎵 Music Commands</b>\n\n"
    "• <code>/play [song name/url]</code> - Play audio in VC\n"
    "• <code>/vplay [song name/url]</code> - Play video in VC\n"
    "• <code>/song [song name]</code> - Download audio directly\n"
    "• <code>/radio [hindi/english]</code> - Play live radio\n\n"
    "<i>Tip: You can also reply to an audio file or text link with /play.</i>"
)

HELP_CONTROLS = (
    "<b>⏯ Playback Controls</b>\n\n"
    "• <code>/pause</code> - Pause the stream\n"
    "• <code>/resume</code> - Resume the stream\n"
    "• <code>/skip</code> - Skip to next track\n"
    "• <code>/stop</code> - Stop and leave VC\n"
    "• <code>/queue</code> - View current playlist\n"
    "• <code>/loop [0/1/2]</code> - 0:Off, 1:Track, 2:Queue\n"
    "• <code>/shuffle</code> - Shuffle the queue\n\n"
    "<i>Tip: Admins can also use inline buttons below the playing message.</i>"
)

HELP_ADMIN = (
    "<b>🛡 Admin & Sudo Commands</b>\n\n"
    "<b>For Group Admins:</b>\n"
    "• <code>/auth</code> - Authorize chat to use bot\n"
    "• <code>/unauth</code> - Unauthorize chat\n\n"
    "<b>For Sudo Users:</b>\n"
    "• <code>/stats</code> - Bot usage statistics\n"
    "• <code>/broadcast</code> - Broadcast message to all chats\n"
    "• <code>/addsudo</code> - Reply to user to add as sudo"
)

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, m):
    await add_user(m.from_user.id, m.from_user.first_name)
    caption = START_CAPTION.format(bot_name=config.BOT_NAME, channel=config.UPDATES_CHANNEL)
    try:
        if config.START_IMG:
            await m.reply_photo(config.START_IMG, caption=caption, reply_markup=start_keyboard())
        else: raise Exception()
    except Exception:
        await m.reply_text(caption, reply_markup=start_keyboard())

@bot.on_message(filters.command(["ping", "help"]))
async def ping_help_cmd(_, m):
    if m.command[0] == "ping":
        return await m.reply_text("🏓 <b>Pong! System is active.</b>")
    try:
        if config.START_IMG:
            await m.reply_photo(config.START_IMG, caption=HELP_MENU_CAPTION, reply_markup=help_main_keyboard())
        else: raise Exception()
    except Exception:
        await m.reply_text(HELP_MENU_CAPTION, reply_markup=help_main_keyboard())

@bot.on_callback_query(filters.regex("^help_"))
async def help_callbacks(_, cq: CallbackQuery):
    data = cq.data
    if data == "help_menu":
        text, kb = HELP_MENU_CAPTION, help_main_keyboard()
    elif data == "help_music":
        text, kb = HELP_MUSIC, help_back_keyboard()
    elif data == "help_controls":
        text, kb = HELP_CONTROLS, help_back_keyboard()
    elif data == "help_admin":
        text, kb = HELP_ADMIN, help_back_keyboard()
    
    try:
        if cq.message.photo:
            await cq.message.edit_caption(caption=text, reply_markup=kb)
        else:
            await cq.message.edit_text(text=text, reply_markup=kb)
    except Exception:
        pass
    await cq.answer()

@bot.on_callback_query(filters.regex("^back_start"))
async def back_start_cb(_, cq: CallbackQuery):
    caption = START_CAPTION.format(bot_name=config.BOT_NAME, channel=config.UPDATES_CHANNEL)
    try:
        if cq.message.photo:
            await cq.message.edit_caption(caption=caption, reply_markup=start_keyboard())
        else:
            await cq.message.edit_text(text=caption, reply_markup=start_keyboard())
    except Exception:
        pass
    await cq.answer("Returned to main menu.")
