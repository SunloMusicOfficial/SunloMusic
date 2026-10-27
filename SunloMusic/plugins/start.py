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

HELP_MENU_CAPTION = (
    "<b>🎧 SunloMusic — Help & Guide</b>\n\n"
    "<blockquote>Explore the commands below to master the bot. Choose a category to view detailed guides.</blockquote>"
)

@bot.on_message(filters.command("start") & filters.private)
@catch_errors
async def start_cmd(_, m):
    await add_user(m.from_user.id, m.from_user.first_name)
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

@bot.on_message(filters.command("start") & filters.group)
@catch_errors
async def start_group_cmd(_, m):
    try: await m.delete()
    except: pass
    text = f"👋 <b>Hello {m.from_user.first_name}!</b>\n\nI am {config.BOT_NAME}, an ultra-fast VC Music Bot.\nUse <code>/play [song]</code> to start playing in this group."
    await m.reply_text(text, reply_markup=start_keyboard())

@bot.on_message(filters.command(["ping", "help"]))
@catch_errors
async def ping_help_cmd(_, m):
    if m.command[0] == "ping": return await m.reply_text("🏓 <b>Pong! System is active.</b>")
    try:
        if config.START_IMG: await m.reply_photo(config.START_IMG, caption=HELP_MENU_CAPTION, reply_markup=help_main_keyboard())
        else: raise Exception()
    except Exception: await m.reply_text(HELP_MENU_CAPTION, reply_markup=help_main_keyboard())

@bot.on_callback_query(filters.regex("^help_"))
@catch_errors
async def help_callbacks(_, cq: CallbackQuery):
    data = cq.data
    if data == "help_menu": text, kb = HELP_MENU_CAPTION, help_main_keyboard()
    elif data == "help_music": text, kb = "<b>🎵 Music Commands</b>\n\n• <code>/play [song]</code>\n• <code>/vplay [song]</code>\n• <code>/song [song]</code>", help_back_keyboard()
    elif data == "help_controls": text, kb = "<b>⏯ Playback Controls</b>\n\n• <code>/pause</code>, <code>/resume</code>\n• <code>/skip</code>\n• <code>/stop</code>\n• <code>/queue</code>\n• <code>/loop</code>", help_back_keyboard()
    elif data == "help_admin": text, kb = "<b>🛡 Admin Commands</b>\n\n• <code>/auth</code>\n• <code>/broadcast</code>\n• <code>/stats</code>", help_back_keyboard()
    try:
        if cq.message.photo: await cq.message.edit_caption(caption=text, reply_markup=kb)
        else: await cq.message.edit_text(text=text, reply_markup=kb)
    except: pass
    await cq.answer()

@bot.on_callback_query(filters.regex("^back_start"))
@catch_errors
async def back_start_cb(_, cq: CallbackQuery):
    caption = START_CAPTION.format(bot_name=config.BOT_NAME, channel=config.UPDATES_CHANNEL)
    try:
        if cq.message.photo: await cq.message.edit_caption(caption=caption, reply_markup=start_keyboard())
        else: await cq.message.edit_text(text=caption, reply_markup=start_keyboard())
    except: pass
    await cq.answer("Returned to main menu.")

@bot.on_callback_query(filters.regex("^dl[av]_"))
@catch_errors
async def dl_callback(_, cq: CallbackQuery):
    fmt = "audio" if cq.data.startswith("dla_") else "video"
    b64_query = cq.data[4:]
    try: query = base64.urlsafe_b64decode(b64_query + "=" * (-len(b64_query) % 4)).decode()
    except: return await cq.answer("Invalid link", show_alert=True)
    await cq.message.edit_text(f"⏳ Fetching <b>{query}</b>...")
    info = await extract_audio(query)
    if not info or not info.get("url"): return await cq.message.edit_text("❌ Failed to fetch.")
    url = info["url"]
    caption = f"🎶 <b>{info['title']}</b>\n\n🤖 @{config.BOT_USERNAME.strip('@')}"
    try:
        if fmt == "video": await cq.message.reply_video(url, caption=caption)
        else: await cq.message.reply_audio(url, caption=caption, title=info['title'])
        await cq.message.delete()
    except Exception as e: await cq.message.edit_text(f"❌ Error: {e}")
