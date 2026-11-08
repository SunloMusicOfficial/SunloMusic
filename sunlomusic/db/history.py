# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from sunlomusic.core.logging import logger


class HistoryMixin:
    async def increment_songs_played(self):
        await self.db.stats.update_one(
            {"_id": "global"},
            {"$inc": {"total_songs_played": 1}},
            upsert=True
        )

    async def get_total_songs_played(self):
        stats = await self.db.stats.find_one({"_id": "global"})
        if stats:
            return stats.get("total_songs_played", 0)
        return 0

    async def track_song_play(self, chat_id, user_id, user_name, song_title, duration=0, thumbnail=""):
        from datetime import datetime

        play_data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "user_name": user_name,
            "song_title": song_title,
            "duration": duration,
            "thumbnail": thumbnail or "",
            "played_at": datetime.utcnow()
        }

        await self.db.play_history.insert_one(play_data)
        logger.info(f"Tracked play: {user_name} played {song_title} in chat {chat_id}")

    async def get_group_stats(self, chat_id, period="daily"):
        from datetime import datetime, timedelta

        if period == "daily":
            time_threshold = datetime.utcnow() - timedelta(days=1)
        else:
            time_threshold = datetime.utcnow() - timedelta(days=7)

        top_users_pipeline = [
            {"$match": {"chat_id": chat_id, "played_at": {"$gte": time_threshold}}},
            {"$group": {
                "_id": {"user_id": "$user_id", "user_name": "$user_name"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]

        top_songs_pipeline = [
            {"$match": {"chat_id": chat_id, "played_at": {"$gte": time_threshold}}},
            {"$group": {
                "_id": "$song_title",
                "count": {"$sum": 1},
                "thumb": {"$max": "$thumbnail"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]

        total_stats_pipeline = [
            {"$match": {"chat_id": chat_id, "played_at": {"$gte": time_threshold}}},
            {"$group": {
                "_id": None,
                "total_songs": {"$sum": 1},
                "total_duration": {"$sum": "$duration"},
                "unique_users": {"$addToSet": "$user_id"}
            }}
        ]

        top_users = await self.db.play_history.aggregate(top_users_pipeline).to_list(5)
        top_songs = await self.db.play_history.aggregate(top_songs_pipeline).to_list(5)
        total_stats = await self.db.play_history.aggregate(total_stats_pipeline).to_list(1)

        return {
            "top_users": top_users,
            "top_songs": top_songs,
            "total_stats": total_stats[0] if total_stats else None
        }

    async def get_global_stats(self):
        from datetime import datetime, timedelta

        top_groups_pipeline = [
            {"$group": {
                "_id": "$chat_id",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]

        top_users_pipeline = [
            {"$group": {
                "_id": {"user_id": "$user_id", "user_name": "$user_name"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]

        top_songs_pipeline = [
            {"$group": {
                "_id": "$song_title",
                "count": {"$sum": 1},
                "thumb": {"$max": "$thumbnail"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]

        total_stats_pipeline = [
            {"$group": {
                "_id": None,
                "total_songs": {"$sum": 1},
                "total_duration": {"$sum": "$duration"},
                "unique_groups": {"$addToSet": "$chat_id"}
            }}
        ]

        top_groups = await self.db.play_history.aggregate(top_groups_pipeline).to_list(5)
        top_users = await self.db.play_history.aggregate(top_users_pipeline).to_list(5)
        top_songs = await self.db.play_history.aggregate(top_songs_pipeline).to_list(5)
        total_stats = await self.db.play_history.aggregate(total_stats_pipeline).to_list(1)

        for group in top_groups:
            chat_info = await self.db.broadcast_groups.find_one({"chat_id": group["_id"]})
            group["chat_title"] = chat_info.get("chat_title", "Unknown Group") if chat_info else "Unknown Group"

        return {
            "top_groups": top_groups,
            "top_users": top_users,
            "top_songs": top_songs,
            "total_stats": total_stats[0] if total_stats else None
        }
