from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    API_ID: int
    API_HASH: str
    BOT_TOKEN: str
    SESSION_STRING: str
    MONGO_URL: str

    ONEGRAB_API_KEY: str = "" # ✅ OneGrab API Key
    ONEGRAB_API_URL: str = "https://api.onegrab.fun"

    OWNER_ID: int = 0
    LOGGER_ID: int = 0
    SUDO_USERS: str = ""

    BOT_NAME: str = "SunloMusic"
    BOT_USERNAME: str = "@SunloMusicBot"
    START_IMG: str = ""

    SUPPORT_CHAT: str = ""
    UPDATES_CHANNEL: str = ""

    DURATION_LIMIT: int = 3600
    QUEUE_LIMIT: int = 50

    @property
    def sudo_list(self) -> list[int]:
        try:
            return [int(x.strip()) for x in self.SUDO_USERS.split(",") if x.strip()]
        except Exception:
            return []

config = Config()
