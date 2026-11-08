# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from SunloMusic.core.config import Config
from SunloMusic.core.logging import logger
from datetime import datetime

class MonitorLogger:
    def __init__(self):
        self.client = None
        self.log_chat_id = Config.LOG_CHAT_ID

    def set_client(self, client):
        self.client = client

    async def log_group_added(self, chat_id: int, chat_title: str, member_count: int = None):
        if not self.client or not self.log_chat_id:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = (
                f"✅ New Group Added\n\n"
                f"Group: {chat_title}\n"
                f"Chat ID: {chat_id}\n"
            )
            if member_count:
                message += f"Members: {member_count}\n"
            message += f"Time: {timestamp}"

            await self.client.send_message(self.log_chat_id, message)
        except Exception as e:
            logger.error(f"Failed to send group added log: {e}")

    async def log_group_removed(self, chat_id: int, chat_title: str):
        if not self.client or not self.log_chat_id:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = (
                f"❌ Bot Removed from Group\n\n"
                f"Group: {chat_title}\n"
                f"Chat ID: {chat_id}\n"
                f"Time: {timestamp}"
            )

            await self.client.send_message(self.log_chat_id, message)
        except Exception as e:
            logger.error(f"Failed to send group removed log: {e}")

    async def log_song_played(self, chat_id: int, chat_title: str, song_title: str, requested_by: str, song_url: str = None):
        if not self.client or not self.log_chat_id:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = (
                f"🎵 Song Played\n\n"
                f"Song: {song_title}\n"
                f"Group: {chat_title}\n"
                f"Requested by: {requested_by}\n"
            )
            if song_url:
                message += f"URL: {song_url}\n"
            message += f"Time: {timestamp}"

            await self.client.send_message(self.log_chat_id, message, disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Failed to send song played log: {e}")

    async def log_error(self, error_type: str, chat_id: int, chat_title: str, error_message: str):
        if not self.client or not self.log_chat_id:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = (
                f"⚠️ Error Occurred\n\n"
                f"Type: {error_type}\n"
                f"Group: {chat_title}\n"
                f"Chat ID: {chat_id}\n"
                f"Error: {error_message}\n"
                f"Time: {timestamp}"
            )

            await self.client.send_message(self.log_chat_id, message)
        except Exception as e:
            logger.error(f"Failed to send error log: {e}")

monitor_logger = MonitorLogger()
