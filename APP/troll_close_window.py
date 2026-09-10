import sys
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Set, List

import win32gui
import win32process
import win32api
import win32con
import psutil

from PySide6.QtCore import QThread, Signal, QObject, QTimer

try:
  from paths import SETTINGS_FILE, BLACK_LISTED_WINDOW_FILE
  import data_manager
  import task_manager
  import jumpscare
except ImportError:
  from APP.paths import SETTINGS_FILE, BLACK_LISTED_WINDOW_FILE
  import APP.data_manager as data_manager
  import APP.task_manager as task_manager
  import APP.jumpscare as jumpscare


DEFAULT_WHITELIST: Set[str] = {
  "pidos.exe",
  "python.exe",
  "pythonw.exe",
  "code.exe",
  "explorer.exe",
  "searchhost.exe",
  "taskmgr.exe"
}

BROWSERS: Set[str] = {
  "chrome.exe",
  "msedge.exe",
  "firefox.exe",
  "brave.exe",
  "opera.exe"
}

DEFAULT_BLACK_LISTED_URLS: List[str] = [
  "youtube",
  "reddit",
  "instagram",
  "twitter",
  "x.com",
  "netflix",
  "facebook",
  "tiktok",
  "twitch"
]


def close_active_tab(hwnd):
  try:
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.05)
    win32api.keybd_event(0x11, 0, 0, 0)
    win32api.keybd_event(0x57, 0, 0, 0)
    win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
  except Exception as e:
    print(f"[troll_close_window] Error closing tab: {e}")


def close_window(hwnd):
  try:
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
  except Exception as e:
    print(f"[troll_close_window] Error closing window: {e}")


class TrollWindowMonitor(QThread):
  tab_closed_signal = Signal(str, str)

  def __init__(self, check_interval_sec: float = 1.5, min_delay_sec=1, max_delay_sec=10, cooldown_sec=60, parent=None):
    super().__init__(parent)
    self.check_interval = check_interval_sec
    self.min_delay_sec = min_delay_sec
    self.max_delay_sec = max_delay_sec
    self.cooldown_sec = cooldown_sec
    self.is_running = True

    self.last_scare_time: datetime | None = None
    self.is_scare_scheduled = False
    self.scare_window = None

  def _is_troll_mode_enabled(self) -> bool:
    settings = data_manager.fetch_settings()
    if isinstance(settings, dict):
      mode_cfg = settings.get("mode", {})
      if isinstance(mode_cfg, dict):
        return mode_cfg.get("troll_mode", False)
    return False

  def _is_task_overdue(self, task: dict) -> bool:
    if task.get("done", False):
      return False

    is_important = bool(task.get("important", False) or task.get("priority", False))
    if not is_important:
      return False

    date_val = task.get("date")
    if not date_val or not isinstance(date_val, list) or len(date_val) != 3:
      return False

    day, month, year = date_val
    time_val = task.get("time") or [23, 59]
    hour = time_val[0] if len(time_val) >= 1 else 23
    minute = time_val[1] if len(time_val) >= 2 else 59

    try:
      due_datetime = datetime(year, month, day, hour, minute)
      return datetime.now() > due_datetime
    except ValueError:
      return False

  def _has_overdue_important_tasks(self) -> bool:
    task_data = task_manager.load_task_data()
    task_root = task_data.get("task", {})
    if isinstance(task_root, dict):
      for day_key, task_list in task_root.items():
        if isinstance(task_list, list):
          for task in task_list:
            if self._is_task_overdue(task):
              return True
    return False

  def _trigger_jumpscare_with_random_delay(self):
    if self.is_scare_scheduled:
      return

    if self.last_scare_time:
      elapsed = (datetime.now() - self.last_scare_time).total_seconds()
      if elapsed < self.cooldown_sec:
        return

    random_delay_ms = random.randint(self.min_delay_sec, self.max_delay_sec) * 1000
    self.is_scare_scheduled = True
    QTimer.singleShot(random_delay_ms, self._fire_jumpscare)

  def _fire_jumpscare(self):
    self.is_scare_scheduled = False
    self.last_scare_time = datetime.now()
    self.scare_window = jumpscare.trigger_jumpscare()

  def run(self):
    while self.is_running:
      try:
        if self._is_troll_mode_enabled():
          hwnd = win32gui.GetForegroundWindow()
          if hwnd and win32gui.IsWindow(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid > 4:
              proc_name = psutil.Process(pid).name().lower()
              window_title = win32gui.GetWindowText(hwnd).lower()

              black_list_data = data_manager.fetch_black_listed_window() or {}
              black_listed_apps = black_list_data.get("black_listed_apps", [])
              black_listed_urls = black_list_data.get("black_listed_urls", DEFAULT_BLACK_LISTED_URLS)

              action_taken = False
              if proc_name in BROWSERS:
                for kw in black_listed_urls:
                  if kw.lower() in window_title:
                    close_active_tab(hwnd)
                    self.tab_closed_signal.emit(proc_name, kw)
                    action_taken = True
                    break
              elif proc_name in [app.lower() for app in black_listed_apps] or (proc_name not in DEFAULT_WHITELIST and proc_name not in BROWSERS):
                close_window(hwnd)
                self.tab_closed_signal.emit(proc_name, window_title)
                action_taken = True

              if action_taken and self._has_overdue_important_tasks():
                self._trigger_jumpscare_with_random_delay()

      except Exception as e:
        pass

      time.sleep(self.check_interval)

  def stop(self):
    self.is_running = False
    self.wait()