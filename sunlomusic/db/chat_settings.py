# Copyright (C) @YO_UR_OFFICIAL_CRUSH

class ChatSettingsMixin:
    async def get_chat_settings(self, chat_id):
        settings = await self.db.chat_settings.find_one({"chat_id": chat_id})
        if not settings:
            settings = {
                "chat_id": chat_id,
                "mode": "audio",
                "quality": "720p",
                "audio_quality": "high",
                "audio_effect": "none",
                "playback_speed": 1.0,
                "autoplay": False,
                "autoplay_permission": "everyone",
                "title_update": False,
                "preferred_source": "youtube",
                "loop_mode": "off",
                "mention_requester": True,
                "vc_welcome": True
            }
            await self.db.chat_settings.insert_one(settings)
        return settings

    async def update_chat_settings(self, chat_id, updates):
        await self.db.chat_settings.update_one(
            {"chat_id": chat_id},
            {"$set": updates},
            upsert=True
        )
