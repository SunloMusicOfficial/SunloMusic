import time
from typing import Dict, Any

# Memory Cache to store song search results (Expires in 2 hours)
SEARCH_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 7200 

def get_cache(query: str):
    if query in SEARCH_CACHE:
        data = SEARCH_CACHE[query]
        if time.time() - data["timestamp"] < CACHE_TTL:
            return data["result"]
        else:
            del SEARCH_CACHE[query]
    return None

def set_cache(query: str, result: dict):
    SEARCH_CACHE[query] = {
        "result": result,
        "timestamp": time.time()
    }
