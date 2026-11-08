<div align="center">

# 🎧 SunloMusic

**A Telegram voice-chat music & video bot.**

Stream YouTube tracks (or your own audio/video files) straight into a group voice chat — with a rich inline player, playlists, audio effects, live-call title updates, and per-group rankings.

<a href="https://codeberg.org/SunloMusicOfficial/SunloMusic/stars"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcodeberg.org%2Fapi%2Fv1%2Frepos%2FSunloMusicOfficial%2FSunloMusic&query=%24.stars_count&label=Stars&color=blue&style=flat" alt="Codeberg stars"></a>
<a href="https://codeberg.org/SunloMusicOfficial/SunloMusic/forks"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcodeberg.org%2Fapi%2Fv1%2Frepos%2FSunloMusicOfficial%2FSunloMusic&query=%24.forks_count&label=Forks&style=flat" alt="Codeberg forks"></a>
<a href="https://codeberg.org/SunloMusicOfficial/SunloMusic/issues"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcodeberg.org%2Fapi%2Fv1%2Frepos%2FSunloMusicOfficial%2FSunloMusic&query=%24.open_issues_count&label=Issues&style=flat" alt="Codeberg issues"></a>
<a href="https://codeberg.org/SunloMusicOfficial/SunloMusic/pulls"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcodeberg.org%2Fapi%2Fv1%2Frepos%2FSunloMusicOfficial%2FSunloMusic&query=%24.open_pr_counter&label=Pull%20Requests&style=flat" alt="Codeberg pull requests"></a>
<br>
<img src="https://img.shields.io/badge/Python-3.11-blue" alt="Python 3.11">
<img src="https://img.shields.io/badge/Database-MongoDB-green" alt="MongoDB">
<img src="https://img.shields.io/badge/Streaming-py--tgcalls-orange" alt="py-tgcalls">
<img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT License">

</div>

---

## 📑 Jump to

