import asyncio, os, aiohttp, re
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.logger import LOGGER
from SunloMusic.config import config

WEB_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://sunlomusic.onrender.com").rstrip("/")

async def get_movie_ddl_links(movie_name: str, imdb_id: str = None):
    # 1. Torrentio API (Needs IMDb ID)
    if imdb_id:
        try:
            url = f"https://torrentio.strem.fun/stream/movie/{imdb_id}.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        streams = data.get("streams", [])
                        if streams:
                            for s in streams:
                                if "url" in s and s["url"].startswith("magnet:"):
                                    LOGGER.info(f"Torrentio found link for {movie_name} ({imdb_id})")
                                    return {"4k": s["url"], "1080p": s["url"], "720p": s["url"]}
        except Exception as e:
            LOGGER.error(f"Torrentio Error: {e}")

    # 2. PirateBay API (With User-Agent to prevent block)
    try:
        clean_name = movie_name.split(':')[0].split('-')[0].strip()
        query = clean_name.replace(' ', '%20')
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://apibay.org/q.php?q={query}&cat=200", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0 and data[0].get("id") != "0":
                        results = sorted([r for r in data if int(r.get("seeders", 0)) > 0], key=lambda x: int(x["seeders"]), reverse=True)
                        if results:
                            best = results[0]
                            info_hash = best["info_hash"]
                            trackers = "&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337"
                            magnet = f"magnet:?xt=urn:btih:{info_hash}{trackers}"
                            LOGGER.info(f"PirateBay found link for {clean_name}")
                            return {"4k": magnet, "1080p": magnet, "720p": magnet}
    except Exception as e:
        LOGGER.error(f"PirateBay Error: {e}")

    return None

async def search_movie_tmdb(query: str):
    if not config.TMDB_API_KEY: return None
    params = {"api_key": config.TMDB_API_KEY, "query": query, "language": "en-US", "page": 1}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results: return results[0]
    except Exception as e: LOGGER.error(f"TMDB Search Error: {e}")
    return None

async def get_imdb_id(tmdb_id: int):
    if not config.TMDB_API_KEY: return ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={config.TMDB_API_KEY}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("imdb_id", "")
    except: pass
    return ""

@bot.on_message(filters.command("movie") & filters.private)
@catch_errors
async def movie_search_cmd(_, m: Message):
    if not config.TMDB_API_KEY: return await m.reply_text("❌ TMDB_API_KEY missing!")
    if len(m.command) < 2: return await m.reply_text("❌ Usage: <code>/movie Movie Name</code>")
    
    query = " ".join(m.command[1:])
    status = await m.reply_text(f"🍿 <b>Searching Database...</b>")
    
    movie = await search_movie_tmdb(query)
    if not movie: return await status.edit_text("❌ <b>Movie nahi mili!</b>")
    
    tmdb_id = movie.get("id")
    title = movie.get("title", "Unknown")
    year = movie.get("release_date", "N/A")[:4]
    rating = movie.get("vote_average", "N/A")
    overview = movie.get("overview", "No description.")[:300]
    poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else ""
    
    # ✅ Get exact IMDb ID
    imdb_id = await get_imdb_id(tmdb_id)
    
    caption = f"🎬 <b>{title} ({year})</b>\n━━━━━━━━━━━━━\n⭐ <b>Rating:</b> {rating}/10\n📝 <b>Plot:</b> <i>{overview}...</i>\n━━━━━━━━━━━━━\n👇 <b>Click below to download:</b>"
    
    # ✅ Pass IMDb ID to website
    download_url = f"{WEB_URL}/movie?id={tmdb_id}&imdb={imdb_id}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("⬇️ Download / Watch Now", url=download_url)]])
    
    await status.delete()
    if poster: 
        try: await m.reply_photo(poster, caption=caption, reply_markup=buttons)
        except: await m.reply_text(caption, reply_markup=buttons)
    else: 
        await m.reply_text(caption, reply_markup=buttons)
