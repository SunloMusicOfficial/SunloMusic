# Copyright (C) @itsSmartDev

class VCAdminsMixin:
    async def add_vc_admin(self, chat_id, user_id, user_name):
        from datetime import datetime
        await self.db.vc_admins.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {
                "user_name": user_name,
                "added_at": datetime.utcnow()
            }},
            upsert=True
        )

    async def remove_vc_admin(self, chat_id, user_id):
        await self.db.vc_admins.delete_one({"chat_id": chat_id, "user_id": user_id})

    async def is_vc_admin(self, chat_id, user_id):
        admin = await self.db.vc_admins.find_one({"chat_id": chat_id, "user_id": user_id})
        return admin is not None

    async def get_vc_admins(self, chat_id):
        cursor = self.db.vc_admins.find({"chat_id": chat_id})
        return await cursor.to_list(length=100)
