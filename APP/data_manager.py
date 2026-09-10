import json
from pathlib import Path
import requests
from dotenv import load_dotenv
import os

try:
  from paths import TASKS_FILE, SETTINGS_FILE, SETTING_JSON, WALLPAPER_URLS_JSON, BLACK_LISTED_WINDOW_FILE, BLACK_LISTED_WINDOW_JSON
  import task_manager
except ImportError:
  from APP.paths import TASKS_FILE, SETTINGS_FILE, SETTING_JSON, WALLPAPER_URLS_JSON, BLACK_LISTED_WINDOW_FILE, BLACK_LISTED_WINDOW_JSON
  import APP.task_manager as task_manager

try:
  load_dotenv()
  PIDOES_WALLPAPER_API_URL = os.getenv("PIDOES_WALLPAPER_API_URL")
except Exception:
  PIDOES_WALLPAPER_API_URL = None


def fetch_task():
  return task_manager.load_task_data()


def fetch_settings(category="all", key="all"):
  setting_file_path = Path(SETTINGS_FILE)
  try:
    if setting_file_path.exists():
      with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    elif SETTING_JSON and Path(SETTING_JSON).exists():
      with open(SETTING_JSON, "r", encoding="utf-8") as f:
        return json.load(f)
  except Exception as e:
    print(f"[data_manager] fetch_settings error: {e}")
  return None


def fetch_wallpaper_urls():
  if PIDOES_WALLPAPER_API_URL:
    try:
      response = requests.get(PIDOES_WALLPAPER_API_URL, timeout=10)
      response.raise_for_status()
      data = response.json()
      categories = ["desktop-wallpaper", "nature", "japan", "space", "technology", "city-skyline", "3d-renders"]
      wallpapers = {}
      api_wallpapers = data.get("wallpapers", {})
      for category in categories:
        item = api_wallpapers.get(category)
        if isinstance(item, list):
          urls = []
          for sub_item in item:
            if isinstance(sub_item, dict) and "image_url" in sub_item:
              urls.append(sub_item["image_url"])
            elif isinstance(sub_item, str):
              urls.append(sub_item)
          wallpapers[category] = urls
        elif isinstance(item, dict):
          wallpapers[category] = item.get("image_url", "")
        elif isinstance(item, str):
          wallpapers[category] = item
      Path(WALLPAPER_URLS_JSON).parent.mkdir(parents=True, exist_ok=True)
      with open(WALLPAPER_URLS_JSON, "w", encoding="utf-8") as f:
        json.dump({"wallpapers": wallpapers}, f, indent=2)
    except requests.RequestException as e:
      print(f"[data_manager] Request failed: {e}")


def read_wallpaper(category=None):
  if Path(WALLPAPER_URLS_JSON).exists():
    try:
      with open(WALLPAPER_URLS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
        wallpapers = data.get("wallpapers", {})
        if category:
          return wallpapers.get(category)
        return wallpapers
    except Exception as e:
      print(f"[data_manager] read_wallpaper error: {e}")
  return None


def write_tasks(data):
  task_manager.save_task_data(data)


def write_settings(data):
  setting_file_path = Path(SETTINGS_FILE)
  try:
    setting_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(setting_file_path, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2)
  except Exception as e:
    print(f"[data_manager] write_settings error: {e}")


def fetch_black_listed_window():
  black_listed_window_file = Path(BLACK_LISTED_WINDOW_FILE)
  try:
    if black_listed_window_file.exists():
      with open(black_listed_window_file, "r", encoding="utf-8") as f:
        return json.load(f)
    elif BLACK_LISTED_WINDOW_JSON and Path(BLACK_LISTED_WINDOW_JSON).exists():
      with open(BLACK_LISTED_WINDOW_JSON, "r", encoding="utf-8") as f:
        return json.load(f)
  except Exception as e:
    print(f"[data_manager] fetch_black_listed_window error: {e}")
  return None


if __name__ == "__main__":
  print(fetch_settings())
  
  