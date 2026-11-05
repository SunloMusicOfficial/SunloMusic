import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import _search_ytdlp_multi_sync
from SunloMusic.formatters import format_duration
from SunloMusic.logger import LOGGER

@bot.on_message(filters.regex(r"^[kK][! ]") & filters.group)
@catch_errors
async def search_shortcut_handler(_, m: Message):
    query = m.text[2:].strip()
    if not query:
        return
        
    status = await m.reply_text("🔎 <b>Searching...</b>")
    loop = asyncio.get_running_loop()
    
    try:
        results = await asyncio.wait_for(
            loop.run_in_executor(None, _search_ytdlp_multi_sync, query, 5),
            timeout=10.0
        )
    except Exception as e:
        LOGGER.error(f"Search shortcut error: {e}")
        results = []
        
    if not results:
        return await status.edit_text("❌ <b>No results found.</b>")
        
    text = f"<b>🔍 Search Results for:</b> <i>{query}</i>\n\n"
    buttons = []
    for i, r in enumerate(results):
        dur = format_duration(r.get("duration", 0))
        title = r.get("title", "Unknown")[:40]
        text += f"{i+1}. {title} <i>({dur})</i>\n"
        buttons.append([InlineKeyboardButton(f"▶️ {title[:35]}", callback_data=f"srchplay_{r['url']}")])
        
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="srch_close")])
    await status.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex("^srchplay_"))
@catch_errors
async def search_play_cb(_, cq):
    url = cq.data.replace("srchplay_", "")
    await cq.message.delete()
    # Trigger play command artificially
    await cq.message.reply_text(f"/play {url}")
    await cq.answer()

@bot.on_callback_query(filters.regex("^srch_close$"))
@catch_errors
async def search_close_cb(_, cq):
    await cq.message.delete()
    await cq.answer()
