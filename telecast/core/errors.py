# Copyright (C) @itsSmartDev

class StreamOperationTimeout(Exception):
    pass


class FloodWaitError(Exception):
    def __init__(self, wait_seconds: int):
        self.wait_seconds = wait_seconds
        super().__init__(f"FLOOD_WAIT_{wait_seconds}")


class TelegramServerError(Exception):
    pass
