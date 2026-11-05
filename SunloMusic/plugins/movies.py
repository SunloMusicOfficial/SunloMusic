import asyncio, os, aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER
from SunloMusic.config import config

# ✅ Ensure URL is clean (No trailing slash)
WEB_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://sunlomusic.onrender.com").rstrip("/")

async def get_movie_ddl_links(movie_name: str):
    # Demo Links (Inhe apne scraper se replace kar)
    return {
        "4k": f"https://vegamovies.download/4k/{movie_name.replace(' ', '-').lower()}",
        "1080p": f"https://vegamovies.download/1080p/{movie_name.replace(' ', '-').lower()}",
        "720p": f"https://vegamovies.download/720p/{movie_name.replace(' ', '-').lower()}"
    }

async def search_movie_tmdb(query: str):
    if not config.TMDB_API_KEY: return []
    params = {"api_key": config.TMDB_API_KEY, "query": query, "language": "en-US", "page": 1}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.themoviedb.org/3/search/multi", params=params, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [r for r in data.get("results", []) if r.get("media_type") == "movie"][:1]
    except: pass
    return []

@bot.on_message(filters.command("movie") & filters.private)
@catch_errors
async def movie_search_cmd(_, m: Message):
    if not config.TMDB_API_KEY: return await m.reply_text("❌ TMDB_API_KEY missing in Render Environment!")
    if len(m.command) < 2: return await m.reply_text("❌ Usage: <code>/movie Movie Name</code>")
    
    query = " ".join(m.command[1:])
    status = await m.reply_text(f"🍿 <b>Searching Database...</b>")
    
    movies = await search_movie_tmdb(query)
    if not movies: return await status.edit_text("❌ <b>Movie nahi mili! Try different name.</b>")
    
    movie = movies[0]
    title = movie.get("title", "Unknown")
    year = movie.get("release_date", "N/A")[:4]
    rating = movie.get("vote_average", "N/A")
    overview = movie.get("overview", "No description.")[:300]
    poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else ""
    
    caption = f"🎬 <b>{title} ({year})</b>\n━━━━━━━━━━━━━\n⭐ <b>Rating:</b> {rating}/10\n📝 <b>Plot:</b> <i>{overview}...</i>\n━━━━━━━━━━━━━\n👇 <b>Click below to download:</b>"
    
    # ✅ FIXED: Removed '&title={title}' to prevent Invalid URL Error
    download_url = f"{WEB_URL}/movie?id={movie['id']}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("⬇️ Download / Watch Now", url=download_url)]])
    
    await status.delete()
    if poster: 
        try: 
            await m.reply_photo(poster, caption=caption, reply_markup=buttons)
        except:
            await m.reply_text(caption, reply_markup=buttons)
    else: 
        await m.reply_text(caption, reply_markup=buttons)
