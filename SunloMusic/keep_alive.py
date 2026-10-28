import asyncio, os, time, aiohttp
from aiohttp import web
from SunloMusic.logger import LOGGER
from SunloMusic.config import config
from SunloMusic.database import get_stats
from SunloMusic.queues import active_chats

START_TIME = time.time()

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
            <head><title>SunloMusic Dashboard</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
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
    app.router.add_get("/", _handle_dashboard) # ✅ Dashboard
    app.router.add_get("/ping", _handle_ping)
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    LOGGER.info(f"✅ Keep-Alive Web Server running on port {port}")
    
    asyncio.create_task(_background_pinger())
