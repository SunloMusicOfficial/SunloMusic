import asyncio
from pyrogram import filters
from pyrogram.types import (
    InlineQuery, InlineQueryResultArticle,
    InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
)
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import _api_request
from SunloMusic.formatters import format_duration
from SunloMusic.logger import LOGGER

@bot.on_inline_query()
@catch_errors
async def inline_handler(_, inline_query: InlineQuery):
    query = inline_query.query.strip()
    
    # ✅ Empty query ke liye ek default message
    if not query:
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    title="🎵 SunloMusic — Search a song",
                    description="Type: @SunloMusicBot song name",
                    thumb_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                    input_message_content=InputTextMessageContent(
                        message_text="🎵 <b>SunloMusic</b>\n\nType <code>@SunloMusicBot song name</code> in any chat to search & play music!"
                    )
                )
            ],
            cache_time=300
        )
        return
    
    # ✅ Fast Search via OneGrab API (3s timeout)
    try:
        search_data = await asyncio.wait_for(
            _api_request("/api/search", {"query": query, "platform": "youtube"}),
            timeout=2.5
        )
    except Exception as e:
        LOGGER.error(f"Inline search timeout/error: {e}")
        search_data = None

    # Agar API fail ho jaye toh empty result bhej do (taaki Telegram timeout na kare)
    if not search_data or not search_data.get("results"):
        await inline_query.answer([], cache_time=60)
        return
    
    inline_results = []
    for r in search_data["results"][:10]:
        title = r.get("title", "Unknown")[:60]
        dur = format_duration(int(r.get("duration") or 0))
        url = r.get("url", "")
        thumb = r.get("thumbnail", "")
        
        # Agar thumbnail nahi hai toh default use karo
        if not thumb:
            thumb = "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
        
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
    
    await inline_query.answer(inline_results, cache_time=60, is_personal=False)
