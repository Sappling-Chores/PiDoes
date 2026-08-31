import sys
import os
import json
from datetime import datetime, timedelta
from functools import partial

from PySide6.QtWidgets import (
    QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QApplication, QWidget,
    QFrame, QLabel, QCheckBox, QPushButton
)
from PySide6.QtGui import QIcon, QPainter, QPen, QColor
from PySide6.QtCore import QSize, QByteArray, Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtSvg import QSvgRenderer

try:
    from textbox import TextBox
    from paths import TODO_QSS, TASK_JSON
except ImportError:
    from APP.textbox import TextBox
    from APP.paths import TODO_QSS, TASK_JSON


class TaskCard(QFrame):
    """
    One task row:
    - grows in height on hover
    - title enlarges + recolors on hover
    - checkbox on the left (done), star on the right (priority/important)
    """

    doneToggled = Signal(str, int, bool)      # day, task_id, done
    priorityToggled = Signal(str, int, bool)  # day, task_id, priority
    deleteRequested = Signal(str, int)        # day, task_id

    COLLAPSED_HEIGHT = 56
    EXPANDED_HEIGHT = 68
    ANIM_MS = 220

    def __init__(self, day, task_data, parent=None):
        super().__init__(parent)
        self.day = day
        self.task_data = task_data
        self._hovered = False

        self.setObjectName("card-body")
        self.setProperty("hovered", False)
        self.setAttribute(Qt.WA_Hover, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.setMinimumHeight(self.COLLAPSED_HEIGHT)
        self.setMaximumHeight(self.COLLAPSED_HEIGHT)

        self._build_ui()

        self._anim_min = QPropertyAnimation(self, b"minimumHeight")
        self._anim_max = QPropertyAnimation(self, b"maximumHeight")
        for anim in (self._anim_min, self._anim_max):
            anim.setDuration(self.ANIM_MS)
            anim.setEasingCurve(QEasingCurve.OutCubic)

    def _build_ui(self):
        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.setSpacing(10)

        self.check_box = QCheckBox()
        self.check_box.setObjectName("task-checkbox")
        self.check_box.setFixedSize(26, 26)
        self.check_box.setChecked(bool(self.task_data.get("done", False)))
        self.check_box.stateChanged.connect(self._on_done_changed)
        h_layout.addWidget(self.check_box)

        v_layout = QVBoxLayout()
        v_layout.setSpacing(2)

        self.task_label = QLabel(str(self.task_data.get("task", "")))
        self.task_label.setObjectName("task-label")
        self.task_label.setProperty("mode", "done" if self.task_data.get("done") else "active")
        v_layout.addWidget(self.task_label)

        self.schedule_label = QLabel(self._schedule_text())
        self.schedule_label.setObjectName("schedule-label")
        self.schedule_label.setProperty("mode", "done" if self.task_data.get("done") else "active")
        v_layout.addWidget(self.schedule_label)

        h_layout.addLayout(v_layout, 1)

        self.arrow_label = QLabel("→")
        self.arrow_label.setObjectName("hover-arrow")
        self.arrow_label.setVisible(False)
        h_layout.addWidget(self.arrow_label)

        self.star_button = QPushButton()
        self.star_button.setObjectName("star-button")
        self.star_button.setCheckable(True)
        is_prio = bool(self.task_data.get("priority", False) or self.task_data.get("important", False))
        self.star_button.setChecked(is_prio)
        self.star_button.setFixedSize(30, 30)
        self.star_button.setCursor(Qt.PointingHandCursor)
        self._sync_star_icon()
        self.star_button.toggled.connect(self._on_priority_changed)
        h_layout.addWidget(self.star_button)

        self.delete_button = QPushButton("✕")
        self.delete_button.setObjectName("delete-button")
        self.delete_button.setFixedSize(26, 26)
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setVisible(bool(self.task_data.get("done", False)))
        self.delete_button.clicked.connect(self._on_delete_clicked)
        h_layout.addWidget(self.delete_button)

    def _schedule_text(self):
        if "schedule_text_override" in self.task_data:
            return self.task_data["schedule_text_override"]
        date_val = self.task_data.get("date") or self.task_data.get("due_date") or []
        date_str = ""
        try:
            d, m, y = date_val
            date_str = f"{int(d):02d}/{int(m):02d}/{int(y)}"
        except (ValueError, TypeError):
            pass
        time_val = self.task_data.get("time") or self.task_data.get("due_time") or []
        time_str = ":".join(str(t) for t in time_val)
        return f"{date_str}  {time_str}".strip() if time_str else date_str

    def _sync_star_icon(self):
        self.star_button.setText("★" if self.star_button.isChecked() else "☆")

    def _on_done_changed(self, state):
        done = bool(state)
        mode = "done" if done else "active"
        for lbl in (self.task_label, self.schedule_label):
            lbl.setProperty("mode", mode)
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)
        self.delete_button.setVisible(done)
        self.doneToggled.emit(self.day, self.task_data.get("id"), done)

    def _on_delete_clicked(self):
        self.deleteRequested.emit(self.day, self.task_data.get("id"))

    def _on_priority_changed(self, checked):
        self._sync_star_icon()
        self.star_button.style().unpolish(self.star_button)
        self.star_button.style().polish(self.star_button)
        self.priorityToggled.emit(self.day, self.task_data.get("id"), checked)

    def enterEvent(self, event):
        self._hovered = True
        self._animate_to(self.EXPANDED_HEIGHT)
        self.arrow_label.setVisible(True)
        self._set_hovered_property(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._animate_to(self.COLLAPSED_HEIGHT)
        self.arrow_label.setVisible(False)
        self._set_hovered_property(False)
        super().leaveEvent(event)

    def _set_hovered_property(self, value):
        self.setProperty("hovered", value)
        self.style().unpolish(self)
        self.style().polish(self)
        for w in (self.task_label, self.schedule_label):
            w.style().unpolish(w)
            w.style().polish(w)
        self.update()

    def _animate_to(self, height):
        for anim, getter in (
            (self._anim_min, self.minimumHeight),
            (self._anim_max, self.maximumHeight),
        ):
            anim.stop()
            anim.setStartValue(getter())
            anim.setEndValue(height)
            anim.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._hovered:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#89b4fa"))
        pen.setWidth(2)
        painter.setPen(pen)
        size, margin = 14, 10
        w, h = self.width(), self.height()
        painter.drawLine(margin, margin, margin + size, margin)
        painter.drawLine(margin, margin, margin, margin + size)
        painter.drawLine(w - margin, h - margin, w - margin - size, h - margin)
        painter.drawLine(w - margin, h - margin, w - margin, h - margin - size)
        painter.end()


class ToDoCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do-Card")
        self.view_mode = "my_day"
        self._load_stylesheet()
        self._json_path = self._find_task_json()

        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setSpacing(12)
        self.refresh_tasks()

        self.add_bar = TextBox()
        self.add_bar.task_added.connect(self.refresh_tasks)

        outermost_layout = QVBoxLayout()
        outermost_layout.addLayout(self.tasks_layout)
        outermost_layout.addWidget(self.add_bar)
        self.setLayout(outermost_layout)

    def set_view_mode(self, mode: str):
        self.view_mode = mode
        self.refresh_tasks()

    def refresh_tasks(self):
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        day, tasks = self.fetch_task()

        if self.view_mode == "old_tasks":
            last_week_tasks = []
            older_tasks = []
            now = datetime.now()

            def parse_task_date(date_val):
                if isinstance(date_val, list):
                    if len(date_val) == 3 and all(isinstance(x, int) for x in date_val):
                        try:
                            return datetime(date_val[2], date_val[1], date_val[0])
                        except ValueError:
                            pass
                    if len(date_val) >= 2:
                        date_val = date_val[1]
                    elif len(date_val) == 1:
                        date_val = date_val[0]
                    else:
                        return None
                if not isinstance(date_val, str):
                    return None
                date_val = date_val.strip()
                try:
                    return datetime.strptime(date_val, "%Y-%m-%d")
                except ValueError:
                    pass
                try:
                    return datetime.strptime(date_val, "%d %B, %Y")
                except ValueError:
                    pass
                return None

            for task_data in tasks:
                orig_date = task_data.get("_original_date_val")
                dt = parse_task_date(orig_date)
                if dt:
                    days_diff = (now - dt).days
                    if days_diff <= 7:
                        last_week_tasks.append(task_data)
                    else:
                        older_tasks.append(task_data)
                else:
                    older_tasks.append(task_data)

            if last_week_tasks:
                self.tasks_layout.addWidget(self.create_section_header("Last Week"))
                for task_data in last_week_tasks:
                    self._add_task_card(day, task_data)

            if older_tasks:
                self.tasks_layout.addWidget(self.create_section_header("Older"))
                for task_data in older_tasks:
                    self._add_task_card(day, task_data)
        else:
            for task_data in tasks:
                self._add_task_card(day, task_data)

    def _add_task_card(self, day, task_data):
        card = TaskCard(task_data.get("_day_key", day), task_data)
        card.doneToggled.connect(self._on_done_toggled)
        card.priorityToggled.connect(self._on_priority_toggled)
        card.deleteRequested.connect(self._on_delete_requested)

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(card)
        self.tasks_layout.addLayout(outer_layout)

    def create_section_header(self, text):
        label = QLabel(text)
        label.setObjectName("section-header")
        label.setStyleSheet("""
            QLabel#section-header {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
                color: #555555;
                padding: 12px 16px 4px 16px;
                background: transparent;
            }
        """)
        return label

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _load_stylesheet(self):
        if TODO_QSS.exists():
            with open(TODO_QSS, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _find_task_json(self):
        if TASK_JSON.exists():
            return TASK_JSON
        possible_paths = [
            "task.json",
            os.path.join("APP", "task.json"),
            os.path.join(os.path.dirname(__file__), "task.json"),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p
        print("error: task.json not found")
        return None

    def fetch_task(self):
        """Returns (day_name, list_of_tasks) for today or filtered view, matching the
        structure in task.json."""
        day = datetime.now().strftime("%A")
        if not self._json_path:
            return day, []
        try:
            with open(self._json_path, "r", encoding="utf-8") as f:
                file_content = json.load(f)

            if self.view_mode == "important":
                important_tasks = []
                task_root = file_content.get("task", {})
                if isinstance(task_root, dict):
                    for day_key, task_list in task_root.items():
                        if isinstance(task_list, list):
                            for task in task_list:
                                if task.get("priority", False) or task.get("important", False):
                                    task_copy = dict(task)
                                    task_copy["_day_key"] = day_key
                                    important_tasks.append(task_copy)
                return "Important", important_tasks

            elif self.view_mode in ("old_tasks", "last_week", "older"):
                old_tasks = []
                incomplete = file_content.get("incomplete_task", [])
                if isinstance(incomplete, list):
                    for idx, item in enumerate(incomplete):
                        if isinstance(item, list) and len(item) >= 2:
                            task_name = item[0]
                            date_val = item[1]
                            if isinstance(date_val, list):
                                schedule_str = "  ".join(str(x) for x in date_val)
                            else:
                                schedule_str = str(date_val)

                            task_dict = {
                                "id": idx,
                                "task": task_name,
                                "done": False,
                                "priority": False,
                                "schedule_text_override": schedule_str,
                                "_day_key": "incomplete_task",
                                "_original_date_val": date_val
                            }

                            if self.view_mode == "old_tasks":
                                old_tasks.append(task_dict)
                            else:
                                now = datetime.now()
                                dt = None
                                if isinstance(date_val, list) and len(date_val) == 3 and all(isinstance(x, int) for x in date_val):
                                    try:
                                        dt = datetime(date_val[2], date_val[1], date_val[0])
                                    except ValueError:
                                        pass
                                days_diff = (now - dt).days if dt else 999
                                if self.view_mode == "last_week" and days_diff <= 7:
                                    old_tasks.append(task_dict)
                                elif self.view_mode == "older" and days_diff > 7:
                                    old_tasks.append(task_dict)

                title_map = {
                    "old_tasks": "Old Tasks",
                    "last_week": "Last Week Tasks",
                    "older": "Older Tasks"
                }
                return title_map[self.view_mode], old_tasks

            else:
                task_root = file_content.get("task", {})
                if isinstance(task_root, dict):
                    tasks = task_root.get(day, [])
                    if isinstance(tasks, list):
                        # Sort so that priority (important) tasks come first (True before False)
                        tasks = sorted(tasks, key=lambda x: not (x.get("priority", False) or x.get("important", False)))
                    return day, tasks
                if isinstance(task_root, list):
                    task_root = sorted(task_root, key=lambda x: not (x.get("priority", False) or x.get("important", False)))
                return day, task_root
        except Exception as e:
            print(f"error reading task.json: {e}")
            return day, []

    def _update_task_field(self, day, task_id, field, value):
        if not self._json_path or task_id is None:
            return
        try:
            with open(self._json_path, "r", encoding="utf-8") as f:
                file_content = json.load(f)

            if day == "incomplete_task":
                if field == "done" and value:
                    incomplete = file_content.get("incomplete_task", [])
                    if 0 <= task_id < len(incomplete):
                        incomplete.pop(task_id)
            else:
                task_root = file_content.get("task", {})
                if isinstance(task_root, dict):
                    day_tasks = task_root.get(day, [])
                    for t in day_tasks:
                        if t.get("id") == task_id:
                            t[field] = value
                            if field in ("priority", "important"):
                                t["priority"] = value
                                t["important"] = value
                            break

            with open(self._json_path, "w", encoding="utf-8") as f:
                json.dump(file_content, f, indent=2)
        except Exception as e:
            print(f"error updating task.json: {e}")

    def _on_done_toggled(self, day, task_id, done):
        self._update_task_field(day, task_id, "done", done)
        if day == "incomplete_task" or self.view_mode == "important":
            self.refresh_tasks()

    def _on_priority_toggled(self, day, task_id, priority):
        self._update_task_field(day, task_id, "priority", priority)
        self.refresh_tasks()

    def _on_delete_requested(self, day, task_id):
        self._remove_task(day, task_id)
        self.refresh_tasks()

    def _remove_task(self, day, task_id):
        if not self._json_path or task_id is None:
            return
        try:
            with open(self._json_path, "r", encoding="utf-8") as f:
                file_content = json.load(f)
            task_root = file_content.get("task", {})
            if isinstance(task_root, dict):
                for d_key, day_tasks in task_root.items():
                    if isinstance(day_tasks, list):
                        file_content["task"][d_key] = [t for t in day_tasks if t.get("id") != task_id]
            with open(self._json_path, "w", encoding="utf-8") as f:
                json.dump(file_content, f, indent=2)
        except Exception as e:
            print(f"error removing task from task.json: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ToDoCard()
    widget.show()
    app.exec()