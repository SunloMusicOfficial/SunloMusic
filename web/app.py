import time
import psutil
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from core.call import sunlo_call
from config.vars import Config

app = FastAPI(title="SunloMusic Dashboard")
START_TIME = time.time()

def get_uptime():
    seconds = int(time.time() - START_TIME)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {mins}m {secs}s"

@app.get("/", response_class=HTMLResponse)
async def home():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    active_vcs = len(sunlo_call.active_calls) if sunlo_call.active_calls else 0
    
    html_content = f"""
    <html>
        <head>
            <title>{Config.BOT_NAME} - Live Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; text-align: center; padding: 50px; }}
                .card {{ background: #1e1e1e; padding: 20px; border-radius: 10px; display: inline-block; margin: 10px; width: 200px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
                h1 {{ color: #1DB954; }}
                h2 {{ margin: 0; font-size: 2em; }}
                p {{ color: #aaaaaa; }}
            </style>
        </head>
        <body>
            <h1>🎵 {Config.BOT_NAME} Engine</h1>
            <p>Live Server Health & Stats</p>
            
            <div class="card">
                <h2>{active_vcs}</h2>
                <p>Active Voice Chats</p>
            </div>
            <div class="card">
                <h2>{cpu}%</h2>
                <p>CPU Usage</p>
            </div>
            <div class="card">
                <h2>{ram}%</h2>
                <p>RAM Usage</p>
            </div>
            <div class="card">
                <h2>{get_uptime()}</h2>
                <p>Server Uptime</p>
            </div>
        </body>
    </html>
    """
    return html_content
