import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("scripts/bot.log", maxBytes=5000000, backupCount=10),
        logging.StreamHandler()
    ]
)

LOGGER = logging.getLogger("SunloMusic")
