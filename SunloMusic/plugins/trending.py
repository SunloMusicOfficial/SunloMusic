import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import _search_ytdlp_multi_sync
from SunloMusic.formatters import format_duration
from SunloMusic.logger import LOGGER

TRENDING_CACHE = {}  # category -> (results, timestamp)

CATEGORIES = {
    "hindi": "trending hindi songs 2024",
    "punjabi": "top punjabi hits 2024",
    "english": "top english hits 2024",
    "lofi": "lofi hindi songs",
    "arijit": "arijit singh best songs",
    "old": "old hindi classic songs",
}

@bot.on_message(filters.command("trending"))
@catch_errors
async def trending_cmd(_, m: Message):
    buttons = [
        [InlineKeyboardButton("🎬 Bollywood", callback_data="tr_hindi"),
         InlineKeyboardButton("🎤 Punjabi", callback_data="tr_punjabi")],
        [InlineKeyboardButton("🌍 English", callback_data="tr_english"),
         InlineKeyboardButton("🌙 Lo-Fi", callback_data="tr_lofi")],
        [InlineKeyboardButton("🎼 Arijit", callback_data="tr_arijit"),
         InlineKeyboardButton("📻 Old Classics", callback_data="tr_old")],
    ]
    await m.reply_text(
        "<b>🔥 Trending Charts</b>\n━━━━━━━━━━━━━\n"
        "Choose a category to see top songs:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query(filters.regex("^tr_"))
@catch_errors
async def trending_category(_, cq):
    cat = cq.data.replace("tr_", "")
    if cat not in CATEGORIES:
        return await cq.answer("Unknown category", show_alert=True)
    
    await cq.answer(f"🔍 Loading {cat}...")
    try: await cq.message.edit_text(f"🔍 <b>Fetching {cat} top songs...</b>")
    except: pass
    
    loop = asyncio.get_running_loop()
    try:
        results = await asyncio.wait_for(
            loop.run_in_executor(None, _search_ytdlp_multi_sync, CATEGORIES[cat], 10),
            timeout=15.0
        )
    except:
        results = []
    
    if not results:
        return await cq.message.edit_text("❌ <b>Could not fetch trending songs.</b>")
    
    text = f"<b>🔥 Trending: {cat.title()}</b>\n━━━━━━━━━━━━━\n\n"
    buttons = []
    for i, r in enumerate(results, 1):
        dur = format_duration(r.get("duration", 0))
        title = r.get("title", "Unknown")[:45]
        text += f"{i}. {title} <i>({dur})</i>\n"
        buttons.append([InlineKeyboardButton(
            f"▶️ {title[:35]}",
            callback_data=f"trplay_{r['url'][:60]}"
        )])
    
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="tr_back")])
    
    await cq.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons[:10] + [[InlineKeyboardButton("🔙 Back", callback_data="tr_back")]])
    )

@bot.on_callback_query(filters.regex("^tr_back$"))
@catch_errors
async def tr_back(_, cq):
    buttons = [
        [InlineKeyboardButton("🎬 Bollywood", callback_data="tr_hindi"),
         InlineKeyboardButton("🎤 Punjabi", callback_data="tr_punjabi")],
        [InlineKeyboardButton("🌍 English", callback_data="tr_english"),
         InlineKeyboardButton("🌙 Lo-Fi", callback_data="tr_lofi")],
        [InlineKeyboardButton("🎼 Arijit", callback_data="tr_arijit"),
         InlineKeyboardButton("📻 Old Classics", callback_data="tr_old")],
    ]
    await cq.message.edit_text(
        "<b>🔥 Trending Charts</b>\n━━━━━━━━━━━━━\n"
        "Choose a category to see top songs:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query(filters.regex("^trplay_"))
@catch_errors
async def tr_play(_, cq):
    url_slug = cq.data.replace("trplay_", "")
    await cq.answer("▶️ Sending play command...")
    # Send /play command from user
    try:
        await cq.message.reply_text(f"/play {url_slug}")
    except: pass
