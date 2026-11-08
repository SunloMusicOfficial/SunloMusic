# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio
import os
import re
import time
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from SunloMusic.core.config import Config
from SunloMusic.core.logging import logger
from SunloMusic.services.yt_search import youtube_search

_executor = ThreadPoolExecutor(max_workers=4)

AUDIO_EXTS = ('.opus', '.webm', '.m4a', '.mp3', '.ogg', '.mp4', '.mkv')

_metadata_cache: Dict[str, tuple] = {}
_CACHE_TTL = 300
_CACHE_MAX = 64


def _is_cache_valid(entry: tuple) -> bool:
    return (time.monotonic() - entry[1]) < _CACHE_TTL


def _slim_info(info: Optional[Dict]) -> Optional[Dict]:
    if not isinstance(info, dict):
        return None
    video_id = info.get('id')
    return {'id': video_id} if video_id else None


def _cache_metadata(url: str, metadata: Dict) -> None:
    now = time.monotonic()
    for key in [k for k, v in _metadata_cache.items() if (now - v[1]) >= _CACHE_TTL]:
        _metadata_cache.pop(key, None)
    if url not in _metadata_cache and len(_metadata_cache) >= _CACHE_MAX:
        oldest = min(_metadata_cache, key=lambda k: _metadata_cache[k][1])
        _metadata_cache.pop(oldest, None)
    _metadata_cache[url] = (metadata, now)


