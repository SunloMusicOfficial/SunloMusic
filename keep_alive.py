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

def ping_self():
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        return
    while True:
        time.sleep(720) # 12 minutes
        try:
            requests.get(url)
        except Exception:
            pass

def keep_alive():
    t1 = threading.Thread(target=run_web_server)
    t1.daemon = True
    t1.start()
    
    t2 = threading.Thread(target=ping_self)
    t2.daemon = True
    t2.start()
