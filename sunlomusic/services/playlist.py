# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from typing import List, Dict, Optional
from sunlomusic.db import db
from sunlomusic.core.logging import logger

class PlaylistManager:
    async def save_playlist(self, chat_id: int, name: str, tracks: List[Dict]) -> bool:
        try:
            await db.save_playlist(chat_id, name, tracks)
            logger.info(f"Saved playlist '{name}' in {chat_id} with {len(tracks)} tracks")
            return True
        except Exception as e:
            logger.error(f"Failed to save playlist '{name}' in {chat_id}: {e}")
            return False

    async def load_playlist(self, chat_id: int, name: str) -> Optional[Dict]:
        try:
            playlist = await db.get_playlist(chat_id, name)
            if playlist:
                logger.info(f"Loaded playlist '{name}' from {chat_id}")
            return playlist
        except Exception as e:
            logger.error(f"Failed to load playlist '{name}' from {chat_id}: {e}")
            return None

    async def list_playlists(self, chat_id: int) -> List[Dict]:
        try:
            playlists = await db.list_playlists(chat_id)
            return playlists
        except Exception as e:
            logger.error(f"Failed to list playlists for {chat_id}: {e}")
            return []

    async def delete_playlist(self, chat_id: int, name: str) -> bool:
        try:
            await db.delete_playlist(chat_id, name)
            logger.info(f"Deleted playlist '{name}' from {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete playlist '{name}' from {chat_id}: {e}")
            return False

    async def get_playlist_tracks(self, chat_id: int, name: str) -> List[Dict]:
        playlist = await self.load_playlist(chat_id, name)
        return playlist.get('tracks', []) if playlist else []

playlist_manager = PlaylistManager()