class MediaDownloader:
    def __init__(self):
        self.cookies_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cookies', 'yt.txt')

        self._base_opts = {
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',
            'socket_timeout': 20,
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 2,
        }

        if os.path.exists(self.cookies_path):
            self._base_opts['cookiefile'] = self.cookies_path
            logger.info(f"YouTube cookies loaded from: {self.cookies_path}")
        else:
            logger.warning(f"YouTube cookies file not found at: {self.cookies_path}")

    def _make_opts(self, extra: dict = None) -> dict:
        opts = self._base_opts.copy()
        if extra:
            opts.update(extra)
        return opts

    def _run_sync(self, fn):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(_executor, fn)

    @staticmethod
    def _extract_video_id(url: str) -> Optional[str]:
        if not url:
            return None
        match = re.search(
            r'(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})', url
        )
        return match.group(1) if match else None

    @staticmethod
    def track_video_id(track: Optional[Dict]) -> Optional[str]:
        if not track:
            return None
        raw = track.get('_raw_info')
        video_id = raw.get('id') if isinstance(raw, dict) else None
        return video_id or MediaDownloader._extract_video_id(track.get('url') or '')

    @staticmethod
    def _safe_video_id(video_id: str) -> str:
        return video_id.replace("'", "").replace('"', "").replace('/', '_').replace('\\', '_')

    def _find_cached_file(self, video_id: Optional[str], suffix: str = "") -> Optional[str]:
        if not video_id:
            return None
        safe = self._safe_video_id(video_id)
        for ext in AUDIO_EXTS:
            file_path = f"{Config.DOWNLOADS_DIR}/{safe}{suffix}{ext}"
            if os.path.exists(file_path):
                return os.path.abspath(file_path)
        return None

    async def get_metadata(self, url: str) -> Optional[Dict]:
        cached = _metadata_cache.get(url)
        if cached and _is_cache_valid(cached):
            logger.info(f"Metadata cache hit for {url}")
            return cached[0]

        opts = self._make_opts({
            'extract_flat': False,
            'noplaylist': True,
            'skip_download': True,
        })

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await self._run_sync(lambda: ydl.extract_info(url, download=False))
        except Exception as e:
            logger.error(f"Failed to get metadata for {url}: {e}")
            return None

        if not info:
            return None

        if 'entries' in info:
            if not info['entries']:
                return None
            info = info['entries'][0]
            if not info:
                return None

        title = info.get('title', 'Unknown')
        duration = int(info.get('duration', 0) or 0)

        metadata = {
            'title': title,
            'duration': duration,
            'thumbnail': info.get('thumbnail', ''),
            'uploader': info.get('uploader', 'Unknown'),
            'url': info.get('webpage_url', info.get('url', url)),
            'is_live': info.get('is_live', False),
            '_raw_info': _slim_info(info),
        }

        _cache_metadata(url, metadata)
        logger.info(f"Fetched metadata: {title} ({duration}s)")
        return metadata

    async def download_audio(self, url: str, info: Optional[Dict] = None) -> Optional[str]:
        try:
            video_id = (info or {}).get('id') or self._extract_video_id(url)

            cached = self._find_cached_file(video_id)
            if cached:
                logger.info(f"Cache hit - audio file exists: {cached}")
                return cached

            opts = self._make_opts({
                'format': 'bestaudio[ext=webm]/bestaudio[ext=opus]/bestaudio/best',
                'outtmpl': f'{Config.DOWNLOADS_DIR}/%(id)s.%(ext)s',
                'noplaylist': True,
            })

            with yt_dlp.YoutubeDL(opts) as ydl:
                dl_info = await self._run_sync(lambda: ydl.extract_info(url, download=True))

            if dl_info:
                if isinstance(dl_info, list):
                    dl_info = dl_info[0] if dl_info else None
                elif dl_info.get('entries'):
                    dl_info = dl_info['entries'][0] if dl_info['entries'] else None

            if dl_info and isinstance(dl_info, dict):
                found = self._find_cached_file(dl_info.get('id') or video_id)
                if found:
                    logger.info(f"Downloaded audio: {found}")
                    return found

            logger.error(f"Audio file not found after download for {url}")
            return None
        except Exception as e:
            logger.error(f"Failed to download audio from {url}: {e}")
            return None

    async def download_video(self, url: str, quality: str = "720p", info: Optional[Dict] = None) -> Optional[str]:
        try:
            video_id = (info or {}).get('id') or self._extract_video_id(url)

            cached = self._find_cached_file(video_id, suffix="_video")
            if cached:
                logger.info(f"Cache hit - video file exists: {cached}")
                return cached

            format_selector = self._get_format_selector(quality)
            opts = self._make_opts({
                'format': format_selector,
                'outtmpl': f'{Config.DOWNLOADS_DIR}/%(id)s_video.%(ext)s',
                'noplaylist': True,
            })

            with yt_dlp.YoutubeDL(opts) as ydl:
                dl_info = await self._run_sync(lambda: ydl.extract_info(url, download=True))

            if dl_info:
                if isinstance(dl_info, list):
                    dl_info = dl_info[0] if dl_info else None
                elif isinstance(dl_info, dict) and dl_info.get('entries'):
                    dl_info = dl_info['entries'][0] if dl_info['entries'] else None

            if dl_info and isinstance(dl_info, dict):
                found = self._find_cached_file(dl_info.get('id') or video_id, suffix="_video")
                if found:
                    logger.info(f"Downloaded video: {found}")
                    return found

            logger.error(f"Downloaded video file not found for {url}")
            return None
        except Exception as e:
            logger.error(f"Failed to download video from {url}: {e}")
            return None

    def _get_format_selector(self, quality: str) -> str:
        quality_map = {
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        }
        return quality_map.get(quality, quality_map['720p'])

    def is_playlist_url(self, url: str) -> bool:
        playlist_patterns = [
            r'[?&]list=([a-zA-Z0-9_-]+)',
            r'youtube\.com/playlist\?',
        ]
        return any(re.search(p, url) for p in playlist_patterns)

    def _extract_playlist_id(self, url: str) -> Optional[str]:
        match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else None

    async def get_playlist_info(self, url: str) -> Optional[Dict]:
        opts = self._make_opts({
            'extract_flat': True,
            'noplaylist': False,
            'playlistend': 999,
            'skip_download': True,
        })
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await self._run_sync(lambda: ydl.extract_info(url, download=False))

            if not info or 'entries' not in info:
                return None

            entries = [e for e in info['entries'] if e]
            return {
                'title': info.get('title', 'Unknown Playlist'),
                'total': len(entries),
                'entries': entries,
            }
        except Exception as e:
            logger.error(f"Failed to get playlist info for {url}: {e}")
            return None

    async def get_playlist_batch(self, url: str, start: int, count: int = 10) -> List[Dict]:
        opts = self._make_opts({
            'extract_flat': True,
            'noplaylist': False,
            'playliststart': start + 1,
            'playlistend': start + count,
            'skip_download': True,
        })
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await self._run_sync(lambda: ydl.extract_info(url, download=False))

            if not info or 'entries' not in info:
                return []

            tracks = []
            for entry in info['entries']:
                if not entry:
                    continue
                video_id = entry.get('id', '')
                tracks.append({
                    'type': 'youtube',
                    'url': f"https://www.youtube.com/watch?v={video_id}" if video_id else entry.get('url', ''),
                    'title': entry.get('title', 'Unknown'),
                    'duration': int(entry.get('duration', 0) or 0),
                    'uploader': entry.get('uploader', 'Unknown'),
                    'thumbnail': entry.get('thumbnail', ''),
                    'is_live': entry.get('is_live', False),
                    '_raw_info': None,
                })
            return tracks
        except Exception as e:
            logger.error(f"Failed to get playlist batch (start={start}): {e}")
            return []

    async def is_live_stream(self, url: str) -> bool:
        metadata = await self.get_metadata(url)
        return metadata.get('is_live', False) if metadata else False

    async def search_one(self, query: str) -> Optional[Dict]:
        if not query:
            return None

        metadata = await youtube_search.search_one(query)
        if metadata:
            _cache_metadata(metadata['url'], metadata)
            return metadata

        logger.warning(f"InnerTube search returned nothing for {query!r}; falling back to yt-dlp")
        return await self._search_one_ytdlp(query)

    async def _search_one_ytdlp(self, query: str) -> Optional[Dict]:
        if not query:
            return None

        opts = self._make_opts({
            'skip_download': True,
            'noplaylist': True,
            'default_search': 'ytsearch1:',
        })

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await self._run_sync(lambda: ydl.extract_info(query, download=False))
        except Exception as e:
            logger.error(f"Failed to search YouTube for '{query}': {e}")
            return None

        if not info:
            return None

        entries = info.get('entries') or ([info] if info.get('id') else [])
        entry = next((e for e in entries if e and e.get('id')), None)
        if not entry:
            return None

        video_id = entry.get('id')
        url = entry.get('webpage_url') or f"https://www.youtube.com/watch?v={video_id}"
        metadata = {
            'title': entry.get('title', 'Unknown'),
            'duration': int(entry.get('duration') or 0),
            'thumbnail': entry.get('thumbnail', ''),
            'uploader': entry.get('uploader') or entry.get('channel', 'Unknown'),
            'url': url,
            'is_live': entry.get('is_live', False),
            '_raw_info': _slim_info(entry),
        }

        _cache_metadata(url, metadata)
        logger.info(f"Search resolved: {metadata['title']} ({metadata['duration']}s)")
        return metadata

    async def search_youtube(self, query: str, max_results: int = 10) -> list:
        if not query:
            return []

        results = await youtube_search.search(query, limit=max_results)
        if results:
            return results

        logger.warning(f"InnerTube search returned nothing for {query!r}; falling back to yt-dlp")
        return await self._search_youtube_ytdlp(query, max_results)

    async def _search_youtube_ytdlp(self, query: str, max_results: int = 10) -> list:
        try:
            search_url = f"ytsearch{max_results}:{query}"
            opts = self._make_opts({
                'extract_flat': True,
                'skip_download': True,
                'noplaylist': True,
            })

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await self._run_sync(
                    lambda: ydl.extract_info(search_url, download=False)
                )

            if not info or not isinstance(info, dict) or 'entries' not in info:
                return []

            results = []
            for entry in info['entries']:
                if not entry or not isinstance(entry, dict):
                    continue
                results.append({
                    'title': entry.get('title', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                    'duration': int(entry.get('duration', 0) or 0),
                    'thumbnail': entry.get('thumbnail', ''),
                    'uploader': entry.get('uploader', 'Unknown'),
                    'view_count': entry.get('view_count', 0),
                    'id': entry.get('id', '')
                })
            return results
        except Exception as e:
            logger.error(f"Failed to search YouTube for '{query}': {e}")
            return []

    async def get_related_tracks(self, track: Optional[Dict], limit: int = 5) -> List[Dict]:
        video_id = self.track_video_id(track)
        if not video_id:
            return []

        results = await youtube_search.related(video_id, limit=limit)
        if not results:
            logger.warning(f"InnerTube related returned nothing for {video_id}; falling back to yt-dlp")
            return await self._related_ytdlp(video_id, limit)

        tracks = []
        for entry in results[:limit]:
            if self._too_long(entry.get('duration', 0)):
                logger.info(f"Skipping related track longer than limit: {entry.get('title')}")
                continue
            tracks.append({
                'type': 'youtube',
                'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                'title': entry.get('title', 'Unknown'),
                'duration': entry.get('duration', 0),
                'uploader': entry.get('uploader', 'Unknown'),
                'thumbnail': entry.get('thumbnail', ''),
                'is_live': False,
                '_raw_info': {'id': entry.get('id')},
            })
        return tracks

    async def _related_ytdlp(self, video_id: str, limit: int) -> List[Dict]:
        mix_url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
        batch = await self.get_playlist_batch(mix_url, 0, limit + 1)
        return [
            track for track in batch
            if self.track_video_id(track) != video_id and not self._too_long(track.get('duration', 0))
        ][:limit]

    @staticmethod
    def _too_long(duration) -> bool:
        return int(duration or 0) > Config.MAX_TRACK_DURATION

downloader = MediaDownloader()
