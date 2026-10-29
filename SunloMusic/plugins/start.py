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

# ✅ UPDATED ALL COMMANDS LIST
ALL_COMMANDS_TEXT = (
    "<b>📜 SunloMusic — All Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "<b>🎵 Music & Playback</b>\n"
    "• <code>/play</code> - Play audio\n"
    "• <code>/vplay</code> - Play video\n"
    "• <code>/search</code> - Search & play\n"
    "• <code>/song</code> - Download audio\n"
    "• <code>/radio</code> - 24/7 Radio\n"
    "• <code>/autodj on/off</code> - Auto-play queue\n\n"
    
    "<b>⏯️ Controls & Queue</b>\n"
    "• <code>/pause</code> - Pause stream\n"
    "• <code>/resume</code> - Resume stream\n"
    "• <code>/skip</code> - Vote to skip\n"
    "• <code>/stop</code> - Stop & leave VC\n"
    "• <code>/queue</code> - View current queue\n"
    "• <code>/clear</code> - Clear queue\n"
    "• <code>/shuffle</code> - Shuffle queue\n"
    "• <code>/loop</code> - 0:Off, 1:Song, 2:Queue\n"
    "• <code>/sleep</code> - Auto leave timer\n\n"
    
    "<b>🎛️ Audio Effects</b>\n"
    "• <code>/bass</code> - Bass Boost\n"
    "• <code>/8d</code> - 8D Audio\n"
    "• <code>/nightcore</code> - Nightcore\n"
    "• <code>/reset</code> - Normal audio\n\n"
    
    "<b>📂 Playlists & Tools</b>\n"
    "• <code>/save</code> / <code>/load</code> - Personal Playlist\n"
    "• <code>/gsave</code> / <code>/gload</code> - Group Playlist\n"
    "• <code>/lyrics</code> - Fetch lyrics\n"
    "• <code>/karaoke</code> - Live lyrics\n"
    "• <code>/id</code> - Get User/Chat ID\n"
    "• <code>/afk</code> - Set Away status\n"
    "• <code>/leaderboard</code> - Top requesters\n"
    "• <code>/gstats</code> - Group stats\n\n"
    
    "<b>🛡️ Admin & Moderation</b>\n"
    "• <code>/auth</code> - Authorize chat\n"
    "• <code>/broadcast</code> - Broadcast msg (Sudo)\n"
    "• <code>/stats</code> - Bot stats (Sudo)\n"
    "• <code>/addsudo</code> - Add sudo (Sudo)\n"
    "• <code>/tagall</code> - Tag everyone\n"
    "• <code>/purge</code> - Delete messages\n"
    "• <code>/welcome on/off</code> - Welcome msgs\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "<i>Use /help for interactive menu</i>"
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

@bot.on_message(filters.command(["ping", "help", "allcommand"]))
@catch_errors
async def ping_help_cmd(_, m):
    cmd = m.command[0].lower()
    if cmd == "ping": return await m.reply_text("🏓 <b>Pong! System is active.</b>")
    elif cmd == "allcommand": return await m.reply_text(ALL_COMMANDS_TEXT)
    
    try:
        if config.START_IMG: await m.reply_photo(config.START_IMG, caption=HELP_MENU_CAPTION, reply_markup=help_main_keyboard())
        else: raise Exception()
    except Exception: await m.reply_text(HELP_MENU_CAPTION, reply_markup=help_main_keyboard())

@bot.on_callback_query(filters.regex("^help_|^all_commands"))
@catch_errors
async def help_callbacks(_, cq: CallbackQuery):
    data = cq.data
    if data == "help_menu": text, kb = HELP_MENU_CAPTION, help_main_keyboard()
    elif data == "all_commands": text, kb = ALL_COMMANDS_TEXT, help_back_keyboard()
    elif data == "help_music": text, kb = "<b>🎵 Music Commands</b>\n\n• <code>/play [song]</code>\n• <code>/vplay [song]</code>\n• <code>/search [song]</code>\n• <code>/song [song]</code>\n• <code>/radio</code>\n• <code>/autodj on</code>", help_back_keyboard()
    elif data == "help_controls": text, kb = "<b>⏯ Playback Controls</b>\n\n• <code>/pause</code>, <code>/resume</code>\n• <code>/skip</code> (Vote)\n• <code>/stop</code>\n• <code>/queue</code>, <code>/clear</code>\n• <code>/loop</code>, <code>/sleep</code>", help_back_keyboard()
    elif data == "help_effects": text, kb = "<b>🎛 Audio Effects</b>\n\n• <code>/bass</code> - Bass Boost\n• <code>/8d</code> - 8D Audio\n• <code>/nightcore</code>\n• <code>/reset</code>", help_back_keyboard()
    elif data == "help_tools": text, kb = "<b>📂 Tools & Playlists</b>\n\n• <code>/save</code> / <code>/load</code>\n• <code>/gsave</code> / <code>/gload</code>\n• <code>/lyrics</code>, <code>/karaoke</code>\n• <code>/id</code>, <code>/afk</code>\n• <code>/leaderboard</code>, <code>/gstats</code>", help_back_keyboard()
    elif data == "help_admin": text, kb = "<b>🛡 Admin Commands</b>\n\n• <code>/auth</code>\n• <code>/broadcast</code>\n• <code>/stats</code>\n• <code>/tagall</code>\n• <code>/purge</code>\n• <code>/welcome</code>", help_back_keyboard()
    
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
