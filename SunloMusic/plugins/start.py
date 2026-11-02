import base64, json
from pyrogram import filters, enums
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message, LinkPreviewOptions
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.keyboards import start_keyboard, help_main_keyboard, help_back_keyboard
from SunloMusic.database import add_user
from SunloMusic.ytdlp import extract_audio
from SunloMusic.decorators import catch_errors
from pyrogram.enums import ButtonStyle

# ✅ Added {user_mention} for clickable name
START_CAPTION = (
    "<blockquote expandable>"
    "<b>🎶 Welcome to SunloMusic 🎶</b>\n\n"
    "👋 <b>Hey {user_mention}!</b>\n"
    "✨ <i>Your ultimate ultra-fast Voice Chat Music Companion.</i>\n\n"
    "<b>🔥 ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ:</b>\n"
    "• 🎧 <b>High-Quality</b> Audio & Video\n"
    "• 🚀 <b>Zero Lag</b> & Turbo Speed\n"
    "• 🛡 <b>24/7 Uptime</b> & Stability\n"
    "• 💎 <b>Elegant</b> & Next-Gen UI\n"
    "• 📥 <b>Unlimited Downloads</b> (MP3/MP4)\n"
    "• ⏩ <b>Seek</b> anywhere in the song\n"
    "• 🎯 <b>Interactive</b> Player Controls\n\n"
    "<i>Over 100+ commands available! Tap the buttons below to start.</i>"
    "</blockquote>"
)

@bot.on_message(filters.command("start"))
@catch_errors
async def start_cmd(_, m):
    me = await bot.get_me()
    
    if m.chat.type != enums.ChatType.PRIVATE:
        return await m.reply_text(
            f"👋 <b>Hello {m.from_user.mention}!</b>\n\n"
            f"I am <b>{config.BOT_NAME}</b>.\n"
            f"Click the button below to start me in PM.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start in PM", url=f"https://t.me/{me.username}?start=start", style=ButtonStyle.SUCCESS)]
            ]),
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )

    await add_user(m.from_user.id, m.from_user.first_name)
    
    if len(m.command) > 1 and m.command[1].startswith("dl_"):
        b64_query = m.command[1][3:]
        try:
            query = base64.urlsafe_b64decode(b64_query + "=" * (-len(b64_query) % 4)).decode()
            await m.reply_text(
                f"📥 <b>Download Menu</b>\n\nSong: <b>{query}</b>\nChoose format:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎵 Audio", callback_data=f"dla_{b64_query}", style=ButtonStyle.SUCCESS), InlineKeyboardButton("🎬 Video", callback_data=f"dlv_{b64_query}", style=ButtonStyle.PRIMARY)]
                ]),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
            return
        except Exception: pass
        
    # ✅ Format caption with user's clickable mention
    caption = START_CAPTION.format(user_mention=m.from_user.mention)
    
    try:
        if config.START_IMG: 
            await m.reply_photo(config.START_IMG, caption=caption, reply_markup=start_keyboard(), has_spoiler=True)
        else: 
            raise Exception()
    except Exception: 
        await m.reply_text(caption, reply_markup=start_keyboard(), link_preview_options=LinkPreviewOptions(is_disabled=True))

# Custom Filter
async def web_app_filter(_, __, m: Message):
    return bool(getattr(m, "web_app_data", None))

web_app_data_filter = filters.create(web_app_filter)

@bot.on_message(web_app_data_filter)
@catch_errors
async def web_app_handler(_, m: Message):
    try:
        data = json.loads(m.web_app_data.data)
        cmd = data.get("command")
        
        if cmd == "/help":
            await m.reply_text(
                "<b>❓ SunloMusic Help</b>\n"
                "━━━━━━━━━━━━━\n\n"
                "Choose a category to explore commands:",
                reply_markup=help_main_keyboard()
            )
        elif cmd == "/allcommand":
            from SunloMusic.plugins.help import ALL_COMMANDS_TEXT
            me = await bot.get_me()
            text = ALL_COMMANDS_TEXT.replace("BOT_USERNAME", me.username)
            await m.reply_text(text)
            
    except Exception as e:
        await m.reply_text(f"❌ Error handling Web App data: {e}")

@bot.on_message(filters.command(["ping", "help"]))
@catch_errors
async def ping_help_cmd(_, m):
    if m.command[0] == "ping":
        return await m.reply_text("🏓 <b>Pong! System is active.</b>")
    
    await m.reply_text(
        "<b>❓ SunloMusic Help</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "Choose a category to explore commands:\n\n"
        "💡 Use <code>/allcommand</code> for full list",
        reply_markup=help_main_keyboard()
    )
