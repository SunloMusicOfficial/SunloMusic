# Premium FFmpeg Filters Dictionary
FFMPEG_FILTERS = {
    "clear": "-af dynaudnorm=f=200",
    "bassboost": "-af bass=g=20,dynaudnorm=f=200",
    "nightcore": "-af asetrate=48000*1.25,aresample=48000,atempo=1.25",
    "8d": "-af apulsator=hz=0.125",
    "speedup": "-af atempo=1.5",
    "slowed": "-af atempo=0.8",
    "karaoke": "-af pan=stereo|c0=c0-c1|c1=c0-c1" # Vocal isolation (Center channel cancellation)
}

ACTIVE_FILTERS = {}

def get_filter(chat_id: int) -> str:
    return ACTIVE_FILTERS.get(chat_id, FFMPEG_FILTERS["clear"])

def set_filter(chat_id: int, filter_name: str) -> str:
    ACTIVE_FILTERS[chat_id] = FFMPEG_FILTERS.get(filter_name, FFMPEG_FILTERS["clear"])
    return ACTIVE_FILTERS[chat_id]
