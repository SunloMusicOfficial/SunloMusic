# Copyright (C) @YO_UR_OFFICIAL_CRUSH

import asyncio
import threading
import time

from sunlomusic.core.logging import logger


class LoopWatchdog:

    def __init__(self, interval: float = 1.0, threshold: float = 5.0, on_stall=None):
        self.interval = interval
        self.threshold = threshold
        self._on_stall = on_stall
        self._loop = None
        self._last_beat = time.monotonic()
        self._heartbeat_task = None
        self._thread = None
        self._stop = threading.Event()
        self._stall_logged = False

    async def _heartbeat(self):
        try:
            while True:
                self._last_beat = time.monotonic()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass

    def _watch(self):
        while not self._stop.wait(self.interval):
            blocked_for = time.monotonic() - self._last_beat
            if blocked_for > self.threshold:
                if not self._stall_logged:
                    logger.error(
                        f"Event loop blocked for {blocked_for:.1f}s — the bot is "
                        f"unresponsive. This indicates a stalled/blocking call; "
                        f"playback ops are timeout-guarded, so check for native or "
                        f"synchronous blocking work."
                    )
                    self._stall_logged = True
                    if self._on_stall:
                        try:
                            self._on_stall(blocked_for)
                        except Exception:
                            pass
            elif self._stall_logged:
                logger.info(f"Event loop recovered after stall ({blocked_for:.1f}s behind)")
                self._stall_logged = False

    def start(self):
        self._loop = asyncio.get_running_loop()
        self._loop.slow_callback_duration = max(self._loop.slow_callback_duration, self.threshold)
        self._last_beat = time.monotonic()
        self._heartbeat_task = asyncio.create_task(self._heartbeat())
        self._thread = threading.Thread(target=self._watch, name="loop-watchdog", daemon=True)
        self._thread.start()
        logger.info(
            f"Loop watchdog started (interval={self.interval}s, threshold={self.threshold}s)"
        )

    def stop(self):
        self._stop.set()
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
        logger.info("Loop watchdog stopped")
