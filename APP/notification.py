import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu
from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QIcon, QAction

try:
    from winotify import Notification, audio
except ImportError:
    Notification = None
    audio = None

try:
    from paths import APP_ICON, TASK_JSON, SETTING_JSON
except ImportError:
    from APP.paths import APP_ICON, TASK_JSON, SETTING_JSON

NEAR_DUE_WINDOW = timedelta(minutes=30)
OVERDUE_NOTIFICATION_INTERVAL = timedelta(hours=1)
CHECK_INTERVAL_MS = 30_000


class NotificationManager(QObject):
    task_action = Signal(int, str)

    def __init__(self, tasks=None, main_window=None, parent=None):
        super().__init__(parent)
        self.tasks = tasks
        self.main_window = main_window
        self.last_overdue_notification_time: datetime | None = None
        self._notified_soon_ids: set = set()

        if APP_ICON and Path(APP_ICON).exists():
            self.tray_icon = QSystemTrayIcon(QIcon(str(APP_ICON)))
        else:
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("dialog-information"))
        self.tray_icon.setToolTip("Pi-Dos")

        menu = QMenu()
        open_action = QAction("Open Pi-Dos", triggered=self._on_open)
        quit_action = QAction("Quit", triggered=self._on_quit)
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_due_tasks)

    def start(self):
        self.timer.start(CHECK_INTERVAL_MS)
        self.check_due_tasks()

    def stop(self):
        self.timer.stop()

    def _is_notification_allowed(self) -> bool:
        if SETTING_JSON and Path(SETTING_JSON).exists():
            try:
                with open(SETTING_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("notification", {}).get("allow_notification", True)
            except Exception:
                pass
        return True

    def _load_tasks(self) -> list[dict]:
        if self.tasks is not None:
            return self.tasks

        if not TASK_JSON or not Path(TASK_JSON).exists():
            return []

        task_list = []
        try:
            with open(TASK_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            task_root = data.get("task", {})
            if isinstance(task_root, dict):
                for _, day_tasks in task_root.items():
                    if isinstance(day_tasks, list):
                        task_list.extend(day_tasks)
            elif isinstance(task_root, list):
                task_list.extend(task_root)
        except Exception as e:
            print(f"[notification] Error reading task.json: {e}")

        return task_list

    def _get_due_datetime(self, task: dict) -> datetime | None:
        if isinstance(task.get("due_time"), datetime):
            return task["due_time"]

        date_val = task.get("due_date") or task.get("date")
        if not date_val or not isinstance(date_val, (list, tuple)) or len(date_val) < 3:
            return None

        try:
            if date_val[2] > 1000:
                day, month, year = int(date_val[0]), int(date_val[1]), int(date_val[2])
            else:
                year, month, day = int(date_val[0]), int(date_val[1]), int(date_val[2])
        except (ValueError, TypeError):
            return None

        time_val = task.get("due_time") or task.get("time") or []
        hour, minute = 23, 59
        if isinstance(time_val, (list, tuple)) and len(time_val) >= 2:
            try:
                hour, minute = int(time_val[0]), int(time_val[1])
            except (ValueError, TypeError):
                pass

        try:
            return datetime(year, month, day, hour, minute)
        except ValueError:
            return None

    def check_due_tasks(self):
        if not self._is_notification_allowed():
            return

        now = datetime.now()
        tasks = self._load_tasks()
        overdue_tasks = []

        for task in tasks:
            if task.get("done", False):
                continue

            due_dt = self._get_due_datetime(task)
            if not due_dt:
                continue

            task_id = task.get("id")
            task_title = task.get("title") or task.get("task", "Untitled Task")

            if due_dt < now:
                overdue_tasks.append((task_id, task_title, due_dt))

            elif now <= due_dt <= now + NEAR_DUE_WINDOW:
                notified = task.get("notified_soon", False) or (task_id in self._notified_soon_ids if task_id else False)
                if not notified:
                    self._fire_toast(
                        title="Task Due Soon",
                        body=f'"{task_title}" is due at {due_dt.strftime("%H:%M")}',
                    )
                    task["notified_soon"] = True
                    if task_id is not None:
                        self._notified_soon_ids.add(task_id)

        if overdue_tasks:
            should_notify = False
            if self.last_overdue_notification_time is None:
                should_notify = True
            elif now - self.last_overdue_notification_time >= OVERDUE_NOTIFICATION_INTERVAL:
                should_notify = True

            if should_notify:
                self._notify_overdue_batch(overdue_tasks)
                self.last_overdue_notification_time = now
        else:
            self.last_overdue_notification_time = None

    def _notify_overdue_batch(self, overdue_tasks: list[tuple]):
        count = len(overdue_tasks)
        if count == 1:
            _, title, due_dt = overdue_tasks[0]
            toast_title = "Task Overdue!"
            toast_body = f'"{title}" was due at {due_dt.strftime("%H:%M")}'
        else:
            toast_title = f"Overdue Tasks ({count})"
            preview_items = [f"• {title}" for _, title, _ in overdue_tasks[:4]]
            if count > 4:
                preview_items.append(f"+ {count - 4} more")
            toast_body = "\n".join(preview_items)

        self._fire_toast(title=toast_title, body=toast_body)

    def _fire_toast(self, title: str, body: str):
        if not Notification:
            print(f"[notification] winotify not installed. {title}: {body}")
            return
        try:
            toast = Notification(
                app_id="Pi-Dos",
                title=title,
                msg=body,
                duration="short",
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            print(f"[notification] {title}: {body}")
        except Exception as e:
            print(f"[notification] Failed to show toast: {e}")

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._on_open()

    def _on_open(self):
        if self.main_window:
            self.main_window.showNormal()
            self.main_window.activateWindow()
            self.main_window.raise_()
        print("[tray] Open clicked")

    def _on_quit(self):
        self.stop()
        QApplication.instance().quit()


class DemoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi-Dos (Notification Demo)")
        self.resize(400, 200)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        print("[window] closed -> hidden to tray (app still running)")


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = DemoMainWindow()
    window.show()

    notifier = NotificationManager()
    notifier.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
