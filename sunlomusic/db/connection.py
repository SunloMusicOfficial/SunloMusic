# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from motor.motor_asyncio import AsyncIOMotorClient

from sunlomusic.core.config import Config
from sunlomusic.core.logging import logger


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(Config.MONGODB_URI)
            self.db = self.client.get_default_database()
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")

            await self._create_indexes()
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    async def _create_indexes(self):
        await self.db.chat_settings.create_index("chat_id", unique=True)
        await self.db.queues.create_index("chat_id", unique=True)
        await self.db.playlists.create_index([("chat_id", 1), ("name", 1)], unique=True)
        await self.db.vc_admins.create_index([("chat_id", 1), ("user_id", 1)], unique=True)
        await self.db.broadcast_users.create_index("user_id", unique=True)
        await self.db.broadcast_groups.create_index("chat_id", unique=True)
        await self.db.audio_cache.create_index("video_id", unique=True)
        logger.info("Database indexes created")

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
