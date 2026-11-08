# Copyright (C) @itsSmartDev

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, DisabledButton
from pyrogram.enums import ButtonStyle

class Keyboards:
    @staticmethod
    def _format_time(seconds: int) -> str:
        if seconds < 0:
            seconds = 0
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    @staticmethod
    def _create_progress_bar(current: int, total: int, length: int = 12) -> str:
        if total == 0 or total < 0:
            return "─" * length
        if current > total:
            current = total
        filled = int((current / total) * length)
        filled = max(0, min(filled, length))
        if filled == 0:
            bar = "▸" + "─" * (length - 1)
        elif filled == length:
            bar = "─" * (length - 1) + "●"
        else:
            bar = "─" * (filled - 1) + "●" + "─" * (length - filled)
        return bar

    @staticmethod
    def player_controls(chat_id: int, is_paused: bool = False, current_time: int = 0, total_time: int = 0, is_live: bool = False, loop_mode: str = 'off', queue_length: int = None, autoplay: bool = False):
        buttons = []
        off = DisabledButton()
        can_rewind = not is_live and current_time > 0
        can_seek = not is_live
        can_replay = not is_live and current_time > 0
        can_shuffle = queue_length is None or queue_length >= 3
        can_skip = queue_length is None or queue_length > 1 or loop_mode != 'off' or autoplay

        if is_live:
            progress_text = "🔴 LIVE"
        elif total_time > 0:
            current_formatted = Keyboards._format_time(current_time)
            total_formatted = Keyboards._format_time(total_time)
            progress_bar = Keyboards._create_progress_bar(current_time, total_time)
            progress_text = f"{current_formatted} ▷ {progress_bar} {total_formatted}"
        else:
            progress_text = "0:00 ▸ ────────────── 0:00"

        buttons.append([
            InlineKeyboardButton(progress_text, callback_data=f"progress_{chat_id}")
        ])

        buttons.append([
            InlineKeyboardButton(
                "Rewind",
                callback_data=f"rewind_{chat_id}",
                icon_custom_emoji_id=6109582886841622728,
                style=ButtonStyle.PRIMARY,
                disabled=None if can_rewind else off
            ),
            InlineKeyboardButton(
                "Resume" if is_paused else "Pause",
                callback_data=f"resume_{chat_id}" if is_paused else f"pause_{chat_id}",
                icon_custom_emoji_id=6114017462049577960 if is_paused else 6111404923637733475,
                style=ButtonStyle.DANGER if is_paused else ButtonStyle.SUCCESS
            ),
            InlineKeyboardButton(
                "Seek",
                callback_data=f"seek_{chat_id}",
                icon_custom_emoji_id=6111648078916229446,
                style=ButtonStyle.PRIMARY,
                disabled=None if can_seek else off
            ),
        ])

        buttons.append([
            InlineKeyboardButton(
                "Shuffle",
                callback_data=f"shuffle_{chat_id}",
                icon_custom_emoji_id=6111735305407045958,
                style=ButtonStyle.PRIMARY,
                disabled=None if can_shuffle else off
            ),
            InlineKeyboardButton(
                "Skip",
                callback_data=f"skip_{chat_id}",
                icon_custom_emoji_id=6111707078881975618,
                style=ButtonStyle.PRIMARY,
                disabled=None if can_skip else off
            ),
            InlineKeyboardButton(
                "Replay",
                callback_data=f"replay_{chat_id}",
                icon_custom_emoji_id=6111871004898762419,
                style=ButtonStyle.PRIMARY,
                disabled=None if can_replay else off
            ),
        ])

        repeat_text = "Repeat" if loop_mode == 'off' else "Repeat ✓"

        buttons.append([
            InlineKeyboardButton(
                "Sound",
                callback_data=f"volume_{chat_id}",
                icon_custom_emoji_id=6111869312681647237,
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                "Download",
                callback_data=f"download_{chat_id}",
                icon_custom_emoji_id=5258336354642697821,
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                repeat_text,
                callback_data=f"toggle_repeat_{chat_id}",
                icon_custom_emoji_id=6111715363873889673,
                style=ButtonStyle.PRIMARY
            ),
        ])

        buttons.append([
            InlineKeyboardButton(
                "Close",
                callback_data=f"close_{chat_id}",
                icon_custom_emoji_id=6111874900434099692,
                style=ButtonStyle.DANGER
            ),
        ])

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def effects_menu(chat_id: int, current: str = "none", speed: float = 1.0):
        from SunloMusic.services.effects import AUDIO_EFFECTS, EFFECT_LABELS

        current = (current or "none").lower()
        order = ["none", "bassboost", "nightcore", "slowed", "lofi", "8d"]

        buttons = []
        row = []
        for name in order:
            if name not in AUDIO_EFFECTS:
                continue
            label = EFFECT_LABELS.get(name, name.capitalize())
            if name == current:
                label = f"✓ {label}"
            row.append(InlineKeyboardButton(label, callback_data=f"seteffect_{name}_{chat_id}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        try:
            speed_val = float(speed)
        except (TypeError, ValueError):
            speed_val = 1.0
        buttons.append([
            InlineKeyboardButton(f"🚀 Speed: {speed_val:g}x", callback_data=f"speedmenu_{chat_id}")
        ])

        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data=f"volume_{chat_id}")
        ])

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def speed_menu(chat_id: int, speed: float = 1.0):
        from SunloMusic.services.effects import SPEED_PRESETS

        try:
            current = round(float(speed), 2)
        except (TypeError, ValueError):
            current = 1.0

        buttons = []
        row = []
        for value in SPEED_PRESETS:
            label = f"{value:g}x"
            if abs(value - current) < 1e-3:
                label = f"✓ {label}"
            row.append(InlineKeyboardButton(label, callback_data=f"setspeed_{value:g}_{chat_id}"))
            if len(row) == 3:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data=f"effects_{chat_id}")
        ])

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def autoplay_prompt(chat_id: int):
        buttons = [
            [
                InlineKeyboardButton(
                    "Play Related Songs",
                    callback_data=f"autoplay_yes_{chat_id}",
                    icon_custom_emoji_id=5334665104677941170,
                    style=ButtonStyle.SUCCESS
                ),
                InlineKeyboardButton(
                    "No Thanks",
                    callback_data=f"autoplay_no_{chat_id}",
                    icon_custom_emoji_id=6111874900434099692,
                    style=ButtonStyle.DANGER
                ),
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def settings_menu(chat_id: int, settings: dict):
        mode = settings.get('mode', 'audio')
        title_update = settings.get('title_update', False)
        admin_only = settings.get('admin_only', False)
        shuffle_mode = settings.get('shuffle_mode', False)
        mention_requester = settings.get('mention_requester', True)
        playlist_permission = settings.get('playlist_permission', 'everyone')
        autoplay = settings.get('autoplay', False)
        autoplay_permission = settings.get('autoplay_permission', 'everyone')
        vc_welcome = settings.get('vc_welcome', True)

        audio_quality = settings.get('audio_quality', 'high')

        mode_icon = "📹 Video" if mode == "video" else "📻 Audio"
        playlist_perm_icon = "👑 Admin Only" if playlist_permission == 'admin' else "🌐 Everyone"
        autoplay_perm_icon = "👑 Admin Only" if autoplay_permission == 'admin' else "🌐 Everyone"
        audio_quality_icon = f"🎚 {audio_quality.capitalize()}"

        def toggle(label: str, key: str, enabled: bool, off_text: str = "🚫 Disabled"):
            # green = on, red = off; the label next to it stays neutral
            return [
                InlineKeyboardButton(label, callback_data=f"toggle_{key}_{chat_id}"),
                InlineKeyboardButton(
                    "✅ Enabled" if enabled else off_text,
                    callback_data=f"toggle_{key}_{chat_id}",
                    style=ButtonStyle.SUCCESS if enabled else ButtonStyle.DANGER,
                ),
            ]

        def choice(label: str, value: str, callback: str):
            # blue = pick one of several values
            return [
                InlineKeyboardButton(label, callback_data="noop", disabled=DisabledButton()),
                InlineKeyboardButton(value, callback_data=callback, style=ButtonStyle.PRIMARY),
            ]

        buttons = [
            choice("🎮 Player Mode", mode_icon, f"toggle_mode_{chat_id}"),
            [
                InlineKeyboardButton("🎵 Audio Quality", callback_data=f"audioquality_{chat_id}"),
                InlineKeyboardButton(audio_quality_icon, callback_data=f"audioquality_{chat_id}", style=ButtonStyle.PRIMARY),
            ],
            toggle("👑 Admin Only", "admin", admin_only, off_text="🔒 Disabled"),
            toggle("✏️ Edit Title", "title", title_update),
            toggle("🔀 Shuffle Mode", "shuffle", shuffle_mode),
            toggle("🔔 Mention Requester", "mention", mention_requester),
            choice("📋 Playlist Loading", playlist_perm_icon, f"toggle_playlist_perm_{chat_id}"),
            toggle("🎧 Autoplay", "autoplay", autoplay),
            choice("🙋 Autoplay Permission", autoplay_perm_icon, f"toggle_autoplay_perm_{chat_id}"),
            toggle("👋 VC Welcome", "vc_welcome", vc_welcome),
            [
                InlineKeyboardButton(
                    "Close",
                    callback_data=f"close_{chat_id}",
                    icon_custom_emoji_id=6111874900434099692,
                    style=ButtonStyle.DANGER,
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def quality_menu(chat_id: int):
        def option(text: str, value: str):
            return [InlineKeyboardButton(text, callback_data=f"setquality_{value}_{chat_id}", style=ButtonStyle.PRIMARY)]

        buttons = [
            option("1080p", "1080p"),
            option("720p", "720p"),
            option("480p", "480p"),
            option("360p", "360p"),
            [InlineKeyboardButton("◀️ Back", callback_data=f"settings_{chat_id}")]
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def audio_quality_menu(chat_id: int, current: str = "high"):
        def option(value, text):
            selected = current == value
            return [InlineKeyboardButton(
                f"{'✅' if selected else '⬜'} {text}",
                callback_data=f"setaudioquality_{value}_{chat_id}",
                style=ButtonStyle.SUCCESS if selected else ButtonStyle.PRIMARY,
            )]
        buttons = [
            option("studio", "Studio (96kHz, stereo)"),
            option("high", "High (48kHz, stereo)"),
            option("medium", "Medium (36kHz, mono)"),
            option("low", "Low (24kHz, mono)"),
            [InlineKeyboardButton("◀️ Back", callback_data=f"settings_{chat_id}")]
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def loop_menu(chat_id: int, current_mode: str):
        buttons = [
            [InlineKeyboardButton(
                f"{'✅' if current_mode == 'off' else '⬜'} Off",
                callback_data=f"setloop_off_{chat_id}"
            )],
            [InlineKeyboardButton(
                f"{'✅' if current_mode == 'track' else '⬜'} Loop Track",
                callback_data=f"setloop_track_{chat_id}"
            )],
            [InlineKeyboardButton(
                f"{'✅' if current_mode == 'queue' else '⬜'} Loop Queue",
                callback_data=f"setloop_queue_{chat_id}"
            )],
            [InlineKeyboardButton("◀️ Back", callback_data=f"back_{chat_id}")]
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def queue_navigation(chat_id: int, page: int, total_pages: int):
        buttons = []

        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("◀️", callback_data=f"qpage_{page-1}_{chat_id}"))
        nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop", disabled=DisabledButton()))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("▶️", callback_data=f"qpage_{page+1}_{chat_id}"))

        if nav_row:
            buttons.append(nav_row)

        buttons.append([
            InlineKeyboardButton("🗑️ Clear Queue", callback_data=f"clearqueue_{chat_id}"),
            InlineKeyboardButton("◀️ Back", callback_data=f"back_{chat_id}")
        ])

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def playlist_menu(chat_id: int, playlists: list):
        buttons = []

        for playlist in playlists[:10]:
            name = playlist.get('name', 'Unknown')
            buttons.append([
                InlineKeyboardButton(f"📀 {name}", callback_data=f"loadpl_{name}_{chat_id}"),
                InlineKeyboardButton("🗑️", callback_data=f"delpl_{name}_{chat_id}")
            ])

        buttons.append([InlineKeyboardButton("◀️ Back", callback_data=f"back_{chat_id}")])

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def volume_menu(chat_id: int, current_volume: int = 100, is_muted: bool = False):
        mute_button = InlineKeyboardButton(
            "🔊 Unmute" if is_muted else "🔇 Mute",
            callback_data=f"unmute_btn_{chat_id}" if is_muted else f"mute_btn_{chat_id}"
        )

        buttons = [
            [
                mute_button,
                InlineKeyboardButton("🔉 25%", callback_data=f"vol_25_{chat_id}"),
                InlineKeyboardButton("🔉 50%", callback_data=f"vol_50_{chat_id}"),
            ],
            [
                InlineKeyboardButton("🔊 75%", callback_data=f"vol_75_{chat_id}"),
                InlineKeyboardButton("🔊 100%", callback_data=f"vol_100_{chat_id}"),
                InlineKeyboardButton("🔊 200%", callback_data=f"vol_200_{chat_id}"),
            ],
            [
                InlineKeyboardButton(
                    "Effects",
                    callback_data=f"effects_{chat_id}",
                    icon_custom_emoji_id=5890925363067886150,
                    style=ButtonStyle.PRIMARY,
                )
            ],
            [InlineKeyboardButton("◀️ Back", callback_data=f"back_{chat_id}")]
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def start_menu(bot_username: str):
        buttons = [
            [
                InlineKeyboardButton(
                    "Add me to a Group",
                    url=f"https://t.me/{bot_username}?startgroup=start",
                    style=ButtonStyle.PRIMARY,
                )
            ],
            [
                InlineKeyboardButton("Help", callback_data="help_menu", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("Support", url="https://t.me/itsSmartDev/2008", style=ButtonStyle.DANGER),
            ],
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def help_back_button():
        buttons = [[InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def help_menu(active: str = None):
        def tab(label: str, key: str):
            return InlineKeyboardButton(
                label,
                callback_data=f"help_{key}",
                style=ButtonStyle.SUCCESS if active == key else ButtonStyle.PRIMARY,
            )

        return InlineKeyboardMarkup([
            [tab("Basic", "basic"), tab("Music", "music"), tab("Settings", "settings")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_start")],
        ])

    @staticmethod
    def logs_menu() -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton("Log Display", callback_data="log_display", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("Clear logs", callback_data="log_clear", style=ButtonStyle.DANGER),
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def close_only(chat_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "Close",
                callback_data=f"close_{chat_id}",
                icon_custom_emoji_id=6111874900434099692,
                style=ButtonStyle.DANGER,
            ),
        ]])

    @staticmethod
    def logs_close() -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton("Close", callback_data="log_close", style=ButtonStyle.DANGER),
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def ranking_menu(chat_id: int, current_view: str = "daily"):
        def active(view: str) -> bool:
            return current_view == view

        buttons = [
            [
                InlineKeyboardButton(
                    "Daily",
                    callback_data=f"rank_daily_{chat_id}",
                    icon_custom_emoji_id=5951855749108863891,
                    style=ButtonStyle.SUCCESS if active("daily") else ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    "Weekly",
                    callback_data=f"rank_weekly_{chat_id}",
                    icon_custom_emoji_id=5951855749108863891,
                    style=ButtonStyle.SUCCESS if active("weekly") else ButtonStyle.PRIMARY,
                ),
            ],
            [
                InlineKeyboardButton(
                    "Global",
                    callback_data=f"rank_global_{chat_id}",
                    icon_custom_emoji_id=5287292843763713628,
                    style=ButtonStyle.SUCCESS if active("global") else ButtonStyle.PRIMARY,
                ),
            ],
            [
                InlineKeyboardButton(
                    "Close",
                    callback_data=f"close_{chat_id}",
                    icon_custom_emoji_id=5465665476971471368,
                    style=ButtonStyle.DANGER,
                ),
            ],
        ]
        return InlineKeyboardMarkup(buttons)

keyboards = Keyboards()
