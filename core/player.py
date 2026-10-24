from typing import Dict, List

QUEUE: Dict[int, List[dict]] = {}
CURRENT_TRACK: Dict[int, dict] = {}
AUTOPLAY: Dict[int, bool] = {} # Auto-play status tracker

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
    if chat_id in CURRENT_TRACK:
        del CURRENT_TRACK[chat_id]

def is_autoplay_enabled(chat_id: int) -> bool:
    # Default Auto-play True rakhna premium feel deta hai
    return AUTOPLAY.get(chat_id, True) 

def toggle_autoplay(chat_id: int) -> bool:
    current_status = is_autoplay_enabled(chat_id)
    AUTOPLAY[chat_id] = not current_status
    return AUTOPLAY[chat_id]
