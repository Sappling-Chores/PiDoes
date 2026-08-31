# paths.py
import sys
import os
from pathlib import Path

def get_base_path() -> Path:
    """Handles both dev mode and PyInstaller-frozen .exe."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

BASE_DIR   = get_base_path()
ASSETS_DIR = BASE_DIR / "assets"
AUDIOS_DIR = ASSETS_DIR / "Audios"

# Stylesheets
BANNER_QSS  = BASE_DIR / "banner.qss"
TODO_QSS    = BASE_DIR / "to-do.qss"
SETTING_QSS = BASE_DIR / "setting.qss"

# Icons / SVGs
APP_ICON       = ASSETS_DIR / "Pi-icon.png"
DOTS_THREE_SVG = ASSETS_DIR / "dots-three.svg"
GEAR_SVG       = ASSETS_DIR / "gear-six-fill.svg"
ARROW_LEFT_SVG = ASSETS_DIR / "arrow-left-bold.svg"
TICK_PNG       = ASSETS_DIR / "tick.png"
STAR_SVG       = ASSETS_DIR / "star.svg"
GHOST_PNG      = ASSETS_DIR / "ghost.png"
SUN_SVG        = ASSETS_DIR / "sun.svg"
NOTEPAD_SVG    = ASSETS_DIR / "notepad.svg"

# Data files (local, bundled with the app)
URLS_JSON    = BASE_DIR / "urls.json"
TASK_JSON    = BASE_DIR / "task.json"
DATA_DIR     = BASE_DIR / "Data"
SETTING_JSON = DATA_DIR / "setting.json"

# Audio
COMPLETION_SOUND = AUDIOS_DIR / "completion_sound.mp3"
JUMPSCARE_SOUND  = AUDIOS_DIR / "jumpscare_sound.wav"

# App-data (user-specific, persisted outside the install dir)
APP_DATA_DIR  = Path(os.getenv("APPDATA", "")) / "PiDos"
TASKS_FILE    = APP_DATA_DIR / "tasks.json"
SETTINGS_FILE = APP_DATA_DIR / "settings.json"