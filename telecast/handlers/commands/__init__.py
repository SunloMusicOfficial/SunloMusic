# Copyright (C) @itsSmartDev

from pyrogram import Client, filters

from .player import (
    play_command,
    pause_command,
    resume_command,
    skip_command,
    stop_command,
    seek_command,
    rewind_command,
    mute_command,
    unmute_command,
)
from .queue import clearplaylist_command, playlist_command
from .settings import settings_command, vcadmin_command, vcunadmin_command
from .rankings import rank_command, ranking_command, show_rankings
from .admin import start_command, help_command, restart_command, status_command, logs_command


def register_commands(app: Client, player):
    async def play_wrapper(c, m):
        await play_command(c, m, player, None)

    async def pause_wrapper(c, m):
        await pause_command(c, m, player)

    async def resume_wrapper(c, m):
        await resume_command(c, m, player)

    async def skip_wrapper(c, m):
        await skip_command(c, m, player)

    async def stop_wrapper(c, m):
        await stop_command(c, m, player)

    async def seek_wrapper(c, m):
        await seek_command(c, m, player)

    async def rewind_wrapper(c, m):
        await rewind_command(c, m, player)

    async def mute_wrapper(c, m):
        await mute_command(c, m, player)

    async def unmute_wrapper(c, m):
        await unmute_command(c, m, player)

    async def playlist_wrapper(c, m):
        await playlist_command(c, m, player)

    async def status_wrapper(c, m):
        await status_command(c, m, player)

    prefixes = ["/", "."]

    app.on_message(filters.command("start", prefixes))(start_command)
    app.on_message(filters.command("play", prefixes))(play_wrapper)
    app.on_message(filters.command("pause", prefixes))(pause_wrapper)
    app.on_message(filters.command("resume", prefixes))(resume_wrapper)
    app.on_message(filters.command("skip", prefixes))(skip_wrapper)
    app.on_message(filters.command("stop", prefixes))(stop_wrapper)
    app.on_message(filters.command("end", prefixes))(stop_wrapper)
    app.on_message(filters.command("seek", prefixes))(seek_wrapper)
    app.on_message(filters.command("rewind", prefixes))(rewind_wrapper)
    app.on_message(filters.command("vcmute", prefixes))(mute_wrapper)
    app.on_message(filters.command("vcunmute", prefixes))(unmute_wrapper)
    app.on_message(filters.command("clearplaylist", prefixes))(clearplaylist_command)
    app.on_message(filters.command("settings", prefixes))(settings_command)
    app.on_message(filters.command("playlist", prefixes))(playlist_wrapper)
    app.on_message(filters.command("vcadmin", prefixes))(vcadmin_command)
    app.on_message(filters.command("vcunadmin", prefixes))(vcunadmin_command)
    app.on_message(filters.command("help", prefixes))(help_command)
    app.on_message(filters.command("restart", prefixes))(restart_command)
    app.on_message(filters.command("logs", prefixes))(logs_command)
    app.on_message(filters.command("status", prefixes))(status_wrapper)
    app.on_message(filters.command("rank", prefixes))(rank_command)
    app.on_message(filters.command("ranking", prefixes))(ranking_command)
