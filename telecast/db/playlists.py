# Copyright (C) @itsSmartDev

class PlaylistsMixin:
    async def save_playlist(self, chat_id, name, tracks):
        from datetime import datetime
        await self.db.playlists.update_one(
            {"chat_id": chat_id, "name": name},
            {"$set": {
                "tracks": tracks,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )

    async def get_playlist(self, chat_id, name):
        return await self.db.playlists.find_one({"chat_id": chat_id, "name": name})

    async def list_playlists(self, chat_id):
        cursor = self.db.playlists.find({"chat_id": chat_id})
        return await cursor.to_list(length=100)

    async def delete_playlist(self, chat_id, name):
        await self.db.playlists.delete_one({"chat_id": chat_id, "name": name})
