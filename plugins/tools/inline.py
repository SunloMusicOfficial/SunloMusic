from pyrogram import Client, enums
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from utils.extractors import fetch_audio_url
import asyncio

@Client.on_inline_query()
async def inline_search(client: Client, query: InlineQuery):
    text = query.query.strip()
    if not text: return
    
    # Fast dummy result to show loading
    results = [
        InlineQueryResultArticle(
            title=f"🔍 Search for: {text}",
            description="Click here to send the play command to the chat.",
            input_message_content=InputTextMessageContent(f"/play {text}"),
            thumb_url="https://via.placeholder.com/150/1DB954/FFFFFF?text=Search"
        )
    ]
    await query.answer(results, cache_time=1)
