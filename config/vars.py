import os
from dotenv import load_dotenv

# .env file load karein
load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    MONGO_URI = os.getenv("MONGO_URI", "")
    REDIS_URI = os.getenv("REDIS_URI", "")
    
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", 0))
    WEB_URL = os.getenv("WEB_URL", "")
    STREAM_API_URL = os.getenv("STREAM_API_URL", "https://api.onegrab.fun")
    STREAM_API_KEY = os.getenv("STREAM_API_KEY", "")
    
    # Premium features limits
    MAX_QUEUE_SIZE = 500
    AUTO_LEAVE_TIME = 120 # Seconds me
    BOT_NAME = "SunloMusic"
CUSTOM_FOOTER = "✨ Powered by SunloMusic"
