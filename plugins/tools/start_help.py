from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config.vars import Config

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("📚 Help & Commands", callback_data="help_menu"),
         InlineKeyboardButton("🌐 Dashboard", url="http://localhost:8080")]
    ])
    await message.reply_photo(
        photo="https://via.placeholder.com/1280x720.png?text=SunloMusic+Premium",
        caption=f"👋 **Hello {message.from_user.first_name}!**\n\nI am **{Config.BOT_NAME}**, an Enterprise-Level Music Bot.\n\n✨ **Features:** 200+\n🎵 **Supported:** YouTube, Spotify, Apple Music, Local Files\n🤖 **AI Powered:** Auto-DJ, Stem Splitter, Trivia Games\n\nAdd me to your group and type `/play` to start the party!",
        reply_markup=buttons
    )

@Client.on_callback_query(filters.regex("^help_menu$"))
async def help_menu_cb(client, cq):
    help_text = (
        "🛠 **SunloMusic Command Menu**\n\n"
        "🎵 **Music:** `/play`, `/vplay`, `/pause`, `/resume`, `/skip`, `/stop`, `/volume`, `/loop`, `/shuffle`\n"
        "🎛 **Filters:** `/filter`, `/karaoke`, `/vocals`, `/music`\n"
        "☁️ **Playlist:** `/save`, `/myplaylist`, `/playall`, `/delplaylist`\n"
        "🪙 **Economy:** `/wallet`, `/daily`, `/bump`, `/leaderboard`\n"
        "🎮 **Games:** `/guess`, `/match`, `/dice`, `/dart`\n"
        "⚙️ **Admin:** `/settings`, `/sleep`, `/record`, `/ban`, `/mute`, `/purge`, `/tagall`\n"
        "📥 **Tools:** `/song`, `/video`, `/lyrics`, `/stats`, `/ping`\n"
        "👑 **Owner:** `/gcastplay`, `/logs`, `/reboot`, `/eval`"
    )
    await cq.message.edit_caption(caption=help_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_menu")]]))

@Client.on_callback_query(filters.regex("^start_menu$"))
async def start_menu_cb(client, cq):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("📚 Help & Commands", callback_data="help_menu"),
         InlineKeyboardButton("🌐 Dashboard", url="http://localhost:8080")]
    ])
    await cq.message.edit_caption(
        caption=f"👋 **Hello {cq.from_user.first_name}!**\n\nI am **{Config.BOT_NAME}**, an Enterprise-Level Music Bot.\n\n✨ **Features:** 200+\n🎵 **Supported:** YouTube, Spotify, Apple Music, Local Files\n🤖 **AI Powered:** Auto-DJ, Stem Splitter, Trivia Games\n\nAdd me to your group and type `/play` to start the party!",
        reply_markup=buttons
    )
