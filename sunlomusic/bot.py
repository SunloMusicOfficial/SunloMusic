# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio
import signal

from pyrogram import Client
from pyrogram.enums import ParseMode

from sunlomusic.core.config import Config
from sunlomusic.core.logging import logger
from sunlomusic.db import db
from sunlomusic.services.stream import TGCallsManager
from sunlomusic.services.player import PlayerController
from sunlomusic.ui.title import TitleUpdater
from sunlomusic.ui.progress import ProgressUpdater
from sunlomusic.ui.vc_messages import VCMessenger
from sunlomusic.handlers.commands import register_commands
from sunlomusic.handlers.callbacks import register_callbacks
from sunlomusic.handlers.broadcast import register_broadcast_handlers
from sunlomusic.handlers.events import register_event_handlers
from sunlomusic.handlers.inline import register_inline_handlers\nfrom sunlomusic.handlers.gemini import register_gemini_handlers
from sunlomusic.handlers.tempmail import register_tempmail_handlers
from sunlomusic.handlers.whisper import register_whisper_handlers
from sunlomusic.utils.monitor import monitor_logger
from sunlomusic.utils.watchdog import LoopWatchdog


class VCMusicBot:
    def __init__(self):
        self.bot = None
        self.user_client = None
        self.tgcalls_manager = None
        self.player_controller = None
        self.title_updater = None
        self.progress_updater = None
        self.vc_messenger = None
        self.watchdog = None
        self.is_running = False

    async def initialize(self):
        Config.validate()
        logger.info("Starting VC Music Bot...")

        self._cleanup_files()

        await db.connect()

        self.bot = Client(
            "SunloMusic",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            parse_mode=ParseMode.MARKDOWN
        )

        self.user_client = Client(
            "user_client",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=Config.SESSION_STRING,
            parse_mode=ParseMode.MARKDOWN
        )

        self.tgcalls_manager = TGCallsManager(self.user_client)

        self.player_controller = PlayerController(self.tgcalls_manager, self.bot)

        self.title_updater = TitleUpdater(self.user_client)

        self.progress_updater = ProgressUpdater(self.bot, self.player_controller)

        self.vc_messenger = VCMessenger(self.user_client)
        self.tgcalls_manager.set_vc_join_callback(self.vc_messenger.welcome)

        import sunlomusic.services.player as player_module
        player_module.player_controller = self.player_controller

        import sunlomusic.ui.title as title_module
        title_module.title_updater = self.title_updater

        import sunlomusic.ui.progress as progress_module
        progress_module.progress_updater = self.progress_updater

        register_commands(self.bot, self.player_controller)
        register_callbacks(self.bot, self.player_controller, self.user_client)
        register_broadcast_handlers(self.bot)
        register_event_handlers(self.bot)
        register_inline_handlers(self.bot)
        register_whisper_handlers(self.bot)
        register_tempmail_handlers(self.bot)

        logger.info("Bot initialized successfully")

    async def start(self):
        try:
            await self.initialize()

            await self.bot.start()
            logger.info("Bot client started")

            await self.user_client.start()
            logger.info("User client started successfully")

            await self.tgcalls_manager.initialize()
            logger.info("PyTgCalls initialized")

            monitor_logger.set_client(self.bot)
            logger.info("Monitor logger initialized")

            self.is_running = True

            self.watchdog = LoopWatchdog(on_stall=self._on_loop_stall)
            self.watchdog.start()

            bot_info = await self.bot.get_me()
            user_info = await self.user_client.get_me()
            logger.info(f"Bot @{bot_info.username} is now running")
            logger.info(f"User client: {user_info.first_name} (ID: {user_info.id})")

            await self._check_restart_message()

            await self.idle()

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self):
        if not self.is_running:
            return

        logger.info("Shutting down bot...")
        self.is_running = False

        if self.watchdog:
            self.watchdog.stop()

        if self.progress_updater:
            self.progress_updater.stop_all_updates()
            logger.info("Stopped all progress updates")

        if self.tgcalls_manager:
            await self.tgcalls_manager.cleanup()

        if self.user_client:
            await self.user_client.stop()
            logger.info("User client stopped")

        if self.bot:
            await self.bot.stop()
            logger.info("Bot client stopped")

        if db:
            await db.close()

        self._cleanup_files()

        logger.info("Bot stopped successfully")

    def _on_loop_stall(self, blocked_for: float):
        loop = self.watchdog._loop if self.watchdog else None
        if not loop:
            return
        try:
            asyncio.run_coroutine_threadsafe(
                monitor_logger.log_error(
                    "Event Loop Stall", 0, "system",
                    f"Event loop was blocked for ~{blocked_for:.1f}s"
                ),
                loop,
            )
        except Exception:
            pass

    def _cleanup_files(self):
        import os
        import shutil

        try:
            if os.path.exists(Config.DOWNLOADS_DIR):
                shutil.rmtree(Config.DOWNLOADS_DIR)
                os.makedirs(Config.DOWNLOADS_DIR, exist_ok=True)
                logger.info(f"Cleaned up {Config.DOWNLOADS_DIR}")

            if os.path.exists(Config.CACHE_DIR):
                shutil.rmtree(Config.CACHE_DIR)
                os.makedirs(Config.CACHE_DIR, exist_ok=True)
                logger.info(f"Cleaned up {Config.CACHE_DIR}")
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")

    async def _check_restart_message(self):
        import os
        import json

        restart_file = '.restart_info.json'

        if not os.path.exists(restart_file):
            return

        try:
            with open(restart_file, 'r') as f:
                restart_info = json.load(f)

            chat_id = restart_info.get('chat_id')
            message_id = restart_info.get('message_id')

            if chat_id and message_id:
                try:
                    await self.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="✅ **Bot restarted successfully!**"
                    )
                    logger.info(f"Updated restart message in chat {chat_id}")
                except Exception as e:
                    logger.error(f"Failed to update restart message: {e}")

            os.remove(restart_file)
            logger.info("Restart info file cleaned up")

        except Exception as e:
            logger.error(f"Error checking restart message: {e}")
            try:
                if os.path.exists(restart_file):
                    os.remove(restart_file)
            except:
                pass

    async def idle(self):
        stop_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT)
        loop = asyncio.get_running_loop()

        background_tasks = set()

        async def signal_handler(sig):
            logger.info(f"Received signal {sig}")
            self.is_running = False

        def schedule_signal_handler(sig):
            task = asyncio.create_task(signal_handler(sig))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

        for sig in stop_signals:
            loop.add_signal_handler(sig, schedule_signal_handler, sig)

        while self.is_running:
            await asyncio.sleep(1)


async def main():
    bot = VCMusicBot()
    await bot.start()
