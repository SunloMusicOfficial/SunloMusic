from motor.motor_asyncio import AsyncIOMotorClient
from config.vars import Config
from utils.logger import LOGGER

class MongoDB:
    def __init__(self):
        if Config.MONGO_URI:
            try:
                self.client = AsyncIOMotorClient(Config.MONGO_URI)
                self.db = self.client.SunloMusic
                self.groups = self.db.groups
                self.users = self.db.users
                LOGGER.info("✅ MongoDB connected successfully!")
            except Exception as e:
                LOGGER.error(f"MongoDB connection failed: {e}")
                self.client = None
        else:
            self.client = None
            LOGGER.warning("⚠️ MONGO_URI not found in .env! Database features disabled.")

    async def get_group(self, chat_id: int):
        if not self.client: return None
        group = await self.groups.find_one({"chat_id": chat_id})
        if not group:
            group = {"chat_id": chat_id, "lang": "en", "strict_mode": False}
            await self.groups.insert_one(group)
        return group

db = MongoDB()
