from typing import Dict, List

# Har group ki queue track karne ke liye dictionary
QUEUE: Dict[int, List[dict]] = {}

def add_to_queue(chat_id: int, track_data: dict):
    if chat_id not in QUEUE:
        QUEUE[chat_id] = []
    QUEUE[chat_id].append(track_data)
    return len(QUEUE[chat_id])

def get_next_track(chat_id: int):
    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        return QUEUE[chat_id].pop(0)
    return None

def clear_queue(chat_id: int):
    if chat_id in QUEUE:
        QUEUE[chat_id].clear()
