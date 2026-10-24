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

    # --- Group Settings ---
    async def get_group(self, chat_id: int):
        if not self.client: return {"chat_id": chat_id, "strict_mode": False}
        group = await self.groups.find_one({"chat_id": chat_id})
        if not group:
            group = {"chat_id": chat_id, "lang": "en", "strict_mode": False}
            await self.groups.insert_one(group)
        return group

    async def toggle_strict_mode(self, chat_id: int):
        if not self.client: return False
        group = await self.get_group(chat_id)
        new_status = not group.get("strict_mode", False)
        await self.groups.update_one({"chat_id": chat_id}, {"$set": {"strict_mode": new_status}})
        return new_status

    # --- User Economy ---
    async def get_user(self, user_id: int):
        if not self.client: return {"user_id": user_id, "coins": 0}
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            user = {"user_id": user_id, "coins": 100} # Naye users ko 100 coins free
            await self.users.insert_one(user)
        return user

    async def add_coins(self, user_id: int, amount: int):
        if not self.client: return False
        user = await self.get_user(user_id)
        new_balance = user["coins"] + amount
        await self.users.update_one({"user_id": user_id}, {"$set": {"coins": new_balance}})
        return new_balance

db = MongoDB()
