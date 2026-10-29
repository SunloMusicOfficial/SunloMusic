import time
import asyncio
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Track:
    title: str
    url: str
    duration: int
    thumbnail: str
    requester: str
    requester_id: int
    video: bool = False
    message_id: int = 0

@dataclass
class ChatQueue:
    chat_id: int
    now_playing: Optional[Track] = None
    queue: list[Track] = field(default_factory=list)
    loop: int = 0
    paused: bool = False
    start_time: float = 0.0
    paused_at: float = 0.0
    total_paused: float = 0.0
    playing_message_id: int = 0
    timer_task: Optional[asyncio.Task] = None
    votes: set = field(default_factory=set)

_queues: dict[int, ChatQueue] = {}

# ✅ Global set for Karaoke
KARAOKE_CHATS = set()

def get_queue(chat_id: int) -> ChatQueue:
    if chat_id not in _queues: _queues[chat_id] = ChatQueue(chat_id=chat_id)
    return _queues[chat_id]

def clear_queue(chat_id: int):
    _queues.pop(chat_id, None)

def active_chats() -> list[int]:
    return list(_queues.keys())
