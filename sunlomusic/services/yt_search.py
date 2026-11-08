from sunlomusic.services.sunlomusic_api import download_with_sunlomusic_api
# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio
import re
import time
from typing import Any, Dict, List, Optional

import aiohttp

from sunlomusic.core.logging import logger

_API_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
_CLIENT_VERSION = "2.20250101.01.00"
_ENDPOINT = f"https://www.youtube.com/youtubei/v1/search?key={_API_KEY}"
_ENDPOINT_NEXT = f"https://www.youtube.com/youtubei/v1/next?key={_API_KEY}"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": _USER_AGENT,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.youtube.com",
    "Referer": "https://www.youtube.com/",
    "X-YouTube-Client-Name": "1",
    "X-YouTube-Client-Version": _CLIENT_VERSION,
}

_TIMEOUT = aiohttp.ClientTimeout(total=10)

_DURATION_RE = re.compile(r"^\d{1,2}(?::\d{1,2}){1,2}$")


def _parse_duration(text: str) -> int:
    if not text or not _DURATION_RE.match(text.strip()):
        return 0
    total = 0
    for part in text.strip().split(":"):
        total = total * 60 + int(part)
    return total


def _parse_views(text: str) -> int:
    if not text:
        return 0
    digits = re.sub(r"[^\d]", "", text.split("view")[0])
    return int(digits) if digits else 0


def _text(node: Any) -> str:
    if not isinstance(node, dict):
        return ""
    if "simpleText" in node:
        return node["simpleText"]
    runs = node.get("runs")
    if isinstance(runs, list):
        return "".join(r.get("text", "") for r in runs if isinstance(r, dict))
    return ""


def _dig(node: Any, *path: str, default: Any = None) -> Any:
    for key in path:
        if not isinstance(node, dict):
            return default
        node = node.get(key)
        if node is None:
            return default
    return node


