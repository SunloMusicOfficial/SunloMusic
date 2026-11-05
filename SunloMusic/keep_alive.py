import asyncio, os, time, aiohttp
from aiohttp import web
from SunloMusic.logger import LOGGER
from SunloMusic.config import config
from SunloMusic.database import get_stats
from SunloMusic.queues import active_chats

START_TIME = time.time()

# ✅ TMDB API Key (Render Environment me add kar)
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

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
            <body style="background:#111; color:#fff; font-family:sans-serif; text-align:center; padding:50px;">
                <h1 style="color:#00e0ff;">🎶 SunloMusic Live Dashboard</h1>
                <div style="background:#222; padding:20px; border-radius:10px; display:inline-block; text-align:left;">
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
        return web.Response(text=f"Error loading dashboard: {e}", status=500)

# ✅ NEW: Movie Download Website
async def _handle_movie_download(request):
    movie_id = request.query.get("id")
    movie_title = request.query.get("title", "Movie")
    poster = request.query.get("poster", "")
    
    # Agar TMDB ID hai, toh poster fetch karte hain
    if movie_id and TMDB_API_KEY and not poster:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        poster = f"{TMDB_IMG_BASE}{data.get('poster_path')}" if data.get("poster_path") else ""
                        movie_title = data.get("title", movie_title)
        except: pass

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Download {movie_title} | SunloMovies</title>
        <style>
            body {{ background: #0f0f0f; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
            .container {{ background: #1a1a1a; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 500px; width: 100%; text-align: center; border: 1px solid #333; }}
            .poster {{ width: 200px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
            h1 {{ color: #00e0ff; margin: 10px 0; font-size: 1.5em; }}
            p {{ color: #aaa; font-size: 0.9em; margin-bottom: 20px; }}
            .btn {{ display: block; width: 100%; padding: 15px; margin: 10px 0; background: linear-gradient(90deg, #e50914, #ff0a16); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em; box-sizing: border-box; transition: 0.3s; border: none; cursor: pointer; }}
            .btn:hover {{ transform: scale(1.02); box-shadow: 0 0 15px rgba(229, 9, 20, 0.6); }}
            .btn-alt {{ background: linear-gradient(90deg, #0078FF, #00C6FF); }}
            .btn-alt:hover {{ box-shadow: 0 0 15px rgba(0, 198, 255, 0.6); }}
            .footer {{ margin-top: 20px; font-size: 0.8em; color: #555; }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="{poster}" class="poster" alt="Poster">
            <h1>{movie_title}</h1>
            <p>High-Speed Download Link (No Ads, No Limits)</p>
            
            <!-- ✅ Yahan Tu Apne Asli Download Links Dalega (GDrive, Mega, DDL) -->
            <a href="https://your-download-link.com/1080p" class="btn">⬇️ Download 1080p (2.5GB)</a>
            <a href="https://your-download-link.com/720p" class="btn btn-alt">⬇️ Download 720p (1.2GB)</a>
            <a href="https://your-download-link.com/480p" class="btn btn-alt">⬇️ Download 480p (700MB)</a>
            
            <div class="footer">© 2024 SunloMovies. All rights reserved.</div>
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
    app.router.add_get("/movie", _handle_movie_download) # ✅ Website Route
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    LOGGER.info(f"✅ Keep-Alive Web Server running on port {port}")
    
    asyncio.create_task(_background_pinger())
