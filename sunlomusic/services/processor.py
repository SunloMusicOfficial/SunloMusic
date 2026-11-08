# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio
import os
from typing import Optional
from sunlomusic.core.config import Config
from sunlomusic.core.logging import logger

class MediaProcessor:
    @staticmethod
    def _clean_filename(filename: str) -> str:
        if not filename:
            return 'Unknown'

        import os
        name = os.path.splitext(filename)[0]

        name = name.replace('_', ' ')

        if len(name) > 60:
            name = name[:57] + '...'

        return name

    @staticmethod
    async def get_stream_url(url: str, is_video: bool = False) -> Optional[str]:
        cookies_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cookies', 'yt.txt')

        cmd = [
            'yt-dlp',
            '-g',
            '-f', 'bestvideo+bestaudio/best' if is_video else 'bestaudio/best',
        ]

        if os.path.exists(cookies_path):
            cmd.extend(['--cookies', cookies_path])
            logger.info(f"Using cookies from {cookies_path} for stream URL extraction")

        cmd.append(url)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                stream_url = stdout.decode().strip().split('\n')[0]
                logger.info(f"Got stream URL for {url}")
                return stream_url
            else:
                logger.error(f"yt-dlp error: {stderr.decode()}")
                return None
        except Exception as e:
            logger.error(f"Failed to get stream URL: {e}")
            return None

    @staticmethod
    async def download_telegram_file(client, message) -> Optional[dict]:
        try:
            if message.audio:
                file_path = f"{Config.DOWNLOADS_DIR}/tg_{message.audio.file_id}.mp3"
                if not os.path.exists(file_path):
                    await client.download_media(message.audio, file_path)
                title = message.audio.title or MediaProcessor._clean_filename(message.audio.file_name) or 'Audio File'
                return {
                    'file_path': file_path,
                    'title': title,
                    'performer': message.audio.performer or 'Unknown',
                    'duration': int(message.audio.duration or 0)
                }
            elif message.video:
                file_path = f"{Config.DOWNLOADS_DIR}/tg_{message.video.file_id}.mp4"
                if not os.path.exists(file_path):
                    await client.download_media(message.video, file_path)
                title = MediaProcessor._clean_filename(message.video.file_name) or 'Video File'
                return {
                    'file_path': file_path,
                    'title': title,
                    'performer': 'Telegram',
                    'duration': int(message.video.duration or 0)
                }
            elif message.document:
                file_name = message.document.file_name
                if file_name and file_name.endswith(('.mp3', '.mp4', '.mkv', '.avi', '.flac', '.opus', '.ogg')):
                    file_path = f"{Config.DOWNLOADS_DIR}/tg_{message.document.file_id}_{file_name}"
                    if not os.path.exists(file_path):
                        await client.download_media(message.document, file_path)
                    title = MediaProcessor._clean_filename(file_name)
                    return {
                        'file_path': file_path,
                        'title': title,
                        'performer': 'Telegram',
                        'duration': 0
                    }
                else:
                    return {'error': 'unsupported'}
            return {'error': 'unsupported'}
        except Exception as e:
            logger.error(f"Failed to download Telegram file: {e}")
            return None

processor = MediaProcessor()
