# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from .connection import MongoDB
from .chat_settings import ChatSettingsMixin
from .queues import QueuesMixin
from .playlists import PlaylistsMixin
from .vc_admins import VCAdminsMixin
from .broadcast import BroadcastMixin
from .history import HistoryMixin
from .audio_cache import AudioCacheMixin


class Database(
    MongoDB,
    ChatSettingsMixin,
    QueuesMixin,
    PlaylistsMixin,
    VCAdminsMixin,
    BroadcastMixin,
    HistoryMixin,
    AudioCacheMixin,
):
    pass


db = Database()
