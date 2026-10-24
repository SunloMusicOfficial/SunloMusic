<p align="center">
  <img src="https://telegra.ph/file/c5952793fa720b08db669.jpg" alt="SunloMusic Premium Banner">
</p>

<h1 align="center">🎧 SunloMusic Premium</h1>

<p align="center">
  <a href="https://github.com/python/cpython"><img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python"></a>
  <a href="https://github.com/KuramDas/pyrofork"><img src="https://img.shields.io/badge/Pyrofork-Latest-orange.svg?style=for-the-badge&logo=telegram"></a>
  <a href="https://github.com/pytgcalls/pytgcalls"><img src="https://img.shields.io/badge/PyTgCalls-2.1.0-red.svg?style=for-the-badge&logo=webrtc"></a>
  <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-Atlas-green.svg?style=for-the-badge&logo=mongodb"></a>
</p>

<p align="center">
  <b>An Enterprise-Grade, High-Performance Telegram Voice Chat Music Bot.</b><br>
  <i>Built with bypass mechanisms for YouTube Error 429, 24/7 Keep-Alive capabilities, and intelligent Auto-VC startup.</i>
</p>

---

## ✨ Premium Features

*   **🛡️ Anti-IP Block Engine:** Integrated with external APIs (like OneGrab) to permanently bypass YouTube's Error 429.
*   **⚡ Auto-VC Startup:** Automatically turns on group Voice Chats if they are off.
*   **🔄 24/7 Keep-Alive:** Built-in self-pinging FastAPI server to prevent Render/Heroku from sleeping.
*   **🔔 Premium Logging:** Beautiful startup cards and ping statuses sent directly to your log group.
*   **🎮 Gamification:** Interactive economy system, leaderboards, and user profiles.
*   **🧹 Auto-Cache Cleaner:** Smart storage management to keep your server disk space free.

---

## 🛠️ Environment Variables (.env)

Rename sample.env to .env and fill in your details:

| Variable | Description | Required |
| :--- | :--- | :---: |
| API_ID | Your Telegram API ID from my.telegram.org | Yes |
| API_HASH | Your Telegram API Hash from my.telegram.org | Yes |
| BOT_TOKEN | Your Bot Token from @BotFather | Yes |
| SESSION_STRING | Pyrogram v2 string session for the Assistant | Yes |
| MONGO_URI | MongoDB Atlas Connection URL | Yes |
| OWNER_ID | Your Telegram User ID for admin rights | Yes |
| LOG_GROUP_ID | Group ID (starting with -100) for bot logs | Yes |
| STREAM_API_URL | API URL for YouTube Bypass | Optional |
| STREAM_API_KEY | API Key if your custom provider requires one | Optional |
| WEB_URL | Your deployed app URL (for Render Keep-Alive) | Optional |

---

## 🚀 Deployment Guides

### 1. Local / VPS Deployment (Ubuntu / Debian)
The most recommended and stable method for hosting.

    # Update and install dependencies
    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install python3 python3-pip git ffmpeg -y

    # Clone the repository
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME

    # Install requirements
    pip3 install -U -r requirements.txt

    # Create and configure .env
    cp sample.env .env
    nano .env # Fill in your details, then press Ctrl+X, Y, Enter

    # Start the bot
    python3 main.py

### 2. Deploy on Render
Render puts free apps to sleep after 15 minutes of inactivity. Our **built-in Keep-Alive system** prevents this by self-pinging the WEB_URL.

1. Create an account on Render.com.
2. Create a new **Web Service** and connect your GitHub repository.
3. Use the following configuration:
   * Build Command: pip install -r requirements.txt
   * Start Command: python main.py
4. Go to **Environment Variables** and add all variables from the .env section above.
5. Copy the generated Render Web URL (e.g., https://mybot.onrender.com), add it as WEB_URL in your variables, and Deploy.

### 3. Deploy on Koyeb
1. Create an account on app.koyeb.com.
2. Create a new App and choose GitHub as your deployment method.
3. In the environment variables section, securely add all required .env details.
4. Set the run command to: python main.py
5. Click **Deploy**.

---

## 📖 Basic Commands Reference

*   /play <song name/link> - Play music in the voice chat.
*   /queue - View the upcoming song list.
*   /join - Force the assistant to join the group.
*   /stats - View global server stats, CPU/RAM usage, and uptime.
*   /update - Auto-pull latest updates from GitHub (Owner only).
*   /gcast - Broadcast a message to all users (Owner only).

---
<p align="center">
  <i>Developed with ❤️ for the Telegram Community</i>
</p>
