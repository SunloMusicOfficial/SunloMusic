import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER

def _search_sync(query: str):
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "noplaylist": True}) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query} audio", download=False)
            results = []
            if info and "entries" in info:
                for e in info["entries"]:
                    if e:
                        results.append({
                            "title": e.get("title", "Unknown"),
                            "url": e.get("url"),
                            "duration": e.get("duration", 0),
                            "id": e.get("id")
                        })
            return results
    except Exception as e:
        LOGGER.error(f"Search error: {e}")
        return []

@bot.on_message(filters.command("search") & filters.group)
@catch_errors
async def search_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Give a song name to search.</b>")
    
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 <b>Searching YouTube...</b>")
    
    import asyncio
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(None, _search_sync, query)
    
    if not results:
        return await status.edit_text("❌ <b>No results found.</b>")
        
    buttons = []
    for idx, res in enumerate(results):
        dur = res["duration"] or 0
        mins, secs = divmod(dur, 60)
        dur_str = f"{mins}:{secs:02d}"
        buttons.append([InlineKeyboardButton(f"{res['title'][:35]}... ({dur_str})", callback_data=f"srch_{res['url']}")])
        
    await status.edit_text(
        f"<b>🔍 Search Results for:</b> <i>{query}</i>\n\nSelect a song to play:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query(filters.regex("^srch_"))
@catch_errors
async def search_select(_, cq):
    url = cq.data.replace("srch_", "")
    await cq.message.delete()
    # Trigger the play command artificially
    await cq.message.reply_text(f"/play {url}")
