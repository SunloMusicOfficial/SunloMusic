import os
from importlib import import_module
from SunloMusic.logger import LOGGER

def load_plugins():
    for file in sorted(os.listdir(os.path.dirname(__file__))):
        if file.endswith(".py") and not file.startswith("_"):
            try:
                import_module(f"SunloMusic.plugins.{file[:-3]}")
                LOGGER.info(f"🔌 Loaded: {file}")
            except Exception as e: LOGGER.error(f"❌ Failed {file}: {e}")
