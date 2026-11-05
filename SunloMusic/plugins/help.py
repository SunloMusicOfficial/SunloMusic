from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.decorators import catch_errors
from SunloMusic.keyboards import start_keyboard, help_main_keyboard, help_back_keyboard

async def _safe_edit(cq: CallbackQuery, text: str, reply_markup=None):
    msg = cq.message
    is_media = bool(msg.photo or msg.video or msg.document or msg.animation)
    try:
        if is_media: await msg.edit_caption(caption=text, reply_markup=reply_markup)
        else: await msg.edit_text(text=text, reply_markup=reply_markup)
    except Exception:
        try: await msg.reply_text(text, reply_markup=reply_markup)
        except Exception: pass

HELP_TEXTS = {
    "music": (
        "<b>🎵 Music Commands</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<b>🎧 Play in VC:</b>\n"
        "<code>/play song name</code> — Play audio\n"
        "<code>/vplay song name</code> — Play video\n"
        "<code>/search query</code> — Search YouTube\n"
        "<code>k! query</code> — Fast Search Shortcut\n"
        "<code>/trending</code> — Top charts\n"
        "<code>/radio hindi</code> — Radio\n"
        "<code>/voteplay song</code> — Request song\n"
        "<code>/splay spotify_link</code> — Play from Spotify\n"
        "<code>/audiobook name</code> — Play audiobook\n"
        "<code>/battle song1 vs song2</code> — Music Battle\n\n"
        "<b>📥 Downloads:</b>\n"
        "<code>/song query</code> — Download MP3 (5💰)\n"
        "<code>/video query</code> — Download MP4 (5💰)"
    ),
    "controls": (
        "<b>⏯ Playback Controls</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<code>/pause</code> — Pause\n"
        "<code>/resume</code> — Resume\n"
        "<code>/skip</code> — Skip\n"
        "<code>/stop</code> — Stop & clear\n"
        "<code>/seek 1:30</code> — Jump time\n"
        "<code>/queue</code> — Show queue\n"
        "<code>/export</code> — Export queue\n"
        "<code>/clear</code> — Clear queue\n"
        "<code>/shuffle</code> — Shuffle queue\n\n"
        "<b>⚡ Audio Control:</b>\n"
        "<code>/speed 1.25</code> — Speed\n"
        "<code>/volume 150</code> — Volume\n"
        "<code>/eq rock</code> — EQ"
    ),
    "effects": (
        "<b>🎛 Audio Effects & Tools</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<code>/bass</code> — Bass boost\n"
        "<code>/8d</code> — 8D audio\n"
        "<code>/nightcore</code> — Nightcore\n"
        "<code>/chipmunk</code> — High pitch\n"
        "<code>/monster</code> — Low pitch\n"
        "<code>/reset</code> — Normal audio\n"
        "<code>/sleep 10m</code> — Auto-leave VC\n\n"
        "<b>🎤 Karaoke & Lyrics:</b>\n"
        "<code>/karaoke on/off</code> — Live lyrics\n"
        "<code>/lyrics song name</code> — Fetch lyrics\n"
        "<code>/autodj on/off</code> — Auto-play\n\n"
        "<b>💝 Dedication:</b>\n"
        "<code>/dedicate @user song</code>\n\n"
        "<b>🤖 AI Features:</b>\n"
        "<code>/settings</code> — Toggle SunloMusic AI & Voice Search\n"
        "<b>AI Chat:</b> Mention me <code>@BotUsername</code> to chat!"
    ),
    "admin": (
        "<b>🛡 Admin Commands</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<b>Group Admin:</b>\n"
        "<code>/auth</code> — Authorize chat\n"
        "<code>/settings</code> — AI Features Panel\n"
        "<code>/fsub @channel</code> — Force Subscribe\n"
        "<code>/setprefix !</code> — Custom Prefix\n"
        "<code>/antilink on/off</code> — Anti-Link\n"
        "<code>/antiforward on/off</code> — Anti-Forward\n"
        "<code>/captcha on/off</code> — Anti-Bot Captcha\n"
        "<code>/welcome on/off</code> — Welcome msgs\n"
        "<code>/purge</code> — Purge msgs\n"
        "<code>/tagall message</code> — Tag all\n"
        "<code>/id</code> — Get IDs\n\n"
        "<b>👑 Sudo Only:</b>\n"
        "<code>/stats</code> — Bot stats\n"
        "<code>/broadcast</code> — Broadcast msg\n"
        "<code>/addsudo</code> — Add sudo\n"
        "<code>/delsudo id</code> — Remove sudo\n"
        "<code>/sudolist</code> — List sudos\n"
        "<code>/activevc</code> — List active VCs\n"
        "<code>/gstats</code> — Group stats\n"
        "<code>/restart</code> — Restart bot"
    ),
}

