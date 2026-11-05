import asyncio, os, aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER
from SunloMusic.config import config

TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/multi"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
WEB_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://sunlomusic.onrender.com")

# ✅ Yahan Tu Apna Scraper API ya Logic Daal Sakta Hai
async def get_movie_ddl_links(movie_name: str):
    """
    Ye function internet se Direct Download Links (DDL) scrape karega.
    Filhal maine demo ke liye kuch fake links daale hain.
    Aap ise VegaMovies, HDHub4u ya 1337x ke scraper se replace kar sakte hain.
    """
    LOGGER.info(f"Scraping DDL for: {movie_name}")
    
    # Example: Agar aapke paas koi API hai jo links nikal kar deta hai, toh use call karein
    # ya fir requests/BeautifulSoup se site scrape karein.
    
    # Demo Links (Jo website ke buttons me jayenge)
    return {
        "4k": f"https://vegamovies.download/4k/{movie_name.replace(' ', '-').lower()}",
        "1080p": f"https://vegamovies.download/1080p/{movie_name.replace(' ', '-').lower()}",
        "720p": f"https://vegamovies.download/720p/{movie_name.replace(' ', '-').lower()}"
    }

async def search_movie_tmdb(query: str):
    if not TMDB_API_KEY: return []
    params = {"api_key": TMDB_API_KEY, "query": query, "language": "en-US", "page": 1}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(TMDB_SEARCH_URL, params=params, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [r for r in data.get("results", []) if r.get("media_type") == "movie"][:1]
    except Exception as e:
        LOGGER.error(f"TMDB Search Error: {e}")
    return []

@bot.on_message(filters.command("movie") & filters.private)
@catch_errors
async def movie_search_cmd(_, m: Message):
    if not TMDB_API_KEY:
        return await m.reply_text("❌ <b>TMDB_API_KEY not set in Render Environment!</b>")
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/movie Movie Name</code>")
    
    query = " ".join(m.command[1:])
    status = await m.reply_text(f"🍿 <b>Searching Database...</b>")
    
    movies = await search_movie_tmdb(query)
    if not movies:
        return await status.edit_text("❌ <b>Movie nahi mili!</b>")
    
    movie = movies[0]
    title = movie.get("title", "Unknown")
    year = movie.get("release_date", "N/A")[:4]
    rating = movie.get("vote_average", "N/A")
    overview = movie.get("overview", "No description.")[:300]
    poster = f"{TMDB_IMG_BASE}{movie.get('poster_path')}" if movie.get("poster_path") else ""
    
    caption = (
        f"🎬 <b>{title} ({year})</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"⭐ <b>Rating:</b> {rating}/10\n"
        f"📝 <b>Plot:</b> <i>{overview}...</i>\n"
        f"━━━━━━━━━━━━━\n"
        f"👇 <b>Click below to download:</b>"
    )
    
    # Website ka Link
    download_url = f"{WEB_URL}/movie?id={movie['id']}&title={title}"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬇️ Download / Watch Now", url=download_url)]
    ])
    
    await status.delete()
    if poster:
        await m.reply_photo(poster, caption=caption, reply_markup=buttons)
    else:
        await m.reply_text(caption, reply_markup=buttons)
