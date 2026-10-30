import asyncio
from pyrogram import filters
from pyrogram.types import (
    InlineQuery, InlineQueryResultArticle,
    InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
)
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import _search_ytdlp_multi_sync
from SunloMusic.formatters import format_duration
from SunloMusic.logger import LOGGER

@bot.on_inline_query()
@catch_errors
async def inline_handler(_, inline_query: InlineQuery):
    query = inline_query.query.strip()
    
    if not query:
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    title="🎵 SunloMusic — Search a song",
                    description="Type: @YourBot song name",
                    thumb_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                    input_message_content=InputTextMessageContent(
                        message_text="🎵 <b>SunloMusic</b>\n\nType <code>@YourBot song name</code> in any chat to search & play music!"
                    )
                )
            ],
            cache_time=300
        )
        return
    
    loop = asyncio.get_running_loop()
    try:
        results = await asyncio.wait_for(
            loop.run_in_executor(None, _search_ytdlp_multi_sync, query, 10),
            timeout=12.0
        )
    except Exception as e:
        LOGGER.error(f"Inline search error: {e}")
        results = []
    
    if not results:
        await inline_query.answer([], cache_time=60)
        return
    
    inline_results = []
    for i, r in enumerate(results[:10]):
        title = r.get("title", "Unknown")[:60]
        dur = format_duration(r.get("duration", 0))
        url = r.get("url", "")
        thumb = r.get("thumbnail", "")
        
        inline_results.append(
            InlineQueryResultArticle(
                title=title,
                description=f"🎵 {dur} • Tap to send /play",
                thumb_url=thumb,
                input_message_content=InputTextMessageContent(
                    message_text=f"/play {url}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ Play in VC", url=url)]
                ])
            )
        )
    
    await inline_query.answer(inline_results, cache_time=120, is_personal=False)
