# Copyright (C) @YO_UR_OFFICIAL_CRUSH

class QueuesMixin:
    async def get_queue(self, chat_id):
        queue = await self.db.queues.find_one({"chat_id": chat_id})
        if not queue:
            queue = {
                "chat_id": chat_id,
                "tracks": [],
                "current_index": 0
            }
            await self.db.queues.insert_one(queue)
        return queue

    async def update_queue(self, chat_id, tracks, current_index=0):
        await self.db.queues.update_one(
            {"chat_id": chat_id},
            {"$set": {"tracks": tracks, "current_index": current_index}},
            upsert=True
        )

    async def clear_queue(self, chat_id):
        await self.db.queues.update_one(
            {"chat_id": chat_id},
            {"$set": {"tracks": [], "current_index": 0}},
            upsert=True
        )
