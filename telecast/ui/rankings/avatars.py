from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, Tuple

import aiohttp

from SunloMusic.core.logging import logger

Key = Tuple[str, object]

_OK_TTL = 6 * 3600
_MISS_TTL = 30 * 60
_cache: Dict[Key, Tuple[float, Optional[bytes]]] = {}
_titles: Dict[int, Tuple[float, str]] = {}


def _cached(key: Key):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < (_OK_TTL if hit[1] else _MISS_TTL):
        return True, hit[1]
    return False, None


async def _telegram_photo(client, peer_id: int, remember_title: bool = False) -> Optional[bytes]:
    chat = await client.get_chat(peer_id)
    title = getattr(chat, "title", None)
    if remember_title and title:
        _titles[peer_id] = (time.time(), title)
    photo = getattr(chat, "photo", None)
    if not photo:
        return None
    buf = await client.download_media(photo.small_file_id, in_memory=True)
    return bytes(buf.getbuffer()) if buf else None


async def _http_image(session: aiohttp.ClientSession, url: str) -> Optional[bytes]:
    async with session.get(url) as resp:
        if resp.status != 200:
            return None
        data = await resp.content.read(2_000_000)
        return data or None


async def _load(key: Key, client, session) -> Optional[bytes]:
    kind, ident = key
    try:
        if kind in ("user", "chat"):
            data = await _telegram_photo(client, int(ident), remember_title=(kind == "chat"))
        else:
            data = await _http_image(session, str(ident))
    except Exception as e:
        logger.debug(f"Rankings avatar miss {key}: {e}")
        data = None
    _cache[key] = (time.time(), data)
    return data


def _wanted(stats: dict) -> list[Key]:
    keys: list[Key] = []
    for g in stats.get("top_groups") or []:
        if g.get("_id") is not None:
            keys.append(("chat", g["_id"]))
    for u in stats.get("top_users") or []:
        ident = u.get("_id") or {}
        if isinstance(ident, dict) and ident.get("user_id"):
            keys.append(("user", ident["user_id"]))
    for s in stats.get("top_songs") or []:
        if s.get("thumb"):
            keys.append(("song", s["thumb"]))
    return keys


def _fill_group_titles(stats: dict) -> None:
    """Groups missing from broadcast_groups come back as 'Unknown Group'; use the live Telegram title instead."""
    for g in stats.get("top_groups") or []:
        known = g.get("chat_title")
        if known and known != "Unknown Group":
            continue
        hit = _titles.get(g.get("_id"))
        if hit and time.time() - hit[0] < _OK_TTL:
            g["chat_title"] = hit[1]


async def collect_avatars(client, stats: dict, timeout: float = 10.0) -> Dict[Key, bytes]:
    """Fetch profile photos / song thumbnails for the ranked rows; misses are simply absent.

    Also repairs missing group titles in ``stats`` (in place) from the same Telegram lookup.
    """
    stats = stats or {}
    keys = _wanted(stats)
    out: Dict[Key, bytes] = {}
    todo: list[Key] = []
    unresolved = {g.get("_id") for g in stats.get("top_groups") or []
                  if g.get("chat_title") in (None, "", "Unknown Group") and g.get("_id") not in _titles}
    for key in keys:
        found, data = _cached(key)
        if found and not (key[0] == "chat" and key[1] in unresolved):
            if data:
                out[key] = data
        else:
            todo.append(key)
    if not todo:
        _fill_group_titles(stats)
        return out

    async def run():
        timeout_cfg = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
            results = await asyncio.gather(*(_load(k, client, session) for k in todo), return_exceptions=True)
        for key, data in zip(todo, results):
            if isinstance(data, bytes):
                out[key] = data

    try:
        await asyncio.wait_for(run(), timeout=timeout)
    except Exception as e:
        logger.warning(f"Rankings avatar fetch incomplete: {e}")
    _fill_group_titles(stats)
    return out
