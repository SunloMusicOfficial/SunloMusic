# Copyright (C) @YO_UR_OFFICIAL_CRUSH

class AudioCacheMixin:
    """Maps a YouTube video id to the Telegram file_id of its already-uploaded audio."""

    async def get_audio_cache(self, video_id):
        return await self.db.audio_cache.find_one({"video_id": video_id})

    async def set_audio_cache(self, video_id, file_id, file_unique_id, title, duration, size):
        from datetime import datetime
        await self.db.audio_cache.update_one(
            {"video_id": video_id},
            {"$set": {
                "file_id": file_id,
                "file_unique_id": file_unique_id,
                "title": title,
                "duration": duration,
                "size": size,
                "cached_at": datetime.utcnow(),
            }},
            upsert=True
        )

    async def delete_audio_cache(self, video_id):
        await self.db.audio_cache.delete_one({"video_id": video_id})
