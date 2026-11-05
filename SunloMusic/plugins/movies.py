import asyncio, os, aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER
from SunloMusic.config import config

WEB_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://sunlomusic.onrender.com").rstrip("/")

async def get_movie_ddl_links(movie_name: str):
    """Fetch real links from YTS, then PirateBay, then fallback to Google."""
    
    # 1. Try YTS API (Best for Hollywood, gives direct .torrent file)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://yts.mx/api/v2/list_movies.json?query_term={movie_name}&limit=1") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    movies = data.get("data", {}).get("movies", [])
                    if movies:
                        torrents = movies[0].get("torrents", [])
                        links = {}
                        for t in torrents:
                            if t["quality"] == "2160p": links["4k"] = t["url"]
                            elif t["quality"] == "1080p": links["1080p"] = t["url"]
                            elif t["quality"] == "720p": links["720p"] = t["url"]
                        
                        if links:
                            LOGGER.info(f"YTS links found for {movie_name}")
                            return {
                                "4k": links.get("4k", links.get("1080p", "#")),
                                "1080p": links.get("1080p", links.get("720p", "#")),
                                "720p": links.get("720p", links.get("1080p", "#"))
                            }
    except Exception as e:
        LOGGER.error(f"YTS API Error: {e}")
    
    # 2. Try PirateBay API (Best for Bollywood, Regional, and New Movies, gives Magnet link)
    try:
        async with aiohttp.ClientSession() as session:
            query = movie_name.replace(' ', '%20')
            # Category 200 = Video
            async with session.get(f"https://apibay.org/q.php?q={query}&cat=200") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Check if results exist and are valid
                    if data and len(data) > 0 and data[0].get("id") != "0":
                        # Sort by seeders to get the best torrent
                        results = sorted([r for r in data if int(r.get("seeders", 0)) > 0], key=lambda x: int(x["seeders"]), reverse=True)
                        if results:
                            best = results[0]
                            info_hash = best["info_hash"]
                            seeders = best["seeders"]
                            # Create Magnet Link
                            trackers = "&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451"
                            magnet = f"magnet:?xt=urn:btih:{info_hash}{trackers}"
                            
                            LOGGER.info(f"PirateBay magnet found for {movie_name} (Seeders: {seeders})")
                            # PirateBay doesn't separate 4K/1080p in basic API, so we give the best magnet for all
                            return {
                                "4k": magnet,
                                "1080p": magnet,
                                "720p": magnet
                            }
    except Exception as e:
        LOGGER.error(f"PirateBay API Error: {e}")

    # 3. Fallback: Google Search (If movie is too new and not even on PirateBay)
    LOGGER.info(f"No torrent found for {movie_name}, using Google fallback.")
    query = movie_name.replace(' ', '+')
    return {
        "4k": f"https://www.google.com/search?q={query}+movie+download+4k",
        "1080p": f"https://www.google.com/search?q={query}+movie+download+1080p",
        "720p": f"https://www.google.com/search?q={query}+movie+download+720p"
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
    
    download_url = f"{WEB_URL}/movie?id={movie['id']}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("⬇️ Download / Watch Now", url=download_url)]])
    
    await status.delete()
    if poster: 
        try: await m.reply_photo(poster, caption=caption, reply_markup=buttons)
        except: await m.reply_text(caption, reply_markup=buttons)
    else: 
        await m.reply_text(caption, reply_markup=buttons)
