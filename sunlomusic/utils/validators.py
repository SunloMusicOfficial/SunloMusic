# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import re
from typing import Tuple, Optional

class Validators:
    @staticmethod
    def is_youtube_url(url: str) -> bool:
        youtube_regex = r'(https?://)?(www\.)?(music\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return bool(re.match(youtube_regex, url))

    @staticmethod
    def normalize_youtube_url(url: str) -> str:
        music_regex = r'https?://music\.youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
        match = re.match(music_regex, url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
        return url

    @staticmethod
    def is_url(text: str) -> bool:
        url_regex = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        return bool(re.match(url_regex, text))

    @staticmethod
    def detect_source(text: str) -> Tuple[str, str]:
        if Validators.is_youtube_url(text):
            return ('youtube', Validators.normalize_youtube_url(text))
        elif Validators.is_url(text):
            return ('url', text)
        else:
            return ('search', text)

validators = Validators()
