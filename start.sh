#!/bin/bash
# Termux check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ ffmpeg not found. Installing..."
    pkg install ffmpeg -y
fi
python -m SunloMusic
