import sys
import os
import ctypes

try:
  ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PiDos.App.1.0")
except Exception:
  pass

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

try:
  from window import MainWindow
  from notification import NotificationManager
  from troll_close_window import TrollWindowMonitor
  from paths import APP_ICON
except ImportError:
  from APP.window import MainWindow
  from APP.notification import NotificationManager
  from APP.troll_close_window import TrollWindowMonitor
  from APP.paths import APP_ICON


def main():
  app = QApplication(sys.argv)
  app.setQuitOnLastWindowClosed(False)

  if APP_ICON and APP_ICON.exists():
    app.setWindowIcon(QIcon(str(APP_ICON)))

  window = MainWindow()
  window.show()

  notifier = NotificationManager(main_window=window)
  notifier.start()

  troll_monitor = TrollWindowMonitor()
  troll_monitor.start()

  exit_code = app.exec()
  notifier.stop()
  troll_monitor.stop()
  sys.exit(exit_code)


if __name__ == "__main__":
  main()