- [Features](#features) · [Requirements](#requirements) · [Quick start](#quick-start) · [Setup](#setup) · [Configuration](#configuration)
- [Commands](#commands) · [Audio effects](#effects) · [Settings](#settings) · [Rankings](#rankings)
- [Troubleshooting](#troubleshooting) · [Known Issues](#known-issues) · [Contributing](#contributing) · [Support](#support) · [License](#license)

---

<a id="features"></a>

## ✨ Features

- 🎵 **Music & video streaming** — play YouTube audio *or* video into a voice chat.
- 🎛 **Inline player** — pause / resume / skip / stop / seek / rewind / replay / volume, all from buttons.
- 🎚 **Audio effects** — Bass Boost, Nightcore, Slowed, Lofi, 8D.
- ⏩ **Playback speed** — from `0.5x` to `2.0x`.
- 🔁 **Loop modes** — off / repeat-track / repeat-queue.
- 📜 **Playlists** — load a whole YouTube playlist (lazy-fetched 10 tracks at a time), plus save / load / delete named playlists.
- 🏆 **Rankings** — daily, weekly and global top-listeners, rendered as banner images.
- 📎 **Telegram files** — reply to an audio/video file to queue it directly.
- 🔴 **Live streams** — plays YouTube live streams.
- 🔍 **Inline search** — type `@YourBot song name` in any chat to search YouTube.
- 🎯 **Live call title** — updates the group call title to the currently playing track.
- 👋 **Voice-chat welcome** — greets listeners inside the voice chat when they join.
- 👥 **Multi-chat** — serves many groups at once.
- 🛡 **Permissions** — group-admins plus a per-group "VC admin" system.
- 📡 **Broadcast** — owner-only message broadcast to all users/groups.

---

<a id="requirements"></a>

## 📋 Requirements

**Runtime (not installable via pip):**

| Dependency | Why | Install |
| --- | --- | --- |
| **Python 3.11** | runtime | [python.org](https://www.python.org/) |
| **ffmpeg** | audio effects + re-encoding | `apt install ffmpeg` (or [ffmpeg.org](https://ffmpeg.org/)) |
| **`yt-dlp` CLI** | live-stream URL extraction | installed automatically by `run.sh` |
| **MongoDB** | all persistence | [mongodb.com](https://www.mongodb.com/) or [Atlas](https://www.mongodb.com/atlas) |
| **Deno** | YouTube JS-challenge solving for `yt-dlp` | installed automatically by `run.sh` |

> **Note on Deno:** it is **required** for solving YouTube's JS challenges. `run.sh` installs it automatically if missing.

Python packages are listed in [`requirements.txt`](requirements.txt) and installed automatically by `run.sh`.

---

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone <your-repo-url>
cd SunloMusic

# 1. Fill in your credentials
cp .env.example .env
nano .env

# 2. Add your YouTube cookies (see "YouTube cookies" below)
mkdir -p cookies
# place your Netscape-format cookies at cookies/yt.txt

# 3. Run (installs deps + yt-dlp + ffmpeg, then launches)
./run.sh
```

That's it. `run.sh` is idempotent — it installs/upgrades Python dependencies, `yt-dlp`, and `ffmpeg` if missing, then starts the bot.

To run without `run.sh`:

```bash
pip install -r requirements.txt
python3.11 bot.py
```

---

<a id="setup"></a>

## 🔐 Setup in detail

### 1. Get your API credentials

1. Go to [my.telegram.org](https://my.telegram.org) and log in.
2. Create an app to get **`API_ID`** and **`API_HASH`**.
3. Create your bot with [@BotFather](https://t.me/BotFather) to get **`BOT_TOKEN`**.

### 2. Get a user `SESSION_STRING`

The bot uses **two** accounts:

- `SunloMusic` — your bot (runs on `BOT_TOKEN`).
- `user_client` — a **user** account (runs on `SESSION_STRING`). This is the account that actually joins the voice chat and streams, because Telegram requires a *user* (not a bot) to stream audio in a voice chat.

Generate the session string using [@TgDevToolBot](https://t.me/TgDevToolBot):

1. Open Telegram and start **[@TgDevToolBot](https://t.me/TgDevToolBot)**.
2. Select **🔐 Pyrogram Session** from the menu.
3. Enter your `API_ID` and `API_HASH` when prompted.
4. Log in with the **user account's** phone number and the OTP code.
5. Copy the resulting string into `.env` as `SESSION_STRING`.

### 3. MongoDB

Use a local MongoDB (`mongodb://localhost:27017/vcbot`) or a free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster. Put the URI in `.env`.

### 4. YouTube cookies

YouTube may block downloads from datacenter IPs ("Sign in to confirm you're not a bot"). To avoid this, export your browser's YouTube cookies in **Netscape format** and save them to `cookies/yt.txt`.

- Easiest method: a browser extension such as *Get cookies.txt LOCALLY*.
- The file must be Netscape/HTTP-cookie format (`# Netscape HTTP Cookie File` header followed by tab-separated rows).

---

<a id="configuration"></a>

## ⚙️ Configuration

All configuration lives in `.env` (see [`.env.example`](.env.example)).

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `API_ID` | ✅ | — | Telegram app ID |
| `API_HASH` | ✅ | — | Telegram app hash |
| `BOT_TOKEN` | ✅ | — | Bot token from BotFather |
| `SESSION_STRING` | ✅ | — | User-account string session |
| `MONGODB_URI` | ✅ | `mongodb://localhost:27017/vcbot` | MongoDB connection URI |
| `LOG_LEVEL` | — | `INFO` | Logging level |
| `LOG_CHAT_ID` | — | `0` | Chat ID to receive log notifications |
| `MAX_QUEUE_SIZE` | — | `100` | Max tracks per queue |
| `MAX_CONCURRENT_CHATS` | — | `50` | Max simultaneous voice chats |
| `MAX_PLAYLIST_TRACKS` | — | `50` | Max tracks loaded from a playlist |
| `MAX_TRACK_DURATION` | — | `7200` | Max track length (seconds) |
| `AUTOPLAY_BATCH_SIZE` | — | `5` | Related tracks queued when autoplay is allowed |
| `AUTOPLAY_PROMPT_TIMEOUT` | — | `90` | Seconds to wait for an answer to the autoplay prompt |

> **Note:** `BOT_OWNER_ID` (used for `/restart`, `/broadcast`, and `/logs`) is **hardcoded** in `SunloMusic/core/config.py`. Change it to your own Telegram user ID before deploying.

---

<a id="commands"></a>

## 🎮 Commands

Commands work with both `/` and `.` prefixes (e.g. `/play` or `.play`). Most work only in groups where the bot is present.

| Command | Description |
| --- | --- |
| `/start` | Show the welcome message |
| `/help` | Show help |
| `/play <query\|url\|playlist>` | Play a song / video / playlist from YouTube |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/skip` | Skip to the next track |
| `/stop` / `/end` | Stop and leave the voice chat |
| `/seek <seconds>` | Seek forward (+) or backward (−) |
| `/rewind` | Rewind 10 seconds |
| `/vcmute` | Mute the voice chat |
| `/vcunmute` | Unmute the voice chat |
| `/playlist` | Show the current queue |
| `/clearplaylist` | Clear upcoming tracks |
| `/settings` | Open the settings menu (admin) |
| `/vcadmin` | Grant voice-chat control to a user (admin) |
| `/vcunadmin` | Revoke voice-chat control (admin) |
| `/rank` / `/ranking` | View group rankings |
| `/status` | Show bot statistics |
| `/restart` | Restart the bot (owner) |
| `/broadcast` | Broadcast a replied-to message (owner) |
| `/logs` | View and clear the bot log file (owner) |

### Player inline buttons

The now-playing message includes a full control bar:

- ⏯ Pause / Resume, ⏭ Skip, ⏹ Stop
- 🔁 Loop (off / track / queue)
- ⏪ Rewind, ⏩ Seek, 🔃 Replay
- 🔊 Volume, 🔇/🔊 Mute / Unmute
- 🎚 Effects & ⏩ Speed menus
- 📜 Queue pager, 🔀 Shuffle, 🗑 Clear queue

---

<a id="effects"></a>

## 🎚 Audio effects & speed

| Effect | Button |
| --- | --- |
| Normal | 🎵 Normal |
| Bass Boost | 🔊 Bass Boost |
| Nightcore | ⚡ Nightcore |
| Slowed | 🐢 Slowed |
| Lofi | 📻 Lofi |
| 8D | 🎧 8D |

Playback speed presets: `0.5x`, `0.75x`, `1.0x`, `1.25x`, `1.5x`, `2.0x`.

---

<a id="settings"></a>

## ⚙️ Settings

Open with `/settings` (admin). Available toggles:

- **Mode** — audio or video
- **Quality** — 360p / 480p / 720p / 1080p
- **Audio quality** — low / medium / high
- **Autoplay** — when the queue drains, ask whether to keep playing related songs
- **Title update** — update the live call title to the current track
- **Admin-only mode** — restrict playback to admins/VC-admins
- **Shuffle**
- **Mention requester**
- **Playlist permission** — who may load playlists (everyone / admins)
- **Autoplay permission** — who may answer the autoplay prompt (everyone / admins)
- **VC Welcome** — greet listeners when they join the voice chat

### Autoplay

With **Autoplay** on, the bot never starts related songs on its own — it asks first.
When the last queued track ends, it posts the track it just played with two buttons:

| Button | Result |
| --- | --- |
| **Play Related Songs** | Queues `AUTOPLAY_BATCH_SIZE` related tracks (from YouTube's own related list) and keeps playing |
| **No Thanks** | Stops playback and leaves the voice chat |

If nobody answers within `AUTOPLAY_PROMPT_TIMEOUT` seconds, playback stops. When the
related batch drains, the bot asks again — so it behaves like a radio while still
giving the group a decision point. Related songs are only offered when the last track
was a YouTube one; tracks longer than `MAX_TRACK_DURATION` are skipped.

**Autoplay permission** decides who may press those buttons:

- **Everyone** (default) — any member of the group can answer
- **Admins** — only group admins and VC admins can answer; others get an alert

---

<a id="vc-welcome"></a>

## 👋 Voice-chat welcome

When someone joins the voice chat while music is playing, the assistant posts a short
greeting **inside the call** — the text bubble that appears over the voice chat:

> 👋 Welcome, Alex! Enjoy the music 🎶

Each listener is greeted **once per call**. If they leave and rejoin the same voice chat,
nothing is sent; when the call ends and a new one starts, they are greeted again. The
assistant never greets itself.

Turn it off per group with **👋 VC Welcome** in `/settings` (on by default).

Two things to know:

- Greetings use Telegram's in-call messages, which only exist while the assistant is in
  the call — so they appear during playback, not in the group's message history.
- The voice chat must have **messages enabled** (an admin setting in Telegram). If they
  are off, Telegram rejects the message; the bot logs why and posts nothing to the group
  instead of falling back to a normal chat message.

---

<a id="rankings"></a>

## 🏆 Rankings

`/rank` renders a banner image of top listeners.

- **Daily** and **Weekly** — per-group.
- **Global** — across all groups.

Switch between them using the inline buttons on the ranking message.

---

<a id="troubleshooting"></a>

## ❓ Troubleshooting

| Problem | Fix |
| --- | --- |
| **"Sign in to confirm you're not a bot"** | YouTube is bot-checking your IP. Add/refresh `cookies/yt.txt`, or route through a proxy/residential IP. |
| **"Network is unreachable" to `googlevideo.com`** | YouTube CDN is unreachable from your server. Try a different region or a proxy. |
| **Download fails for some tracks** | Make sure `yt-dlp` is up to date (`pip install -U yt-dlp`). |
| **User account won't join the call** | The user account must be in the group and the bot must be admin. |
| **Title doesn't update** | The user account needs the **"Manage Voice Chats"** admin permission. |
| **`SESSION_STRING` invalid** | Regenerate the string session (see Setup). |

---

<a id="known-issues"></a>

## 🐛 Known Issues

### Bot doesn't leave the voice chat when an audio effect is applied

When a track plays with an **audio effect** (Bass Boost, Nightcore, Slowed, Lofi, or 8D), the bot may not auto-leave the voice chat after it ends. With **🎵 Normal**, it leaves correctly.

The effect runs through an FFmpeg filter chain that can block the end-of-stream signal, so the bot doesn't detect that the track has finished. The fix belongs in `SunloMusic/services/stream.py` (end-of-stream detection) and `SunloMusic/services/effects.py` (filter chain) — contributions welcome!

---

<a id="contributing"></a>

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo and clone your fork.
2. Install **Python 3.11** and the dependencies (`pip install -r requirements.txt`).
3. Make your changes, keeping the style consistent with the rest of the project.
4. Test by running the bot (`python3.11 bot.py`) and checking `logs/bot.log`.
5. Open a pull request describing what changed and why.

Don't commit secrets — `.env`, `*.session*`, and `cookies/yt.txt` are gitignored.

---

<a id="support"></a>

## 💬 Support

- **Update channel:** [@YO_UR_OFFICIAL_CRUSH](https://t.me/YO_UR_OFFICIAL_CRUSH)
- **Discussion chat:** [@Vip_Sakil_Bio](https://t.me/Vip_Sakil_Bio)

---

<a id="license"></a>

## 📄 License & credits

This project is licensed under the **[MIT License](LICENSE)**. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell the software, provided the copyright notice above is included in all copies or substantial portions.

© [@YO_UR_OFFICIAL_CRUSH](https://github.com/YO_UR_OFFICIAL_CRUSH) — copyright holder.

Built with [Pyrogram](https://github.com/pyrogram/pyrogram) (via the *kurigram* fork), [py-tgcalls](https://github.com/pytgcalls/pytgcalls), [ntgcalls](https://github.com/pytgcalls/ntgcalls), [yt-dlp](https://github.com/yt-dlp/yt-dlp), [MongoDB/motor](https://www.mongodb.com/docs/drivers/motor/), [Pillow](https://python-pillow.org/) and [numpy](https://numpy.org/).

---

## Ethical Notice 🔔

> **Ethics Reminder:** Simply modifying a few lines of code does not constitute original authorship. When forking a project, always fork responsibly and give proper credit to the original creators.
