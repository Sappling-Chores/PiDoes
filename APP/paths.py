# paths.py
import sys
import os
from pathlib import Path

def get_base_path() -> Path:
    """Handles both dev mode and PyInstaller-frozen .exe."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

BASE_DIR = get_base_path()
ASSETS_DIR = BASE_DIR / "assets"
ICON_PATH = ASSETS_DIR / "icons" / "app.ico"

# For writable data (tasks, settings, logs) — NOT inside the bundle,
# use a proper user-writable location instead:
APP_DATA_DIR = Path(os.getenv("APPDATA")) / "PiDos"
TASKS_FILE = APP_DATA_DIR / "tasks.json"
SETTINGS_FILE = APP_DATA_DIR / "settings.json"