import base64
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.keyboards import start_keyboard, help_main_keyboard, help_back_keyboard
from SunloMusic.database import add_user
from SunloMusic.ytdlp import extract_audio
from SunloMusic.logger import LOGGER

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
async def start_group_cmd(_, m):
    try: await m.delete()
    except: pass
    text = f"👋 <b>Hello {m.from_user.first_name}!</b>\n\nI am {config.BOT_NAME}, an ultra-fast VC Music Bot.\nUse <code>/play [song]</code> to start playing in this group."
    await m.reply_text(text, reply_markup=start_keyboard())

@bot.on_message(filters.command(["ping", "help"]))
async def ping_help_cmd(_, m):
    if m.command[0] == "ping":
        return await m.reply_text("🏓 <b>Pong! System is active.</b>")
    try:
        if config.START_IMG: await m.reply_photo(config.START_IMG, caption=HELP_MENU_CAPTION, reply_markup=help_main_keyboard())
        else: raise Exception()
    except Exception: await m.reply_text(HELP_MENU_CAPTION, reply_markup=help_main_keyboard())

@bot.on_callback_query(filters.regex("^dl[av]_"))
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
