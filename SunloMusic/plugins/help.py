from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.decorators import catch_errors
from SunloMusic.keyboards import (
    start_keyboard, help_main_keyboard, help_back_keyboard
)


# ═══════════════════════════════════════════
# ✅ SAFE EDIT HELPER — text/photo/caption sab handle karega
# ═══════════════════════════════════════════
async def _safe_edit(cq: CallbackQuery, text: str, reply_markup=None):
    msg = cq.message
    is_media = bool(msg.photo or msg.video or msg.document or msg.animation)
    try:
        if is_media:
            await msg.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await msg.edit_text(text=text, reply_markup=reply_markup)
    except Exception:
        # Final fallback: new message
        try:
            await msg.reply_text(text, reply_markup=reply_markup)
        except Exception:
            pass


# ═══════════════════════════════════════════
# HELP CATEGORIES
# ═══════════════════════════════════════════
HELP_TEXTS = {
    "music": (
        "<b>🎵 Music Commands</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<b>🎧 Play in VC:</b>\n"
        "<code>/play song name</code> — Play audio\n"
        "<code>/vplay song name</code> — Play video\n"
        "<code>/search query</code> — Search YouTube\n"
        "<code>/trending</code> — Top charts\n"
        "<code>/radio hindi</code> — Radio (hindi/english/lofi)\n"
        "<code>/voteplay song</code> — Request song\n\n"
        "<b>📥 Downloads:</b>\n"
        "<code>/song query</code> — Download MP3 (5💰)\n"
        "<code>/video query</code> — Download MP4 (5💰)"
    ),
    "controls": (
        "<b>⏯ Playback Controls</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<code>/skip</code> — Skip current\n"
        "<code>/next</code> — Alias for skip\n"
        "<code>/queue</code> — Show queue\n"
        "<code>/clear</code> — Clear queue (admin)\n"
        "<code>/shuffle</code> — Shuffle queue (admin)\n\n"
        "<b>⚡ Audio Control:</b>\n"
        "<code>/speed 1.25</code> — Change speed (0.5-2.0)\n"
        "<code>/volume 150</code> — Change volume (0-200)\n"
        "<code>/eq rock</code> — EQ: bass/pop/rock/jazz/vocal/flat"
    ),
    "effects": (
        "<b>🎛 Audio Effects</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<code>/bass</code> — Bass boost\n"
        "<code>/8d</code> — 8D audio\n"
        "<code>/nightcore</code> — Sped up\n"
        "<code>/reset</code> — Normal audio\n"
        "<code>/sleep 10m</code> — Auto-leave VC\n\n"
        "<b>🎤 Karaoke & Lyrics:</b>\n"
        "<code>/karaoke on/off</code> — Live lyrics\n"
        "<code>/lyrics song name</code> — Fetch lyrics\n"
        "<code>/autodj on/off</code> — Auto-play\n\n"
        "<b>💝 Dedication:</b>\n"
        "<code>/dedicate @user song</code>"
    ),
    "admin": (
        "<b>🛡 Admin Commands</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "<b>Group Admin:</b>\n"
        "<code>/auth</code> — Authorize chat\n"
        "<code>/welcome on/off</code> — Welcome msgs\n"
        "<code>/purge</code> — Purge (reply to msg)\n"
        "<code>/tagall message</code> — Tag all\n"
        "<code>/id</code> — Get IDs\n\n"
        "<b>👑 Sudo Only:</b>\n"
        "<code>/stats</code> — Bot stats\n"
        "<code>/broadcast</code> — Broadcast\n"
        "<code>/addsudo</code> — Add sudo\n"
        "<code>/delsudo id</code> — Remove\n"
        "<code>/gstats</code> — Group stats\n\n"
        "<b>📊 Utility:</b>\n"
        "<code>/afk reason</code> — AFK\n"
        "<code>/leaderboard</code> — Top users\n"
        "<code>/recent</code> — Recent songs"
    ),
}


