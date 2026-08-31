import sys
import os
import ctypes

# Set AppUserModelID on Windows for PyInstaller .exe taskbar & toast notification support
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PiDos.App.1.0")
except Exception:
    pass

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

try:
    from window import MainWindow
    from notification import NotificationManager
    from paths import APP_ICON
except ImportError:
    from APP.window import MainWindow
    from APP.notification import NotificationManager
    from APP.paths import APP_ICON


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray when window is closed

    if APP_ICON and APP_ICON.exists():
        app.setWindowIcon(QIcon(str(APP_ICON)))

    window = MainWindow()
    window.show()

    # Start background notification manager attached to main window and tray
    notifier = NotificationManager(main_window=window)
    notifier.start()

    exit_code = app.exec()
    notifier.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
