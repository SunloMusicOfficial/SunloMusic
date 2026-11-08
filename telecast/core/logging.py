# Copyright (C) @itsSmartDev

import logging
import sys
import os
from SunloMusic.core.config import Config

class FilteredStderr:
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self._pending = []
        self.suppress_next = False

    def write(self, text):
        if any(err in text for err in ["CHANNEL_INVALID", "ID not found", "USER_NOT_PARTICIPANT", "PermissionError"]):
            self.suppress_next = True
            return

        if self.suppress_next and any(marker in text for marker in ["Traceback", "File ", "raise ", "During handling"]):
            return

        if text.strip() == "":
            self.suppress_next = False

        self.original_stderr.write(text)

    def flush(self):
        self.original_stderr.flush()

    def isatty(self):
        return False

    def fileno(self):
        return self.original_stderr.fileno()

    @property
    def encoding(self):
        return getattr(self.original_stderr, "encoding", None) or "utf-8"

sys.stderr = FilteredStderr(sys.stderr)

def setup_logger():
    logger = logging.getLogger("VCBot")
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, Config.LOG_LEVEL))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    file_handler = logging.FileHandler(f"{Config.LOGS_DIR}/bot.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
