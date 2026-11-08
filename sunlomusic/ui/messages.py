# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from typing import Dict, List

class Messages:
    @staticmethod
    def now_playing(track: Dict, requested_by: str = "Unknown", current_time: int = 0, queue: List[Dict] = None, playlist_unfetched: int = 0) -> str:
        title = track.get('title', 'Unknown')

        message = f"![🎵](tg://emoji?id=5334665104677941170) **Music Playlist:**\n\n"

        req_id = track.get('requested_by_id')
        if req_id:
            req_mention = f"[{requested_by}](tg://user?id={req_id})"
        else:
            req_mention = requested_by

        message += f"**1. ![🎸](tg://emoji?id=5222472119295684375) {title}**\n"
        message += f"![🏆](tg://emoji?id=5944970130554359187) **Requested by:** {req_mention}\n\n"

        if queue and len(queue) > 1:
            for i, next_track in enumerate(queue[1:4], start=2):
                next_title = next_track.get('title', 'Unknown')
                if len(next_title) > 50:
                    next_title = next_title[:47] + "..."
                next_name = next_track.get('requested_by', 'Unknown')
                next_id = next_track.get('requested_by_id')
                if next_id:
                    next_mention = f"[{next_name}](tg://user?id={next_id})"
                else:
                    next_mention = next_name
                message += f"**{i}. ![🎸](tg://emoji?id=5222472119295684375) {next_title}**\n"
                message += f"![🏆](tg://emoji?id=5944970130554359187) **Requested by:** {next_mention}\n\n"

            shown = min(len(queue), 4)
            remaining_in_queue = len(queue) - shown
            total_remaining = remaining_in_queue + playlist_unfetched
            if total_remaining > 0:
                message += f"**✨ {total_remaining} tracks still in the playlist.....**"

        return message

    @staticmethod
    def _create_progress_bar(current: int, total: int, length: int = 12) -> str:
        if total == 0:
            return "━" * length

        filled = int((current / total) * length)
        bar = "✦" * filled + "✧" * (length - filled)
        return bar

    @staticmethod
    def queue_list(queue: List[Dict], page: int = 0, page_size: int = 10) -> str:
        if not queue:
            return "📄 **Queue is empty**"

        start = page * page_size
        end = start + page_size
        page_queue = queue[start:end]

        message = f"📄 **Queue** ({len(queue)} tracks)\n\n"

        for i, track in enumerate(page_queue, start=start+1):
            title = track.get('title', 'Unknown')
            duration = Messages._format_duration(track.get('duration', 0))
            message += f"{i}. **{title}** `[{duration}]`\n"

        total_pages = (len(queue) + page_size - 1) // page_size
        message += f"\nPage {page+1}/{total_pages}"

        return message

    @staticmethod
    def settings_info(settings: Dict) -> str:
        message = "![⚙️](tg://emoji?id=5316832430529722441) **Configure Your VCPlayer Settings Here.**\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━"

        return message

    @staticmethod
    def settings_rich(custom_emoji: bool = True):
        """Rich-message version of settings_info()."""
        from pyrogram import types
        icon = types.RichTextCustomEmoji("5316832430529722441", "⚙️") if custom_emoji else "⚙️"
        return types.InputRichMessage(blocks=[
            types.InputRichBlockParagraph([icon, " ", types.RichTextBold("Configure Your VCPlayer Settings Here.")]),
            types.InputRichBlockDivider(),
        ])

    @staticmethod
    def autoplay_prompt(seed_title: str) -> str:
        return (
            f"![🎧](tg://emoji?id=5334665104677941170) **Playlist finished**\n\n"
            f"**Last played:** {seed_title}\n\n"
            f"Want me to keep the music going with related songs?"
        )

    @staticmethod
    def autoplay_prompt_rich(seed_title: str, custom_emoji: bool = True):
        """Rich "Playlist Finished" prompt asking whether to keep playing related songs."""
        from pyrogram import types

        icon = types.RichTextCustomEmoji("5316631095347788915", "🎵") if custom_emoji else "🎵"
        return types.InputRichMessage(blocks=[
            types.InputRichBlockSectionHeading([icon, " Playlist Finished"], size=1),
            types.InputRichBlockDivider(),
            types.InputRichBlockParagraph([types.RichTextBold("Last Played:"), f" {seed_title}"]),
            types.InputRichBlockDivider(),
            types.InputRichBlockBlockQuotation([
                types.InputRichBlockParagraph("Want me to keep the music going with related songs?")
            ]),
        ])

    @staticmethod
    def autoplay_searching() -> str:
        return (
            "![🔎](tg://emoji?id=5258396243666681152) **Looking for related songs…**\n\n"
            "This may take a few seconds."
        )

    @staticmethod
    def autoplay_queued(count: int, seed_title: str) -> str:
        return (
            f"![🎧](tg://emoji?id=5334665104677941170) **Autoplay on**\n\n"
            f"Queued **{count} related track(s)** based on **{seed_title}**."
        )

    @staticmethod
    def autoplay_queued_rich(count: int, seed_title: str, custom_emoji: bool = True):
        """Rich "Autoplay Status" message shown once related tracks are queued."""
        from pyrogram import types

        def emoji(emoji_id: str, alt: str):
            return types.RichTextCustomEmoji(emoji_id, alt) if custom_emoji else alt

        def stat(label, value):
            return types.InputRichBlockListItem(
                blocks=[types.InputRichBlockParagraph([types.RichTextBold(label), value])]
            )

        return types.InputRichMessage(blocks=[
            types.InputRichBlockSectionHeading([emoji("5222472119295684375", "🎶"), " Autoplay Status"], size=1),
            types.InputRichBlockDivider(),
            types.InputRichBlockParagraph([types.RichTextBold("Status:"), " On"]),
            types.InputRichBlockSectionHeading([emoji("5915480455603295660", "🎶"), " Queue Information"], size=3),
            types.InputRichBlockList([
                stat("Based On:", f" {seed_title}"),
                stat("Queued Tracks:", f" {count} related track(s)"),
            ]),
        ])

    @staticmethod
    def autoplay_unavailable() -> str:
        return (
            "❌ **No related songs found**\n\n"
            "Autoplay could not find anything to play next."
        )

    @staticmethod
    def autoplay_declined() -> str:
        return "⏹️ **Autoplay skipped** — playback stopped."

    @staticmethod
    def autoplay_expired() -> str:
        return "⌛️ **Autoplay request expired** — nobody answered, playback stopped."

    @staticmethod
    def vc_welcome(name: str = None) -> str:
        who = f", {name}" if name else ""
        return f"👋 Welcome{who}! Enjoy the music 🎶"

    @staticmethod
    def track_added(track: Dict, position: int) -> str:
        title = track.get('title', 'Unknown')
        return f"✅ Added to queue at position {position}\n**{title}**"

    @staticmethod
    def queue_updated(queue: List[Dict]) -> str:
        if not queue:
            return "📄 **Queue is empty**"

        message = f"![🎵](tg://emoji?id=5334665104677941170) **Music Playlist:**\n\n"

        for i, track in enumerate(queue[:5], start=1):
            track_title = track.get('title', 'Unknown')
            if len(track_title) > 60:
                track_title = track_title[:57] + "..."
            req_name = track.get('requested_by', 'Unknown')
            req_id = track.get('requested_by_id')
            if req_id:
                req_mention = f"[{req_name}](tg://user?id={req_id})"
            else:
                req_mention = req_name
            message += f"**{i}. ![🎸](tg://emoji?id=5222472119295684375) {track_title}**\n"
            message += f"![🏆](tg://emoji?id=5944970130554359187) **Requested by:** {req_mention}\n\n"

        if len(queue) > 5:
            remaining = len(queue) - 5
            message += f"**✨ {remaining} tracks still in the playlist.....**"

        return message

    @staticmethod
    def playlist_saved(name: str, count: int) -> str:
        return f"💾 Playlist **{name}** saved with {count} tracks"

    @staticmethod
    def playlist_loaded(name: str, count: int) -> str:
        return f"📀 Loaded playlist **{name}** with {count} tracks"

    @staticmethod
    def error(message: str) -> str:
        return f"❌ **Error:** {message}"

    @staticmethod
    def success(message: str) -> str:
        return f"✅ {message}"

    @staticmethod
    def _format_duration(seconds: int) -> str:
        if seconds == 0:
            return "Live"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    @staticmethod
    def start_welcome() -> str:
        return (
            "![🎧](tg://emoji?id=5334665104677941170) **Welcome to SunloMusic!**\n"
            "Your all-in-one voice chat player for music and video\n\n"
            "![🎵](tg://emoji?id=5334665104677941170) Play music & videos\n"
            "⚡️ Smooth streaming\n"
            "📌 Multi-chat support\n"
            "🏚 Full controls (pause, skip, seek, shuffle, replay)\n"
            "💿 Audio & video modes\n\n"
            "![🚀](tg://emoji?id=5429440296867886716) Choose an option below to get started!"
        )

    @staticmethod
    def start_welcome_rich(custom_emoji: bool = True):
        """Rich-message version of start_welcome(). Falls back to plain emoji when custom emoji aren't wanted."""
        from pyrogram import types

        def emoji(emoji_id: str, alt: str):
            return types.RichTextCustomEmoji(emoji_id, alt) if custom_emoji else alt

        def feature(*parts):
            return types.InputRichBlockListItem(blocks=[types.InputRichBlockParagraph(list(parts))])

        bold = types.RichTextBold
        return types.InputRichMessage(blocks=[
            types.InputRichBlockSectionHeading([emoji("5316631095347788915", "🎵"), " Welcome to SunloMusic!"], size=1),
            types.InputRichBlockDivider(),
            types.InputRichBlockParagraph(bold("Your all-in-one voice chat player for music and video")),
            types.InputRichBlockSectionHeading([emoji("5316742794562254812", "✨"), " Key Features"], size=2),
            types.InputRichBlockList([
                feature(bold("Play Music & Videos")),
                feature(bold("Smooth Streaming")),
                feature(bold("Multi-Chat Support")),
                feature(bold("Full Controls"), " (pause, skip, seek, shuffle, replay)"),
                feature(bold("Audio & Video Modes")),
            ]),
            types.InputRichBlockDivider(),
            types.InputRichBlockParagraph([emoji("5316571734604790521", "🚀"), " ", bold("Choose an option below to get started!")]),
        ])

    @staticmethod
    def playlist_ready_rich(loaded: int, total: int, cap_note: str, first_track: str, custom_emoji: bool = True):
        """Rich "Playlist Ready" message shown after a playlist is loaded."""
        from pyrogram import types

        def emoji(emoji_id: str, alt: str):
            return types.RichTextCustomEmoji(emoji_id, alt) if custom_emoji else alt

        def stat(label, value):
            return types.InputRichBlockListItem(
                blocks=[types.InputRichBlockParagraph([types.RichTextBold(label), value])]
            )

        return types.InputRichMessage(blocks=[
            types.InputRichBlockSectionHeading([emoji("5316631095347788915", "🎵"), " Playlist Ready"], size=1),
            types.InputRichBlockDivider(),
            types.InputRichBlockSectionHeading("Status Update", size=2),
            types.InputRichBlockList([
                stat("Added to Queue:", f" {loaded} tracks"),
                stat("Playlist Contains:", f" {total} tracks{cap_note}"),
            ]),
            types.InputRichBlockDivider(),
            types.InputRichBlockSectionHeading([emoji("5850346984501680054", "▶️"), " First Track"], size=2),
            types.InputRichBlockParagraph(types.RichTextBold(first_track)),
        ])

    HELP_BASIC = [
        ("/start", "Show welcome message"),
        ("/help", "Show this help message"),
        ("/status", "Show bot statistics"),
        ("/rank or /ranking", "View group rankings"),
    ]
    HELP_MUSIC = [
        ("/play <query>", "Play a song from YouTube"),
        ("/pause", "Pause current playback"),
        ("/resume", "Resume playback"),
        ("/skip", "Skip to next track"),
        ("/stop", "Stop and leave voice chat"),
        ("/playlist", "View current queue"),
        ("/clearplaylist", "Clear upcoming tracks"),
        ("/seek <seconds>", "Seek forward/backward"),
        ("/rewind", "Rewind 10 seconds"),
    ]
    HELP_SETTINGS = [
        ("/settings", "Configure bot settings"),
        ("/vcadmin", "Add voice chat admin"),
        ("/vcunadmin", "Remove voice chat admin"),
    ]
    HELP_OWNER = [("/restart", "Restart the bot")]

    @staticmethod
    def help_rich(section: str = None):
        """Rich help page. section: None (overview), 'basic', 'music' or 'settings'."""
        from pyrogram import types

        bold, code = types.RichTextBold, types.RichTextCode
        Block = types

        def cell(text, header=False):
            return Block.RichBlockTableCell(text, is_header=header, colspan=1, rowspan=1, align="left", valign="middle")

        def table(rows):
            body = [[cell("Command", True), cell("Description", True)]]
            body += [[cell(code(cmd)), cell(desc)] for cmd, desc in rows]
            return Block.InputRichBlockTable(body, is_bordered=True, is_striped=True, is_compact=False)

        def title(text):
            return [Block.InputRichBlockSectionHeading(text, size=1), Block.InputRichBlockDivider()]

        def heading(text):
            return Block.InputRichBlockSectionHeading(text, size=2)

        def para(*parts):
            return Block.InputRichBlockParagraph(list(parts) if len(parts) > 1 else parts[0])

        def quote(*parts):
            return Block.InputRichBlockBlockQuotation([Block.InputRichBlockParagraph(list(parts))])

        def item(*parts):
            return Block.InputRichBlockListItem(blocks=[Block.InputRichBlockParagraph(list(parts))])

        note = quote(bold("📌 Note"), ": Most commands work only in groups where the bot is admin.")

        if section == "basic":
            blocks = title("📖 Basic Commands") + [table(Messages.HELP_BASIC)]
        elif section == "music":
            blocks = title("🎶 Music Commands") + [
                para("(Use in groups)"),
                table(Messages.HELP_MUSIC),
                quote(bold("🎚 Effects"), ": Tap the ", bold("Effects"), " button on the player for ",
                      code("bassboost"), ", ", code("nightcore"), ", ", code("slowed"), ", ", code("lofi"), ", ",
                      code("8d"), " + speed control."),
            ]
        elif section == "settings":
            blocks = title("⚙️ Settings") + [
                para("(Admin only)"),
                table(Messages.HELP_SETTINGS),
                heading("Owner Commands"),
                table(Messages.HELP_OWNER),
                Block.InputRichBlockDivider(),
                note,
            ]
        else:
            blocks = title("🎵 SunloMusic Bot Commands") + [
                para("Pick a category below to see its commands."),
                Block.InputRichBlockList([
                    item(bold("Basic"), " — start, help, status and rankings"),
                    item(bold("Music"), " — playback, queue, seek and effects"),
                    item(bold("Settings"), " — admin tools and owner commands"),
                ]),
                Block.InputRichBlockDivider(),
                note,
            ]
        return Block.InputRichMessage(blocks=blocks)

    @staticmethod
    def help_message(section: str = None) -> str:
        """Plain-text help page (fallback for help_rich)."""
        def rows(items):
            return "\n".join(f"`{cmd}` - {desc}" for cmd, desc in items)

        note = "📌 **Note:** Most commands work only in groups where the bot is admin."
        if section == "basic":
            return f"📖 **Basic Commands**\n\n{rows(Messages.HELP_BASIC)}"
        if section == "music":
            return (
                f"🎶 **Music Commands** (Use in groups)\n\n{rows(Messages.HELP_MUSIC)}\n"
                "🎚 **Effects** - Tap the Effects button on the player for bassboost/nightcore/slowed/lofi/8d + speed control"
            )
        if section == "settings":
            return (
                f"⚙️ **Settings** (Admin only)\n\n{rows(Messages.HELP_SETTINGS)}\n\n"
                f"**Owner Commands:**\n{rows(Messages.HELP_OWNER)}\n\n{note}"
            )
        return (
            "![🎵](tg://emoji?id=5334665104677941170) **SunloMusic Bot Commands**\n\n"
            "Pick a category below to see its commands.\n\n"
            "• **Basic** - start, help, status and rankings\n"
            "• **Music** - playback, queue, seek and effects\n"
            "• **Settings** - admin tools and owner commands\n\n"
            f"{note}"
        )

    @staticmethod
    def dm_not_allowed() -> str:
        return "Add me to a group to play music!"

    @staticmethod
    def status_message(total_users: int, total_groups: int, total_songs: int, active_vcs: int,
                       ping: float = None, cpu_usage: float = None) -> str:
        text = (
            f"📊 **Bot Usage Report**\n"
            f"━━━━━━━━━━━\n"
            f"**Total Users:** {total_users}\n"
            f"**Total Groups:** {total_groups}\n"
            f"**Total Songs Played:** {total_songs}\n"
            f"**Active Voice Chats:** {active_vcs}"
        )
        if ping is not None or cpu_usage is not None:
            text += "\n\n🛰 **Voice Engine**\n"
            if ping is not None:
                text += f"**Ping:** {ping:.1f} ms\n"
            if cpu_usage is not None:
                text += f"**CPU Usage:** {cpu_usage:.1f}%"
        return text

    @staticmethod
    def ranking_message(stats: Dict, period: str = "Daily") -> str:
        message = f"![🏆](tg://emoji?id=5944970130554359187) **Group Rankings - {period}**\n"
        message += "━━━━━━━━━━━━━━━━\n\n"

        if not stats or not stats.get('total_stats'):
            return message + "❌ No data available for this period."

        top_users = stats.get('top_users', [])
        top_songs = stats.get('top_songs', [])
        total_stats = stats.get('total_stats', {})

        if top_users:
            message += "👥 **Top 5 Users:**\n"
            for i, user in enumerate(top_users, 1):
                user_name = user['_id']['user_name']
                count = user['count']
                message += f"{i}. {user_name} - {count} songs\n"
            message += "\n"
        else:
            message += "👥 **Top 5 Users:**\nNo data available\n\n"

        if top_songs:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\n"
            for i, song in enumerate(top_songs, 1):
                song_title = song['_id']
                if len(song_title) > 40:
                    song_title = song_title[:37] + "..."
                count = song['count']
                message += f"{i}. {song_title} - {count} plays\n"
            message += "\n"
        else:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\nNo data available\n\n"

        message += "📊 **Stats:**\n"
        total_songs = total_stats.get('total_songs', 0)
        unique_users = len(total_stats.get('unique_users', []))
        total_duration = total_stats.get('total_duration', 0)

        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60

        message += f"Total Songs: {total_songs}\n"
        message += f"Active Users: {unique_users}\n"
        message += f"Listening Time: {hours}h {minutes}m\n"

        return message

    @staticmethod
    def global_ranking_message(stats: Dict) -> str:
        message = "🌍 **Global Rankings**\n"
        message += "━━━━━━━━━━━━━━━━\n\n"

        if not stats or not stats.get('total_stats'):
            return message + "❌ No data available."

        top_groups = stats.get('top_groups', [])
        top_users = stats.get('top_users', [])
        top_songs = stats.get('top_songs', [])
        total_stats = stats.get('total_stats', {})

        if top_groups:
            message += "![🏆](tg://emoji?id=5944970130554359187) **Top 5 Groups:**\n"
            for i, group in enumerate(top_groups, 1):
                chat_title = group.get('chat_title', 'Unknown Group')
                if len(chat_title) > 30:
                    chat_title = chat_title[:27] + "..."
                count = group['count']
                message += f"{i}. {chat_title} - {count} songs\n"
            message += "\n"
        else:
            message += "![🏆](tg://emoji?id=5944970130554359187) **Top 5 Groups:**\nNo data available\n\n"

        if top_users:
            message += "👥 **Top 5 Users:**\n"
            for i, user in enumerate(top_users, 1):
                user_name = user['_id']['user_name']
                count = user['count']
                message += f"{i}. {user_name} - {count} songs\n"
            message += "\n"
        else:
            message += "👥 **Top 5 Users:**\nNo data available\n\n"

        if top_songs:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\n"
            for i, song in enumerate(top_songs, 1):
                song_title = song['_id']
                if len(song_title) > 40:
                    song_title = song_title[:37] + "..."
                count = song['count']
                message += f"{i}. {song_title} - {count} plays\n"
            message += "\n"
        else:
            message += "![🎵](tg://emoji?id=5334665104677941170) **Top 5 Songs:**\nNo data available\n\n"

        message += "📊 **Global Stats:**\n"
        total_songs = total_stats.get('total_songs', 0)
        unique_groups = len(total_stats.get('unique_groups', []))
        total_duration = total_stats.get('total_duration', 0)

        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60

        message += f"Total Songs: {total_songs}\n"
        message += f"Total Groups: {unique_groups}\n"
        message += f"Total Time: {hours}h {minutes}m\n"

        return message

messages = Messages()
