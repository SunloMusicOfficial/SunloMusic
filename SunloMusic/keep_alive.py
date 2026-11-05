import asyncio, os, time, aiohttp
from aiohttp import web
from SunloMusic.logger import LOGGER
from SunloMusic.config import config
from SunloMusic.database import get_stats
from SunloMusic.queues import active_chats

START_TIME = time.time()
TMDB_API_KEY = config.TMDB_API_KEY
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/original"

async def _handle_ping(request):
    return web.Response(text="SunloMusic is alive!", status=200)

async def _handle_dashboard(request):
    try:
        stats = await get_stats()
        active = len(active_chats())
        uptime = int(time.time() - START_TIME)
        h, rem = divmod(uptime, 3600)
        m, s = divmod(rem, 60)
        
        html = f"""
        <html>
            <head><title>SunloMusic Dashboard</title></head>
            <body style="background:#0a0a0a; color:#fff; font-family:sans-serif; text-align:center; padding:50px;">
                <h1 style="color:#00e0ff;">🎶 SunloMusic Live Dashboard</h1>
                <div style="background:#1a1a1a; padding:20px; border-radius:15px; display:inline-block; text-align:left; border:1px solid #333;">
                    <p><b>Status:</b> <span style="color:lime;">🟢 ONLINE</span></p>
                    <p><b>Uptime:</b> {h}h {m}m {s}s</p>
                    <p><b>Total Users:</b> {stats['users']}</p>
                    <p><b>Total Chats:</b> {stats['chats']}</p>
                    <p><b>Active VCs:</b> {active}</p>
                </div>
            </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")
    except Exception as e:
        return web.Response(text=f"Error: {e}", status=500)

async def _handle_movie_download(request):
    from SunloMusic.plugins.movies import get_movie_ddl_links
    
    movie_id = request.query.get("id")
    imdb_id = request.query.get("imdb", "")
    
    if not movie_id or not TMDB_API_KEY: return web.Response(text="Invalid Request.", status=400)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}") as resp:
                if resp.status != 200: return web.Response(text="Movie not found.", status=404)
                data = await resp.json()
    except: return web.Response(text="Error fetching data.", status=500)

    title = data.get("title", "Unknown")
    year = data.get("release_date", "N/A")[:4]
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview", "No description.")
    runtime = data.get("runtime", 0)
    genres = " • ".join([g["name"] for g in data.get("genres", [])])
    poster = f"{TMDB_IMG_BASE}{data.get('poster_path')}" if data.get("poster_path") else ""
    backdrop = f"{TMDB_IMG_BASE}{data.get('backdrop_path')}" if data.get("backdrop_path") else poster
    
    links = await get_movie_ddl_links(title, imdb_id)

    if not links:
        btn_html = """
        <div style="text-align: center; padding: 20px; background: rgba(255,0,0,0.1); border: 1px solid rgba(255,0,0,0.3); border-radius: 12px;">
            <h3 style="color: #ff4444; margin-bottom: 10px;">⚠️ Download Not Available</h3>
            <p style="color: #ccc; font-size: 0.9rem;">This movie has no active torrents available right now on Torrentio or PirateBay.</p>
        </div>
        """
    else:
        btn_html = f"""
        <div class="btn-group">
            <a href="{links['4k']}" class="btn btn-4k"><span class="quality">4K UHD</span></a>
            <a href="{links['1080p']}" class="btn btn-1080p"><span class="quality">1080p FHD</span></a>
            <a href="{links['720p']}" class="btn btn-720p"><span class="quality">720p HD</span></a>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Download {title} | SunloMovies</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
            body {{ background-color: #0a0a0a; color: #fff; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; background-image: url('{backdrop}'); background-size: cover; background-position: center; background-attachment: fixed; }}
            body::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(10, 10, 10, 0.85); backdrop-filter: blur(15px); z-index: -1; }}
            .container {{ background: rgba(20, 20, 20, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 40px; max-width: 900px; width: 100%; display: flex; gap: 40px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); backdrop-filter: blur(20px); animation: fadeIn 0.8s ease-out; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            .poster-wrap {{ flex-shrink: 0; }}
            .poster {{ width: 300px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }}
            .info {{ flex-grow: 1; display: flex; flex-direction: column; justify-content: center; }}
            h1 {{ font-size: 2.5rem; font-weight: 800; margin-bottom: 5px; color: #fff; line-height: 1.2; }}
            .meta {{ display: flex; gap: 15px; font-size: 0.9rem; color: #bbb; margin-bottom: 15px; align-items: center; }}
            .rating {{ background: #f5c518; color: #000; padding: 2px 8px; border-radius: 5px; font-weight: bold; }}
            .plot {{ font-size: 0.95rem; color: #ccc; margin-bottom: 30px; line-height: 1.6; }}
            .download-title {{ font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; color: #00e0ff; }}
            .btn-group {{ display: flex; flex-direction: column; gap: 12px; }}
            .btn {{ display: flex; align-items: center; justify-content: space-between; padding: 15px 25px; border-radius: 12px; text-decoration: none; color: white; font-weight: 600; font-size: 1rem; transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden; }}
            .btn:hover {{ transform: translateY(-3px) scale(1.02); }}
            .btn::after {{ content: '⬇️'; font-size: 1.2rem; transition: 0.3s; }}
            .btn:hover::after {{ transform: translateY(3px); }}
            .btn-4k {{ background: linear-gradient(135deg, #8E2DE2, #4A00E0); box-shadow: 0 5px 15px rgba(142, 45, 226, 0.3); }}
            .btn-1080p {{ background: linear-gradient(135deg, #0078FF, #00C6FF); box-shadow: 0 5px 15px rgba(0, 198, 255, 0.3); }}
            .btn-720p {{ background: linear-gradient(135deg, #11998e, #38ef7d); box-shadow: 0 5px 15px rgba(56, 239, 125, 0.3); }}
            .btn-4k:hover {{ box-shadow: 0 8px 25px rgba(142, 45, 226, 0.6); }}
            .btn-1080p:hover {{ box-shadow: 0 8px 25px rgba(0, 198, 255, 0.6); }}
            .btn-720p:hover {{ box-shadow: 0 8px 25px rgba(56, 239, 125, 0.6); }}
            .quality {{ font-size: 1.1em; font-weight: 800; letter-spacing: 1px; }}
            @media (max-width: 768px) {{ .container {{ flex-direction: column; align-items: center; text-align: center; padding: 20px; gap: 20px; }} .poster {{ width: 200px; }} h1 {{ font-size: 1.8rem; }} .meta {{ justify-content: center; }} .btn {{ justify-content: center; gap: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="poster-wrap"><img src="{poster}" class="poster" alt="Poster"></div>
            <div class="info">
                <h1>{title}</h1>
                <div class="meta"><span>{year}</span><span class="rating">⭐ {rating}/10</span><span>{runtime} min</span></div>
                <div class="meta" style="font-size:0.8rem; color:#888;">{genres}</div>
                <div class="plot">{overview}</div>
                <div class="download-title">⬇️ High-Speed Downloads</div>
                {btn_html}
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")

async def _background_pinger():
    await asyncio.sleep(60)
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url: return
    ping_url = f"{url.rstrip('/')}/ping"
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(ping_url, timeout=10) as resp: await resp.read()
            except: pass
            await asyncio.sleep(600)

async def start_keep_alive():
    app = web.Application()
    app.router.add_get("/", _handle_dashboard)
    app.router.add_get("/ping", _handle_ping)
    app.router.add_get("/movie", _handle_movie_download) 
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    LOGGER.info(f"✅ Web Server running on port {port}")
    asyncio.create_task(_background_pinger())
