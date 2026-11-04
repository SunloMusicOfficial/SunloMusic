from pyrogram import filters, enums
from pyrogram.types import Message, InlineQueryResultArticle, InputTextMessageContent
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.config import config
from SunloMusic.ytdlp import extract_audio
from SunloMusic.logger import LOGGER

@bot.on_guest_message()
@catch_errors
async def guest_handler(_, m: Message):
    query = m.text or ""
    if not query: return
    
    if query.lower().startswith("play "):
        song = query[5:].strip()
        if not song: return
        
        info = await extract_audio(song)
        if info:
            await bot.answer_guest_query(
                m.guest_query_id,
                result=InlineQueryResultArticle(
                    title=f"🎵 {info['title'][:60]}",
                    description=f"⏱ {info['duration']}s • Click to play in VC",
                    thumb_url=info.get("thumbnail"),
                    input_message_content=InputTextMessageContent(
                        message_text=f"/play {info['url']}"
                    )
                )
            )
        else:
            await bot.answer_guest_query(
                m.guest_query_id,
                result=InlineQueryResultArticle(
                    title="❌ Song not found",
                    description="Try a different search",
                    input_message_content=InputTextMessageContent(
                        message_text="Could not find the song."
                    )
                )
            )
