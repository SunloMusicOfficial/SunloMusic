from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    # Core API & Database Credentials
    API_ID: int
    API_HASH: str
    BOT_TOKEN: str
    SESSION_STRING: str
    MONGO_URL: str

    # ✅ ShrutiBots API (Replaced OneGrab)
    SHRUTI_API_KEY: str = ""
    SHRUTI_API_URL: str = "https://api.shrutibots.in"
    
    # Groq AI API for Voice Commands
    GROQ_API_KEY: str = ""

    # Owner & Admin Settings
    OWNER_ID: int = 0
    LOGGER_ID: int = 0
    SUDO_USERS: str = ""

    # Bot Details & UI
    BOT_NAME: str = "SunloMusic"
    BOT_USERNAME: str = "@SunloMusicBot"
    START_IMG: str = ""

    # Support Links
    SUPPORT_CHAT: str = ""
    UPDATES_CHANNEL: str = ""

    # Limits
    DURATION_LIMIT: int = 3600
    QUEUE_LIMIT: int = 50

    @property
    def sudo_list(self) -> list[int]:
        try:
            return [int(x.strip()) for x in self.SUDO_USERS.split(",") if x.strip()]
        except Exception:
            return []

config = Config()
