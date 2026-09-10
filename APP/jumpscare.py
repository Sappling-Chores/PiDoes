import sys
import random
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QHBoxLayout
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import Qt, QTimer, QUrl, QObject
from PySide6.QtGui import QPixmap

try:
  from paths import SCARY_IMAGE, JUMPSCARE_SOUND
  import task_manager
except ImportError:
  from APP.paths import SCARY_IMAGE, JUMPSCARE_SOUND
  import APP.task_manager as task_manager


class JumpscareWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Scary")
    self.frame = QFrame()
    self.setWindowFlag(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    self.frame.setStyleSheet(
      """
      QFrame{
        background:black;
      }
      """
    )
    h_layout = QHBoxLayout(self.frame)
    label = QLabel()
    if SCARY_IMAGE and Path(SCARY_IMAGE).exists():
      pixmap = QPixmap(str(SCARY_IMAGE))
      scaled = pixmap.scaled(
        self.size(),
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
      )
      label.setPixmap(scaled)
    label.setStyleSheet(
      """
      QLabel{
        background: #000000;
      }
      """
    )

    h_layout.addStretch(1)
    h_layout.addWidget(label)
    h_layout.addStretch(1)
    self.setCentralWidget(self.frame)

    self.sound = QSoundEffect()
    if JUMPSCARE_SOUND and Path(JUMPSCARE_SOUND).exists():
      self.sound.setSource(QUrl.fromLocalFile(str(JUMPSCARE_SOUND)))
      self.sound.setVolume(1)
      self.sound.play()
    QTimer.singleShot(3000, self.close)

  def close_jumpscare(self):
    self.sound.stop()
    self.close()
    self.deleteLater()


class JumpscareManager(QObject):
  def __init__(self, min_delay_sec=30, max_delay_sec=300, cooldown_sec=600, parent=None):
    super().__init__(parent)
    self.min_delay_sec = min_delay_sec
    self.max_delay_sec = max_delay_sec
    self.cooldown_sec = cooldown_sec

    self.last_scare_time: datetime | None = None
    self.is_scheduled = False

    self.check_timer = QTimer(self)
    self.check_timer.timeout.connect(self._check_overdue_important_tasks)

  def start(self):
    self.check_timer.start(30_000)
    self._check_overdue_important_tasks()

  def stop(self):
    self.check_timer.stop()

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

  def _check_overdue_important_tasks(self):
    if self.is_scheduled:
      return

    if self.last_scare_time:
      elapsed = (datetime.now() - self.last_scare_time).total_seconds()
      if elapsed < self.cooldown_sec:
        return

    task_data = task_manager.load_task_data()
    task_root = task_data.get("task", {})

    has_overdue_important = False
    if isinstance(task_root, dict):
      for day_key, task_list in task_root.items():
        if isinstance(task_list, list):
          for task in task_list:
            if self._is_task_overdue(task):
              has_overdue_important = True
              break
        if has_overdue_important:
          break

    if has_overdue_important:
      random_delay_ms = random.randint(self.min_delay_sec, self.max_delay_sec) * 1000
      self.is_scheduled = True
      QTimer.singleShot(random_delay_ms, self._trigger_jumpscare)

  def _trigger_jumpscare(self):
    self.is_scheduled = False
    self.last_scare_time = datetime.now()

    self.scare_window = JumpscareWindow()
    self.scare_window.showFullScreen()
    self.scare_window.show()


if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = JumpscareWindow()
  window.showFullScreen()
  window.show()
  app.exec()