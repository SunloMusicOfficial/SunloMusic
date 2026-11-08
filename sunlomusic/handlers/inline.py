# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from SunloMusic.services.downloader import downloader
from SunloMusic.core.logging import logger

def format_views(count):
    if count >= 1_000_000_000:
        return f"{count / 1_000_000_000:.1f}B views"
    elif count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M views"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K views"
    else:
        return f"{count} views"

def format_duration(seconds):
    if seconds == 0:
        return "Live"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

async def inline_query_handler(client: Client, inline_query: InlineQuery):
    query = inline_query.query.strip()

    if not query:
        await inline_query.answer(
            results=[],
            switch_pm_text="Type a song name to search...",
            switch_pm_parameter="start",
            cache_time=0
        )
        return

    try:
        logger.info(f"Inline query from user {inline_query.from_user.id}: {query}")

        results = await downloader.search_youtube(query, max_results=20)

        if not results:
            await inline_query.answer(
                results=[],
                switch_pm_text="No results found",
                switch_pm_parameter="start",
                cache_time=5
            )
            return

        inline_results = []
        for idx, result in enumerate(results[:20]):
            title = result['title']
            url = result['url']
            views = format_views(result['view_count'])
            duration = format_duration(result['duration'])
            uploader = result['uploader']
            thumbnail = result['thumbnail']
            video_id = result['id']

            thumb_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

            description = f"{views}"
            if duration != "Live":
                description += f" • {duration}"

            message_text = f"/play {url}"

            inline_results.append(
                InlineQueryResultArticle(
                    id=f"yt_{idx}_{video_id}",
                    title=title,
                    description=description,
                    thumb_url=thumb_url,
                    input_message_content=InputTextMessageContent(
                        message_text=message_text
                    )
                )
            )

        await inline_query.answer(
            results=inline_results,
            cache_time=300,
            is_gallery=False,
            is_personal=False
        )

        logger.info(f"Sent {len(inline_results)} results for query: {query}")

    except Exception as e:
        logger.error(f"Error handling inline query: {e}")
        await inline_query.answer(
            results=[],
            switch_pm_text="Error occurred",
            switch_pm_parameter="start",
            cache_time=0
        )

def register_inline_handlers(app: Client):
    app.on_inline_query()(inline_query_handler)
    logger.info("Inline query handlers registered")