ALL_COMMANDS_TEXT = (
    "<b>📜 All SunloMusic Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "<b>🎵 Music</b>\n"
    "/play • /vplay • /search • k! • /trending • /radio • /voteplay • /splay • /audiobook • /battle\n\n"
    "<b>📥 Download</b>\n"
    "/song • /video\n\n"
    "<b>⏯ Controls</b>\n"
    "/pause • /resume • /skip • /stop • /seek • /queue • /export • /clear • /shuffle\n\n"
    "<b>⚡ Audio</b>\n"
    "/speed • /volume • /eq\n\n"
    "<b>🎛 Effects</b>\n"
    "/bass • /8d • /nightcore • /chipmunk • /monster • /reset • /sleep\n\n"
    "<b>🎤 Tools</b>\n"
    "/karaoke • /autodj • /lyrics • /dedicate\n"
    "/settings • /style\n\n"
    "<b>🛡 Moderation</b>\n"
    "/auth • /fsub • /setprefix • /antilink • /antiforward • /captcha • /purge • /tagall • /welcome • /id\n\n"
    "<b>🎮 Games & AI</b>\n"
    "/battle • /quiz • /guess • /quizlb\n"
    "<i>Mention bot to chat with AI!</i>\n\n"
    "<b>❤️ Favorites</b>\n"
    "/like • /favorites • /playfav\n\n"
    "<b>📀 Playlists</b>\n"
    "/save • /addsong • /myplaylists • /load • /delplaylist • /gsave • /gload\n\n"
    "<b>💰 Rewards</b>\n"
    "/daily • /points • /shop\n\n"
    "<b>👑 Sudo / Owner</b>\n"
    "/stats • /broadcast • /addsudo • /delsudo • /sudolist • /activevc • /gstats • /restart\n\n"
    "<b>👤 User</b>\n"
    "/afk • /leaderboard • /recent\n\n"
    "<b>🤖 Start</b>\n"
    "/start • /ping • /help • /allcommand\n\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "<b>💡 Inline Mode:</b>\n"
    "Type <code>@BOT_USERNAME song name</code> in any chat\n\n"
    "<b>🎤 Shazam:</b>\n"
    "Send any voice/audio in group"
)

@bot.on_message(filters.command("allcommand"))
@catch_errors
async def allcommand_cmd(_, m: Message):
    me = await bot.get_me()
    text = ALL_COMMANDS_TEXT.replace("BOT_USERNAME", me.username)
    await m.reply_text(text)

@bot.on_callback_query(filters.regex(r"^help_menu$"))
@catch_errors
async def help_menu_cb(_, cq: CallbackQuery):
    await _safe_edit(cq, "<b>❓ SunloMusic Help</b>\n━━━━━━━━━━━━━\n\nChoose a category to explore commands:", reply_markup=help_main_keyboard())
    await cq.answer()

@bot.on_callback_query(filters.regex(r"^help_(music|controls|effects|admin)$"))
@catch_errors
async def help_category_cb(_, cq: CallbackQuery):
    cat = cq.data.replace("help_", "", 1)
    text = HELP_TEXTS.get(cat)
    if not text: return await cq.answer("Unknown category", show_alert=True)
    await _safe_edit(cq, text, reply_markup=help_back_keyboard())
    await cq.answer()

@bot.on_callback_query(filters.regex(r"^all_commands$"))
@catch_errors
async def all_commands_cb(_, cq: CallbackQuery):
    me = await bot.get_me()
    text = ALL_COMMANDS_TEXT.replace("BOT_USERNAME", me.username)
    await _safe_edit(cq, text, reply_markup=help_back_keyboard())
    await cq.answer()

@bot.on_callback_query(filters.regex(r"^back_start$"))
@catch_errors
async def back_start_cb(_, cq: CallbackQuery):
    caption = (
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
    await _safe_edit(cq, caption, reply_markup=start_keyboard())
    await cq.answer()
