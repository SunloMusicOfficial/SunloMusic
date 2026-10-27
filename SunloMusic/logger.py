import logging
import sys
from pyfiglet import figlet_format

LOGGER = logging.getLogger("SunloMusic")
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

if not LOGGER.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(
        "\x1b[36m%(asctime)s\x1b[0m │ \x1b[33m%(levelname)-8s\x1b[0m │ %(message)s",
        datefmt="%H:%M:%S"
    ))
    LOGGER.addHandler(_handler)

def print_banner():
    banner = figlet_format("SunloMusic", font="slant")
    print(f"\x1b[95m{banner}\x1b[0m")
    print("\x1b[96m" + "═" * 60 + "\x1b[0m")
    print("\x1b[92m   🎶 Premium Telegram VC Music Bot\x1b[0m")
    print("\x1b[93m   Author: Sakil  |  @YO_UR_OFFICIAL_CRUSH\x1b[0m")
    print("\x1b[94m   Channel: https://t.me/Vip_Sakil_Bio\x1b[0m")
    print("\x1b[96m" + "═" * 60 + "\x1b[0m\n")
