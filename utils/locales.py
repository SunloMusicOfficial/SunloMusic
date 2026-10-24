LANG_DICT = {
    "en": {"playing": "▶️ Now Playing", "paused": "⏸ Paused"},
    "hi": {"playing": "▶️ Ab Baj Raha Hai", "paused": "⏸ Ruk Gaya"}
}

def get_string(lang: str, key: str) -> str:
    return LANG_DICT.get(lang, LANG_DICT["en"]).get(key, key)
