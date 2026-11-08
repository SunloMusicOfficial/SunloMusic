# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from typing import List, Dict, Optional
import random
from SunloMusic.db import db
from SunloMusic.core.logging import logger

class QueueManager:
    def __init__(self):
        self.queues: Dict[int, List[Dict]] = {}
        self.playlist_states: Dict[int, Dict] = {}

    async def load_queue(self, chat_id: int):
        queue_data = await db.get_queue(chat_id)
        self.queues[chat_id] = queue_data.get('tracks', [])
        return queue_data

    async def add_track(self, chat_id: int, track: Dict):
        if chat_id not in self.queues:
            await self.load_queue(chat_id)

        self.queues[chat_id].append(track)
        await self._save_queue(chat_id)
        logger.info(f"Added track to queue in {chat_id}: {track.get('title')}")

    async def remove_track(self, chat_id: int, index: int) -> bool:
        if chat_id not in self.queues:
            await self.load_queue(chat_id)

        if 0 <= index < len(self.queues[chat_id]):
            removed = self.queues[chat_id].pop(index)
            await self._save_queue(chat_id)
            logger.info(f"Removed track from queue in {chat_id}: {removed.get('title')}")
            return True
        return False

    async def get_queue(self, chat_id: int) -> List[Dict]:
        if chat_id not in self.queues:
            await self.load_queue(chat_id)
        return self.queues[chat_id]

    async def get_current_track(self, chat_id: int) -> Optional[Dict]:
        queue = await self.get_queue(chat_id)
        return queue[0] if queue else None

    async def next_track(self, chat_id: int) -> Optional[Dict]:
        if chat_id not in self.queues:
            await self.load_queue(chat_id)

        if self.queues[chat_id]:
            self.queues[chat_id].pop(0)
            await self._save_queue(chat_id)

            if self.queues[chat_id]:
                return self.queues[chat_id][0]
        return None

    async def clear_queue(self, chat_id: int):
        self.queues[chat_id] = []
        await db.clear_queue(chat_id)
        logger.info(f"Cleared queue in {chat_id}")

    async def clear_upcoming_tracks(self, chat_id: int):
        if chat_id not in self.queues:
            await self.load_queue(chat_id)

        queue = self.queues[chat_id]
        self.clear_playlist_state(chat_id)

        if len(queue) > 1:
            self.queues[chat_id] = [queue[0]]
            await self._save_queue(chat_id)
            logger.info(f"Cleared upcoming tracks and playlist state in {chat_id}, kept current track")
            return True
        elif len(queue) == 1:
            logger.info(f"No upcoming tracks to clear in {chat_id}")
            return False
        else:
            logger.info(f"Queue is empty in {chat_id}")
            return False

    async def move_track(self, chat_id: int, from_index: int, to_index: int) -> bool:
        if chat_id not in self.queues:
            await self.load_queue(chat_id)

        queue = self.queues[chat_id]
        if 0 <= from_index < len(queue) and 0 <= to_index < len(queue):
            track = queue.pop(from_index)
            queue.insert(to_index, track)
            await self._save_queue(chat_id)
            logger.info(f"Moved track in {chat_id} from {from_index} to {to_index}")
            return True
        return False

    async def get_queue_length(self, chat_id: int) -> int:
        queue = await self.get_queue(chat_id)
        return len(queue)

    async def shuffle_queue(self, chat_id: int):
        if chat_id not in self.queues:
            await self.load_queue(chat_id)

        if len(self.queues[chat_id]) > 1:
            current = self.queues[chat_id][0]
            rest = self.queues[chat_id][1:]
            random.shuffle(rest)
            self.queues[chat_id] = [current] + rest
            await self._save_queue(chat_id)
            logger.info(f"Shuffled queue in {chat_id}")

    async def _save_queue(self, chat_id: int):
        await db.update_queue(chat_id, self.queues[chat_id])

    def set_playlist_state(self, chat_id: int, playlist_url: str, total: int, fetched: int, requested_by: str, requested_by_id: int):
        self.playlist_states[chat_id] = {
            'url': playlist_url,
            'total': total,
            'fetched': fetched,
            'requested_by': requested_by,
            'requested_by_id': requested_by_id,
        }

    def get_playlist_state(self, chat_id: int) -> Optional[Dict]:
        return self.playlist_states.get(chat_id)

    def update_playlist_fetched(self, chat_id: int, fetched: int):
        if chat_id in self.playlist_states:
            self.playlist_states[chat_id]['fetched'] = fetched

    def clear_playlist_state(self, chat_id: int):
        self.playlist_states.pop(chat_id, None)

queue_manager = QueueManager()
