#!/usr/bin/env bash
# Copyright (C) @YO_UR_OFFICIAL_CRUSH

# Run the SunloMusic bot: install/upgrade Python deps + yt-dlp + ffmpeg, then launch.
set -euo pipefail

cd "$(dirname "$0")"

# --- Python interpreter ---
if command -v python3.11 >/dev/null 2>&1; then
    PYTHON=python3.11
elif command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    echo "Error: no Python 3 interpreter found on PATH" >&2
    exit 1
fi

echo "==> Using $($PYTHON --version 2>&1)"

# --- Python dependencies (idempotent: no-op if already satisfied) ---
echo "==> Installing Python dependencies"
"$PYTHON" -m pip install -r requirements.txt

# --- yt-dlp: upgrades the library AND installs the yt-dlp CLI on PATH ---
echo "==> Upgrading yt-dlp (library + CLI)"
"$PYTHON" -m pip install -U "yt-dlp[default]"

# --- Deno (OPTIONAL): external JS runtime yt-dlp can use for YouTube JS challenges.
#     NOT required — yt-dlp ships a bundled engine via the yt-dlp-ejs package installed above.
#     Deno only makes YouTube "nsig" challenge solving faster / more robust.
DENO_BIN="$HOME/.deno/bin/deno"
if command -v deno >/dev/null 2>&1; then
    echo "==> Deno found: $(deno --version 2>/dev/null | head -1)"
elif [ -x "$DENO_BIN" ]; then
    export PATH="$HOME/.deno/bin:$PATH"
    echo "==> Deno found at ~/.deno/bin/deno"
elif command -v curl >/dev/null 2>&1; then
    echo "==> Deno missing; installing (optional JS runtime for yt-dlp)"
    if curl -fsSL https://deno.land/install.sh | sh; then
        export PATH="$HOME/.deno/bin:$PATH"
        echo "==> Deno installed to ~/.deno/bin"
    else
        echo "Warning: Deno install failed (skipping — not required)" >&2
    fi
else
    echo "==> Deno missing and curl unavailable; skipping (not required)" >&2
fi

# --- ffmpeg: system binary, not pip-installable ---
if command -v ffmpeg >/dev/null 2>&1; then
    echo "==> ffmpeg found: $(ffmpeg -version 2>/dev/null | head -1)"
else
    echo "==> ffmpeg missing; trying apt-get"
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -y && apt-get install -y ffmpeg || echo "Warning: apt-get failed to install ffmpeg" >&2
    else
        echo "Warning: no apt-get on PATH; install ffmpeg manually (https://ffmpeg.org)" >&2
    fi
fi

# --- Final sanity check ---
command -v yt-dlp >/dev/null 2>&1 || echo "Warning: yt-dlp CLI not on PATH" >&2
command -v ffmpeg  >/dev/null 2>&1 || echo "Warning: ffmpeg not on PATH" >&2

echo "==> Starting bot"
exec "$PYTHON" bot.py
