from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors

ALL_COMMANDS_TEXT = (
    "<b>📜 All SunloMusic Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "<b>🎵 Music</b>\n"
    "/play • /vplay • /search • k! • /trending • /radio • /voteplay • /splay • /audiobook • /battle\n\n"
    "<b>🍿 Movies</b>\n"
    "/movie movie_name (DM only)\n\n"
    "<b>📥 Download</b>\n"
    "/song • /video\n\n"
    "<b>⏯ Controls</b>\n"
    "/pause • /resume • /skip • /stop • /seek • /queue • /export • /clear • /shuffle\n\n"
    "<b>⚡ Audio</b>\n"
    "/speed • /volume • /eq\n\n"
    "<b>🎛 Effects</b>\n"
    "/bass • /8d • /nightcore • /chipmunk • /monster • /reset • /sleep • /crossfade\n\n"
    "<b>🎤 Tools & AI</b>\n"
    "/karaoke • /autodj • /lyrics • /dedicate • /settings • /style\n"
    "<i>Mention bot to chat with AI!</i>\n\n"
    "<b>🛡 Moderation</b>\n"
    "/auth • /fsub • /setprefix • /antilink • /antiforward • /captcha • /purge • /tagall • /welcome • /id\n\n"
    "<b>🎮 Games</b>\n"
    "/battle • /quiz • /guess • /quizlb\n\n"
    "<b>❤️ Favorites & Playlist</b>\n"
    "/like • /favorites • /playfav\n"
    "/save • /addsong • /myplaylists • /load • /delplaylist • /gsave • /gload\n\n"
    "<b>💰 Rewards</b>\n"
    "/daily • /points • /shop\n\n"
    "<b>👑 Sudo / Owner</b>\n"
    "/stats • /broadcast • /addsudo • /delsudo • /sudolist • /activevc • /gstats • /restart\n\n"
    "<b>👤 User</b>\n"
    "/afk • /leaderboard • /recent\n\n"
    "<b>🤖 Start</b>\n"
    "/start • /ping • /help • /allcommand\n"
)

@bot.on_message(filters.command("allcommand"))
@catch_errors
async def allcommand_cmd(_, m: Message):
    await m.reply_text(ALL_COMMANDS_TEXT)
