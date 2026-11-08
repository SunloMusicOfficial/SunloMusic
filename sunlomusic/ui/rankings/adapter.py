# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from SunloMusic.core.logging import logger

from SunloMusic.ui.rankings.renderer import PALETTE, render_banner

_ACCENT_SONGS = (167, 116, 255)
_ACCENT_PEOPLE = (56, 189, 248)
_ACCENT_TIME = (74, 222, 128)

Row = Tuple[str, int, str, Optional[bytes]]


def _fmt_duration(seconds: int) -> str:
    seconds = int(seconds or 0)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def _users_rows(top_users: List[dict], avatars: Dict) -> List[Row]:
    rows: List[Row] = []
    for u in top_users or []:
        ident = u.get("_id") or {}
        name = (ident.get("user_name") if isinstance(ident, dict) else None) or "Unknown"
        uid = ident.get("user_id") if isinstance(ident, dict) else None
        rows.append((str(name), int(u.get("count", 0)), "songs", avatars.get(("user", uid))))
    return rows


def _songs_rows(top_songs: List[dict], avatars: Dict) -> List[Row]:
    rows: List[Row] = []
    for s in top_songs or []:
        title = s.get("_id") or "Unknown"
        rows.append((str(title), int(s.get("count", 0)), "plays", avatars.get(("song", s.get("thumb")))))
    return rows


def _groups_rows(top_groups: List[dict], avatars: Dict) -> List[Row]:
    rows: List[Row] = []
    for g in top_groups or []:
        title = g.get("chat_title", "Unknown Group") or "Unknown Group"
        rows.append((str(title), int(g.get("count", 0)), "songs", avatars.get(("chat", g.get("_id")))))
    return rows


def build_rankings_banner(scope: str, stats: Dict, output_path: Optional[str] = None, avatars: Optional[Dict] = None) -> Optional[str]:
    avatars = avatars or {}
    if not stats or not stats.get("total_stats"):
        return None

    if output_path is None:
        fd, output_path = tempfile.mkstemp(prefix=f"rankings_{scope}_", suffix=".png")
        os.close(fd)
    out = Path(output_path)

    total = stats.get("total_stats", {}) or {}
    total_songs = total.get("total_songs", 0)
    duration = _fmt_duration(total.get("total_duration", 0))

    if scope == "global":
        unique_groups = len(total.get("unique_groups", []) or [])
        panels = [
            ("TOP 5 GROUPS", "group", PALETTE["violet"], _groups_rows(stats.get("top_groups", []), avatars), "Most active music communities worldwide"),
            ("TOP 5 USERS", "user", PALETTE["cyan"], _users_rows(stats.get("top_users", []), avatars), "Most active listeners across all communities"),
            ("TOP 5 SONGS", "music", PALETTE["pink"], _songs_rows(stats.get("top_songs", []), avatars), "Most played tracks across all communities"),
        ]
        stat_cards = [
            ("music", str(total_songs), "TOTAL SONGS", "All tracked tracks across communities", _ACCENT_SONGS),
            ("group", str(unique_groups), "TOTAL GROUPS", "Active communities", _ACCENT_PEOPLE),
            ("clock", duration, "TOTAL LISTENING TIME", "Combined listening duration", _ACCENT_TIME),
        ]
        render_banner(
            output=out,
            title="GLOBAL RANKINGS",
            tagline="THE WORLD IS LISTENING",
            panels=panels,
            stats_title="GLOBAL STATS",
            stats_subtitle="Premium overview across all connected music communities",
            stats=stat_cards,
            seed=31052026,
        )
        return str(out)

    is_weekly = scope == "weekly"
    unique_users = len(total.get("unique_users", []) or [])
    panels = [
        ("TOP 5 USERS", "user", PALETTE["cyan"], _users_rows(stats.get("top_users", []), avatars), "Top listeners in this group"),
        ("TOP 5 SONGS", "music", PALETTE["pink"], _songs_rows(stats.get("top_songs", []), avatars), "Most played tracks in this group"),
    ]
    stat_cards = [
        ("music", str(total_songs), "TOTAL SONGS",
         "Tracked this week" if is_weekly else "Tracked today", _ACCENT_SONGS),
        ("user", str(unique_users), "ACTIVE USERS",
         "Weekly listeners" if is_weekly else "Listeners today", _ACCENT_PEOPLE),
        ("clock", duration, "LISTENING TIME",
         "Weekly duration" if is_weekly else "Daily duration", _ACCENT_TIME),
    ]
    render_banner(
        output=out,
        title="GROUP RANKINGS",
        tagline="WEEKLY MUSIC REPORT" if is_weekly else "DAILY MUSIC REPORT",
        panels=panels,
        stats_title="WEEKLY STATS" if is_weekly else "DAILY STATS",
        stats_subtitle=("This week's group listening activity at a glance" if is_weekly
                        else "Today's group listening activity at a glance"),
        stats=stat_cards,
        seed=6042028 if is_weekly else 6042026,
    )
    return str(out)


async def generate_rankings_banner(scope: str, stats: Dict, avatars: Optional[Dict] = None, timeout: float = 25.0) -> Optional[str]:
    try:
        return await asyncio.wait_for(asyncio.to_thread(build_rankings_banner, scope, stats, None, avatars), timeout=timeout)
    except Exception as e:
        logger.error(f"Rankings banner generation failed ({scope}): {e}")
        return None
