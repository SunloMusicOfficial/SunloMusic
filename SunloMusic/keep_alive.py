import asyncio, os, time, aiohttp
from aiohttp import web
from SunloMusic.logger import LOGGER
from SunloMusic.config import config
from SunloMusic.database import get_stats
from SunloMusic.queues import active_chats

START_TIME = time.time()

# ✅ HTML + CSS + JS for Web App
WEB_APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SunloMusic Premium</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--tg-theme-bg-color, #121212); color: var(--tg-theme-text-color, #ffffff); padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 24px; background: -webkit-linear-gradient(45deg, #00e0ff, #8a2be2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .header p { color: #888; font-size: 14px; margin-top: 5px; }

        .btn { display: flex; align-items: center; justify-content: center; padding: 18px; border-radius: 12px; font-size: 16px; font-weight: bold; text-decoration: none; color: white; transition: transform 0.2s, opacity 0.2s; border: none; cursor: pointer; width: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .btn:active { transform: scale(0.96); opacity: 0.8; }
        
        /* Colorful Gradients */
        .btn-green { background: linear-gradient(135deg, #11998e, #38ef7d); }
        .btn-blue { background: linear-gradient(135deg, #2193b0, #6dd5ed); }
        .btn-purple { background: linear-gradient(135deg, #8E2DE2, #4A00E0); }
        .btn-orange { background: linear-gradient(135deg, #f12711, #f5af19); }
        .btn-red { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
        
        .row { display: flex; gap: 15px; width: 100%; }
        .row .btn { flex: 1; padding: 18px 10px; font-size: 15px; }

        .icon { margin-right: 8px; font-size: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SunloMusic Premium</h1>
        <p>Your Ultimate Music Companion</p>
    </div>

    <button class="btn btn-green" onclick="addGroup()">
        <span class="icon">➕</span> ADD ME TO YOUR GROUP
    </button>

    <div class="row">
        <button class="btn btn-blue" onclick="sendCmd('/help')">
            <span class="icon">⏳</span> HELP
        </button>
        <button class="btn btn-blue" onclick="openLink('https://t.me/YO_UR_OFFICIAL_CRUSH')">
            <span class="icon">💬</span> SUPPORT
        </button>
    </div>

    <div class="row">
        <button class="btn btn-purple" onclick="openLink('https://t.me/Vip_Sakil_Bio')">
            <span class="icon">📢</span> UPDATES
        </button>
        <button class="btn btn-red" onclick="sendCmd('/allcommand')">
            <span class="icon">📜</span> COMMANDS
        </button>
    </div>

    <button class="btn btn-orange" onclick="openLink('https://t.me/YO_UR_OFFICIAL_CRUSH')" style="margin-top: 20px;">
        <span class="icon">👨‍💻</span> MY DEV
    </button>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand(); // Full screen
        
        function sendCmd(cmd) {
            tg.sendData(JSON.stringify({ command: cmd }));
            tg.close();
        }
        
        function addGroup() {
            tg.openTelegramLink("https://t.me/SunloMusicBot?startgroup=true");
        }

        function openLink(url) {
            tg.openTelegramLink(url);
        }
    </script>
</body>
</html>
"""

async def _handle_ping(request):
    return web.Response(text="SunloMusic is alive!", status=200)

# ✅ Web App Route
async def _handle_webapp(request):
    return web.Response(text=WEB_APP_HTML, content_type="text/html")

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
    app.router.add_get("/", _handle_dashboard)
    app.router.add_get("/ping", _handle_ping)
    app.router.add_get("/app", _handle_webapp) # ✅ Web App Route
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    LOGGER.info(f"✅ Keep-Alive Web Server running on port {port}")
    
    asyncio.create_task(_background_pinger())