def _collect(node: Any, key: str, out: List[Any]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                out.append(v)
            else:
                _collect(v, key, out)
    elif isinstance(node, list):
        for v in node:
            _collect(v, key, out)


def _is_live(video: Dict) -> bool:
    for badge in video.get("badges") or []:
        style = (badge.get("metadataBadgeRenderer") or {}).get("style", "")
        if style == "BADGE_STYLE_TYPE_LIVE_NOW":
            return True
    overlay = video.get("thumbnailOverlays") or []
    for entry in overlay:
        status = entry.get("thumbnailOverlayTimeStatusRenderer") or {}
        if status.get("style") == "LIVE":
            return True
    return False


def _to_track(video: Dict) -> Optional[Dict]:
    video_id = video.get("videoId")
    if not video_id:
        return None

    thumbnails = ((video.get("thumbnail") or {}).get("thumbnails") or [])
    thumbnail = thumbnails[-1].get("url", "") if thumbnails else ""

    return {
        "id": video_id,
        "title": _text(video.get("title")) or "Unknown",
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "duration": _parse_duration(_text(video.get("lengthText"))),
        "thumbnail": thumbnail,
        "uploader": _text(
            video.get("ownerText")
            or video.get("longBylineText")
            or video.get("shortBylineText")
        ) or "Unknown",
        "is_live": _is_live(video),
        "view_count": _parse_views(_text(video.get("viewCountText"))),
    }


def _lockup_duration(lockup: Dict) -> int:
    overlays = _dig(lockup, "contentImage", "thumbnailViewModel", "overlays", default=[])
    for overlay in overlays:
        badges = ((overlay or {}).get("thumbnailBottomOverlayViewModel") or {}).get("badges") or []
        for badge in badges:
            text = ((badge or {}).get("thumbnailBadgeViewModel") or {}).get("text", "")
            duration = _parse_duration(text)
            if duration:
                return duration
    return 0


def _lockup_uploader(lockup: Dict) -> str:
    rows = _dig(
        lockup, "metadata", "lockupMetadataViewModel", "metadata",
        "contentMetadataViewModel", "metadataRows", default=[],
    )
    for row in rows:
        for part in (row or {}).get("metadataParts") or []:
            text = ((part or {}).get("text") or {}).get("content", "")
            if text:
                return text
    return "Unknown"


def _lockup_to_track(lockup: Dict) -> Optional[Dict]:
    video_id = lockup.get("contentId")
    if not video_id or lockup.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO":
        return None

    duration = _lockup_duration(lockup)
    if duration <= 0:
        return None

    sources = _dig(lockup, "contentImage", "thumbnailViewModel", "image", "sources", default=[])
    thumbnail = sources[-1].get("url", "") if sources else ""

    return {
        "id": video_id,
        "title": _dig(lockup, "metadata", "lockupMetadataViewModel", "title", "content") or "Unknown",
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "duration": duration,
        "thumbnail": thumbnail,
        "uploader": _lockup_uploader(lockup),
        "is_live": False,
        "view_count": 0,
    }


class YouTubeSearch:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            async with self._session_lock:
                if self._session is None or self._session.closed:
                    self._session = aiohttp.ClientSession(
                        headers=_HEADERS, timeout=_TIMEOUT
                    )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def search(self, query: str, limit: int = 1) -> List[Dict]:
        query = (query or "").strip()
        if not query:
            return []

        payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": _CLIENT_VERSION,
                    "hl": "en",
                    "gl": "US",
                }
            },
            "query": query,
        }

        started = time.monotonic()
        try:
            session = await self._get_session()
            async with session.post(_ENDPOINT, json=payload) as resp:
                if resp.status != 200:
                    logger.warning(
                        f"InnerTube search returned HTTP {resp.status} for {query!r}"
                    )
                    return []
                data = await resp.json(content_type=None)
        except asyncio.TimeoutError:
            logger.warning(f"InnerTube search timed out for {query!r}")
            return []
        except Exception as e:
            logger.warning(f"InnerTube search failed for {query!r}: {e}")
            return []

        renderers: List[Any] = []
        _collect(data, "videoRenderer", renderers)

        tracks = []
        for renderer in renderers:
            if len(tracks) >= limit:
                break
            if not isinstance(renderer, dict):
                continue
            track = _to_track(renderer)
            if track:
                tracks.append(track)

        if tracks:
            logger.info(
                f"InnerTube search {query!r} -> {len(tracks)} result(s) "
                f"in {time.monotonic() - started:.2f}s"
            )
        return tracks

    async def related(self, video_id: str, limit: int = 25) -> List[Dict]:
        video_id = (video_id or "").strip()
        if not video_id:
            return []

        payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": _CLIENT_VERSION,
                    "hl": "en",
                    "gl": "US",
                }
            },
            "videoId": video_id,
        }

        started = time.monotonic()
        try:
            session = await self._get_session()
            async with session.post(_ENDPOINT_NEXT, json=payload) as resp:
                if resp.status != 200:
                    logger.warning(
                        f"InnerTube next returned HTTP {resp.status} for {video_id}"
                    )
                    return []
                data = await resp.json(content_type=None)
        except asyncio.TimeoutError:
            logger.warning(f"InnerTube next timed out for {video_id}")
            return []
        except Exception as e:
            logger.warning(f"InnerTube next failed for {video_id}: {e}")
            return []

        results = _dig(
            data,
            "contents", "twoColumnWatchNextResults",
            "secondaryResults", "secondaryResults", "results",
            default=[],
        )

        tracks: List[Dict] = []
        seen = {video_id}
        for entry in results:
            if len(tracks) >= limit:
                break
            if not isinstance(entry, dict):
                continue

            renderer = entry.get("lockupViewModel") or entry.get("compactVideoRenderer")
            if not isinstance(renderer, dict):
                continue

            track = _lockup_to_track(renderer) if "contentId" in renderer else _to_track(renderer)
            if not track or track["id"] in seen:
                continue

            seen.add(track["id"])
            tracks.append(track)

        logger.info(
            f"InnerTube related {video_id} -> {len(tracks)} result(s) "
            f"in {time.monotonic() - started:.2f}s"
        )
        return tracks

    async def search_one(self, query: str) -> Optional[Dict]:
        results = await self.search(query, limit=1)
        if not results:
            return None

        track = results[0]
        return {
            "title": track["title"],
            "duration": track["duration"],
            "thumbnail": track["thumbnail"],
            "uploader": track["uploader"],
            "url": track["url"],
            "is_live": track["is_live"],
            "_raw_info": {"id": track["id"]},
        }


youtube_search = YouTubeSearch()