# ═══════════════════════════════════════════
# ALL COMMANDS
# ═══════════════════════════════════════════
ALL_COMMANDS_TEXT = (
    "<b>📜 All SunloMusic Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "<b>🎵 Music</b>\n"
    "/play • /vplay • /search • /trending • /radio • /voteplay\n\n"
    "<b>📥 Download</b>\n"
    "/song • /video\n\n"
    "<b>⏯ Controls</b>\n"
    "/skip • /next • /queue • /clear • /shuffle\n\n"
    "<b>⚡ Audio</b>\n"
    "/speed • /volume • /eq\n\n"
    "<b>🎛 Effects</b>\n"
    "/bass • /8d • /nightcore • /reset • /sleep\n\n"
    "<b>🎤 Tools</b>\n"
    "/karaoke • /autodj • /lyrics • /dedicate\n\n"
    "<b>❤️ Favorites</b>\n"
    "/like • /favorites • /playfav\n\n"
    "<b>📀 Personal Playlist</b>\n"
    "/save • /addsong • /myplaylists • /load • /delplaylist\n\n"
    "<b>📀 Group Playlist</b>\n"
    "/gsave • /gload\n\n"
    "<b>🎮 Fun</b>\n"
    "/quiz • /guess • /quizlb\n\n"
    "<b>💰 Rewards</b>\n"
    "/daily • /points • /shop\n\n"
    "<b>🛡 Moderation</b>\n"
    "/auth • /purge • /tagall • /welcome • /id\n\n"
    "<b>👑 Sudo</b>\n"
    "/stats • /broadcast • /addsudo • /delsudo • /gstats\n\n"
    "<b>👤 User</b>\n"
    "/afk • /leaderboard • /recent • /gstats\n\n"
    "<b>🤖 Start</b>\n"
    "/start • /ping • /help • /allcommand\n\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "<b>💡 Inline Mode:</b>\n"
    "Type <code>@BOT_USERNAME song name</code> in any chat\n\n"
    "<b>🎤 Shazam:</b>\n"
    "Send any voice/audio in group"
)


# ═══════════════════════════════════════════
# MESSAGE COMMANDS
# ═══════════════════════════════════════════
@bot.on_message(filters.command("allcommand"))
@catch_errors
async def allcommand_cmd(_, m: Message):
    me = await bot.get_me()
    text = ALL_COMMANDS_TEXT.replace("BOT_USERNAME", me.username)
    await m.reply_text(text)


# ═══════════════════════════════════════════
# CALLBACKS — all use _safe_edit
# ═══════════════════════════════════════════
@bot.on_callback_query(filters.regex(r"^help_menu$"))
@catch_errors
async def help_menu_cb(_, cq: CallbackQuery):
    await _safe_edit(
        cq,
        "<b>❓ SunloMusic Help</b>\n"
        "━━━━━━━━━━━━━\n\n"
        "Choose a category to explore commands:",
        reply_markup=help_main_keyboard(),
    )
    await cq.answer()


@bot.on_callback_query(filters.regex(r"^help_(music|controls|effects|admin)$"))
@catch_errors
async def help_category_cb(_, cq: CallbackQuery):
    cat = cq.data.replace("help_", "", 1)
    text = HELP_TEXTS.get(cat)
    if not text:
        return await cq.answer("Unknown category", show_alert=True)
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
        f"<b>🎶 Welcome to {config.BOT_NAME}!</b>\n\n"
        f"<i>Your ultimate ultra-fast Voice Chat Music Companion.</i>\n\n"
        f"✨ <b>Features:</b>\n"
        f"• High-Quality Audio & Video Streaming\n"
        f"• Zero Lag & 24/7 Uptime\n"
        f"• Premium User Interface\n\n"
        f"👨‍💻 <b>Developer:</b> <a href='https://t.me/YO_UR_OFFICIAL_CRUSH'>Sakil</a>\n"
        f"📢 <b>Updates:</b> <a href='{config.UPDATES_CHANNEL}'>Vip Sakil Bio</a>"
    )
    await _safe_edit(cq, caption, reply_markup=start_keyboard())
    await cq.answer()
