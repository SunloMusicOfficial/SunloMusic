# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUNLOMUSIC_API_KEY = os.getenv("SUNLOMUSIC_API_KEY", "")
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    SESSION_STRING = os.getenv("SESSION_STRING", "")
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/vcbot")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BOT_OWNER_ID = 6024212623
    LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "0"))
    CACHE_CHAT_ID = int(os.getenv("CACHE_CHAT_ID", "0"))

    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "100"))
    MAX_CONCURRENT_CHATS = int(os.getenv("MAX_CONCURRENT_CHATS", "50"))
    MAX_PLAYLIST_TRACKS = int(os.getenv("MAX_PLAYLIST_TRACKS", "50"))
    MAX_TRACK_DURATION = int(os.getenv("MAX_TRACK_DURATION", "7200"))

    CACHE_DIR = "cache"
    DOWNLOADS_DIR = "downloads"
    LOGS_DIR = "logs"

    PREFETCH_ENABLED = os.getenv("PREFETCH_ENABLED", "true").lower() in ("1", "true", "yes", "on")

    AUTOPLAY_BATCH_SIZE = int(os.getenv("AUTOPLAY_BATCH_SIZE", "5"))
    AUTOPLAY_PROMPT_TIMEOUT = int(os.getenv("AUTOPLAY_PROMPT_TIMEOUT", "90"))

    DEFAULT_QUALITY = "720p"
    DEFAULT_AUDIO_BITRATE = "128k"
    DEFAULT_VIDEO_BITRATE = "1000k"

    TITLE_UPDATE_TEMPLATE = "🎵 Playing: {title}"

    @classmethod
    def validate(cls):
        if not cls.API_ID or cls.API_ID == 0:
            raise ValueError("API_ID is not set")
        if not cls.API_HASH:
            raise ValueError("API_HASH is not set")
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is not set")
        if not cls.SESSION_STRING:
            raise ValueError("SESSION_STRING is not set - User client is required for voice chat")
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI is not set")

        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        os.makedirs(cls.DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
