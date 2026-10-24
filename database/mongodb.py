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

    async def get_user(self, user_id: int):
        if not self.client: return {"user_id": user_id, "coins": 0, "playlist": [], "play_count": 0}
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            user = {"user_id": user_id, "coins": 100, "playlist": [], "play_count": 0}
            await self.users.insert_one(user)
        return user

    async def add_coins(self, user_id: int, amount: int):
        if not self.client: return False
        user = await self.get_user(user_id)
        new_balance = user.get("coins", 0) + amount
        await self.users.update_one({"user_id": user_id}, {"$set": {"coins": new_balance}})
        return new_balance

    # --- New: Playlist & Stats ---
    async def save_to_playlist(self, user_id: int, track_data: dict):
        if not self.client: return False
        user = await self.get_user(user_id)
        playlist = user.get("playlist", [])
        
        # Limit playlist to 50 songs per user
        if len(playlist) >= 50:
            return "limit_reached"
            
        # Avoid duplicates
        for song in playlist:
            if song["title"] == track_data["title"]:
                return "duplicate"
                
        playlist.append({"title": track_data["title"], "url": track_data.get("original_url", track_data["title"])})
        await self.users.update_one({"user_id": user_id}, {"$set": {"playlist": playlist}})
        return "success"
        
    async def inc_play_count(self, user_id: int):
        if not self.client: return
        user = await self.get_user(user_id)
        current = user.get("play_count", 0)
        await self.users.update_one({"user_id": user_id}, {"$set": {"play_count": current + 1}})

    async def get_top_users(self):
        if not self.client: return []
        cursor = self.users.find().sort("play_count", -1).limit(10)
        return await cursor.to_list(length=10)

db = MongoDB()

    # --- Blacklist & Maintenance ---
    async def is_maintenance(self):
        if not self.client: return False
        config = await self.db.config.find_one({"_id": "maintenance"})
        return config["status"] if config else False

    async def set_maintenance(self, status: bool):
        if not self.client: return
        await self.db.config.update_one({"_id": "maintenance"}, {"$set": {"status": status}}, upsert=True)

    async def is_blacklisted(self, user_id: int):
        if not self.client: return False
        user = await self.users.find_one({"user_id": user_id})
        return user.get("blacklisted", False) if user else False

    async def blacklist_user(self, user_id: int, status: bool):
        if not self.client: return
        await self.users.update_one({"user_id": user_id}, {"$set": {"blacklisted": status}}, upsert=True)
