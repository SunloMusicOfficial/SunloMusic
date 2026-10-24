import time
from pyrogram.types import Message

SPAM_CACHE = {}
SPAM_LIMIT = 3 # Max 3 messages per 5 seconds

async def is_spam(user_id: int) -> bool:
    current_time = time.time()
    if user_id not in SPAM_CACHE:
        SPAM_CACHE[user_id] = [current_time]
        return False
        
    # Remove old timestamps
    SPAM_CACHE[user_id] = [t for t in SPAM_CACHE[user_id] if current_time - t < 5]
    
    if len(SPAM_CACHE[user_id]) >= SPAM_LIMIT:
        return True
        
    SPAM_CACHE[user_id].append(current_time)
    return False
