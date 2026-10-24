<h1 align="center">
  <img src="https://telegra.ph/file/b811802a46e1c15f9d254.gif" alt="Premium Banner" width="100%">
</h1>

<h2 align="center">✦ SUNLO MUSIC PREMIUM ✦</h2>

<p align="center">
  <a href="https://github.com/python/cpython"><img src="https://img.shields.io/badge/Python-3.9%2B-black?style=for-the-badge&logo=python&logoColor=yellow"></a>
  <a href="https://github.com/KuramDas/pyrofork"><img src="https://img.shields.io/badge/Pyrofork-v2.3-black?style=for-the-badge&logo=telegram&logoColor=blue"></a>
  <a href="https://github.com/pytgcalls/pytgcalls"><img src="https://img.shields.io/badge/PyTgCalls-v2.1-black?style=for-the-badge&logo=webrtc&logoColor=red"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-Server-black?style=for-the-badge&logo=fastapi&logoColor=009688"></a>
</p>

<p align="center">
  <b>A Next-Generation, Scalable, and Lag-Free Telegram Music Bot.</b><br>
  <i>Designed for ultimate speed, flawless audio quality, and zero YouTube IP bans.</i>
</p>

<hr>

### 🚀 **Why Choose SunloMusic?**

🌟 **Anti-429 Engine:** Seamlessly bypasses YouTube IP bans using dynamic API routing (OneGrab/Saavn).
⚡ **24/7 Uninterrupted:** Built-in web server and Keep-Alive pinger ensures Render/VPS never sleeps.
🛡️ **Smart Storage:** Auto-cleans cache on startup to prevent disk space overflow.
🔔 **Premium Logging:** Beautiful visual logs with inline buttons sent directly to your control group.
📈 **Fully Asynchronous:** Handled by Pyrogram v2 & FastAPI for handling massive server loads.

<hr>

### ⚙️ **Configuring Variables (.env)**

Rename <code>sample.env</code> to <code>.env</code> and fill in your details:

| Variable | Description |
| :--- | :--- |
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Bot Token from [@BotFather](https://t.me/BotFather) |
| `SESSION_STRING` | Pyrogram v2 Session string for Assistant Account |
| `MONGO_URI` | MongoDB Connection URL for Database |
| `OWNER_ID` | Your Telegram User ID |
| `LOG_GROUP_ID` | ID of your Log Group (Must start with `-100`) |
| `STREAM_API_URL` | Optional: Your API URL (e.g., `https://api.onegrab.fun`) |
| `WEB_URL` | Optional: Render/Server Web URL for 24/7 Keep-Alive |

<hr>

### 🌐 **One-Click Deployment**

Deploy directly to your favorite cloud platforms with zero hassle:

<p align="left">
  <a href="https://render.com/deploy">
    <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
  </a>
  &nbsp;&nbsp;
  <a href="https://app.koyeb.com/deploy">
    <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb">
  </a>
</p>

<details>
<summary><b>💻 VPS / Local Deployment (Click to Expand)</b></summary>
<br>
Run these commands in your Ubuntu/Debian terminal:

<pre><code>sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install python3 python3-pip git ffmpeg -y
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
pip3 install -U -r requirements.txt
cp sample.env .env
nano .env # Fill your variables
python3 main.py
</code></pre>
</details>

<hr>

### 📋 **Core Commands**

* `/play <song name>` - Stream music/video on Voice Chat.
* `/queue` - Check the upcoming tracks.
* `/stats` - View global server, CPU, and RAM statistics.
* `/join` - Force assistant to join the group.
* `/reboot` - Restart the bot remotely.

<hr>
<p align="center">
  <b>Developed & Maintained by <a href="https://t.me/YO_UR_OFFICIAL_CRUSH">@YO_UR_OFFICIAL_CRUSH</a></b><br>
  <i>Open Source & Proudly Developed for the Community 🎵</i>
</p>
