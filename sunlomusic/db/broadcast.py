# Copyright (C) @YO_UR_OFFICIAL_CRUSH

class BroadcastMixin:
    async def save_broadcast_user(self, user_id, user_name, username=None):
        from datetime import datetime
        await self.db.broadcast_users.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_name": user_name,
                "username": username,
                "last_interaction": datetime.utcnow()
            }},
            upsert=True
        )

    async def save_broadcast_group(self, chat_id, chat_title):
        from datetime import datetime
        await self.db.broadcast_groups.update_one(
            {"chat_id": chat_id},
            {"$set": {
                "chat_title": chat_title,
                "joined_at": datetime.utcnow()
            }},
            upsert=True
        )

    async def get_all_broadcast_users(self):
        cursor = self.db.broadcast_users.find({})
        return await cursor.to_list(length=None)

    async def get_all_broadcast_groups(self):
        cursor = self.db.broadcast_groups.find({})
        return await cursor.to_list(length=None)
