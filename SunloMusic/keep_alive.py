import asyncio
import os
import time
import aiohttp
from aiohttp import web
from SunloMusic.logger import LOGGER
from SunloMusic.bot import bot
from SunloMusic.config import config

START_TIME = time.time()

async def _ping_url(url: str, session: aiohttp.ClientSession) -> float:
    try:
        start = time.time()
        async with session.get(url, timeout=10) as resp:
            await resp.read()
            latency = (time.time() - start) * 1000
            return latency
    except Exception:
        return 0.0

async def _send_premium_log(latency: float, status: str):
    if not config.LOGGER_ID:
        return
    uptime_sec = int(time.time() - START_TIME)
    h, rem = divmod(uptime_sec, 3600)
    m, s = divmod(rem, 60)
    uptime_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
    
    # Premium HTML Log Card
    text = (
        f"<b>🛡️ SunloMusic Keep-Alive Monitor</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 <b>Status:</b> {status}\n"
        f"⚡ <b>Latency:</b> <code>{latency:.2f} ms</code>\n"
        f"⏱️ <b>Uptime:</b> <code>{uptime_str}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>System is active. Sleep prevention successful.</i>"
    )
    try:
        await bot.send_message(config.LOGGER_ID, text)
    except Exception as e:
        LOGGER.error(f"Failed to send premium log: {e}")

async def _background_pinger():
    await asyncio.sleep(60) # Initial startup delay
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        LOGGER.warning("⚠️ RENDER_EXTERNAL_URL not found. Self-ping disabled.")
        return
    
    ping_url = f"{url.rstrip('/')}/ping"
    LOGGER.info(f"🚀 Self-ping engine started for: {ping_url}")
    
    async with aiohttp.ClientSession() as session:
        while True:
            latency = await _ping_url(ping_url, session)
            if latency > 0:
                await _send_premium_log(latency, "🟢 Active & Healthy")
            else:
                await _send_premium_log(0.0, "🔴 Ping Failed")
            await asyncio.sleep(600) # Ping every 10 minutes

async def _handle_ping(request):
    return web.Response(text="SunloMusic is alive!", status=200)

async def start_keep_alive():
    app = web.Application()
    app.router.add_get("/", _handle_ping)
    app.router.add_get("/ping", _handle_ping)
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    LOGGER.info(f"✅ Keep-Alive Web Server running on port {port}")
    
    asyncio.create_task(_background_pinger())
