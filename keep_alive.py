import os
import threading
import time
import requests
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "SunloMusic Bot is Alive!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def get_external_url():
    # 1. Render (Automatic)
    if os.environ.get("RENDER_EXTERNAL_URL"):
        return os.environ.get("RENDER_EXTERNAL_URL")
    # 2. Koyeb (Automatic)
    if os.environ.get("KOYEB_PUBLIC_DOMAIN"):
        return f"https://{os.environ.get('KOYEB_PUBLIC_DOMAIN')}"
    # 3. Railway (Automatic)
    if os.environ.get("RAILWAY_PUBLIC_DOMAIN"):
        return f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}"
    # 4. Heroku (Automatic)
    if os.environ.get("HEROKU_APP_NAME"):
        return f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com"
    # 5. Fly.io (Automatic)
    if os.environ.get("FLY_APP_NAME"):
        return f"https://{os.environ.get('FLY_APP_NAME')}.fly.dev"
    
    return None

def ping_self():
    url = get_external_url()
    
    if not url:
        print("⚠️ URL not detected. Make sure you deployed as a Web Service.")
        return
    
    print(f"✅ Auto-detected URL: {url}")
    print("⏳ Self-ping started (every 12 minutes)...")
    
    while True:
        time.sleep(720) # 12 minutes
        try:
            requests.get(url)
            print(f"✅ Self-ping successful at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Self-ping failed: {e}")

def keep_alive():
    t1 = threading.Thread(target=run_web_server)
    t1.daemon = True
    t1.start()
    
    t2 = threading.Thread(target=ping_self)
    t2.daemon = True
    t2.start()
