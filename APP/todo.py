import sys
import os
import json
from datetime import datetime
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
except ImportError:
    from APP.textbox import TextBox


class TaskCard(QFrame):
    """
    One task row, styled to mirror the React CategoryList item:
    - grows in height on hover (QPropertyAnimation, since QSS can't animate size)
    - shows corner brackets on hover (hand-painted, since QSS has no ::before/::after)
    - title enlarges + recolors on hover, driven by the 'hovered' dynamic property in QSS
    - checkbox on the left (done), star on the right (priority)
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
        self.setAttribute(Qt.WA_StyledBackground, True)  # let QSS rgba background paint through
        self.setMouseTracking(True)
        self.setMinimumHeight(self.COLLAPSED_HEIGHT)
        self.setMaximumHeight(self.COLLAPSED_HEIGHT)

        self._build_ui()

        self._anim_min = QPropertyAnimation(self, b"minimumHeight")
        self._anim_max = QPropertyAnimation(self, b"maximumHeight")
        for anim in (self._anim_min, self._anim_max):
            anim.setDuration(self.ANIM_MS)
            anim.setEasingCurve(QEasingCurve.OutCubic)

    # ---------- UI ----------

    def _build_ui(self):
        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.setSpacing(10)

        self.check_box = QCheckBox()
        self.check_box.setObjectName("task-checkbox")
        self.check_box.setFixedSize(26, 26)  # square + roomy, so the indicator isn't clipped
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

        # Appears only on hover, mirrors the arrow icon in the React card
        self.arrow_label = QLabel("→")
        self.arrow_label.setObjectName("hover-arrow")
        self.arrow_label.setVisible(False)
        h_layout.addWidget(self.arrow_label)

        self.star_button = QPushButton()
        self.star_button.setObjectName("star-button")
        self.star_button.setCheckable(True)
        self.star_button.setChecked(bool(self.task_data.get("priority", False)))
        self.star_button.setFixedSize(30, 30)
        self.star_button.setCursor(Qt.PointingHandCursor)
        self._sync_star_icon()
        self.star_button.toggled.connect(self._on_priority_changed)
        h_layout.addWidget(self.star_button)

        # Only shown once a task is checked done — lets you clear it out for good
        self.delete_button = QPushButton("✕")
        self.delete_button.setObjectName("delete-button")
        self.delete_button.setFixedSize(26, 26)
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setVisible(bool(self.task_data.get("done", False)))
        self.delete_button.clicked.connect(self._on_delete_clicked)
        h_layout.addWidget(self.delete_button)

    def _schedule_text(self):
        date_val = self.task_data.get("date", [])
        date_str = ""
        try:
            d, m, y = date_val
            date_str = f"{int(d):02d}/{int(m):02d}/{int(y)}"
        except (ValueError, TypeError):
            pass
        time_val = self.task_data.get("time") or []
        time_str = ":".join(str(t) for t in time_val)
        return f"{date_str}  {time_str}".strip() if time_str else date_str

    def _sync_star_icon(self):
        self.star_button.setText("★" if self.star_button.isChecked() else "☆")

    # ---------- state changes ----------

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

    # ---------- hover behavior ----------

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
        pen = QPen(QColor("#89b4fa"))  # swap for your accent color
        pen.setWidth(2)
        painter.setPen(pen)
        size, margin = 14, 10
        w, h = self.width(), self.height()
        # top-left bracket
        painter.drawLine(margin, margin, margin + size, margin)
        painter.drawLine(margin, margin, margin, margin + size)
        # bottom-right bracket
        painter.drawLine(w - margin, h - margin, w - margin - size, h - margin)
        painter.drawLine(w - margin, h - margin, w - margin, h - margin - size)
        painter.end()


class ToDoCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do-Card")
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

    def refresh_tasks(self):
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        day, tasks = self.fetch_task()
        for task_data in tasks:
            card = TaskCard(day, task_data)
            card.doneToggled.connect(self._on_done_toggled)
            card.priorityToggled.connect(self._on_priority_toggled)
            card.deleteRequested.connect(self._on_delete_requested)

            outer_layout = QHBoxLayout()
            outer_layout.addStretch(1)
            outer_layout.addWidget(card, 6)
            outer_layout.addStretch(1)
            self.tasks_layout.addLayout(outer_layout)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _load_stylesheet(self):
        possible_paths = [
            "to-do-task.qss",
            os.path.join("APP", "to-do-task.qss"),
            os.path.join(os.path.dirname(__file__), "to-do-task.qss"),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                return

    def _find_task_json(self):
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
        """Returns (day_name, list_of_tasks) for today, matching the
        weekday-keyed structure in task.json."""
        day = datetime.now().strftime("%A")
        if not self._json_path:
            return day, []
        try:
            with open(self._json_path, "r") as f:
                file_content = json.load(f)
            task_root = file_content.get("task", {})
            if isinstance(task_root, dict):
                return day, task_root.get(day, [])
            return day, task_root  # fallback for a flat-list format
        except Exception as e:
            print(f"error reading task.json: {e}")
            return day, []

    def _update_task_field(self, day, task_id, field, value):
        if not self._json_path or task_id is None:
            return
        try:
            with open(self._json_path, "r") as f:
                file_content = json.load(f)
            day_tasks = file_content.get("task", {}).get(day, [])
            for t in day_tasks:
                if t.get("id") == task_id:
                    t[field] = value
                    break
            with open(self._json_path, "w") as f:
                json.dump(file_content, f, indent=2)
        except Exception as e:
            print(f"error updating task.json: {e}")

    def _on_done_toggled(self, day, task_id, done):
        self._update_task_field(day, task_id, "done", done)

    def _on_priority_toggled(self, day, task_id, priority):
        self._update_task_field(day, task_id, "priority", priority)

    def _on_delete_requested(self, day, task_id):
        self._remove_task(day, task_id)
        self.refresh_tasks()

    def _remove_task(self, day, task_id):
        if not self._json_path or task_id is None:
            return
        try:
            with open(self._json_path, "r") as f:
                file_content = json.load(f)
            day_tasks = file_content.get("task", {}).get(day, [])
            file_content["task"][day] = [t for t in day_tasks if t.get("id") != task_id]
            with open(self._json_path, "w") as f:
                json.dump(file_content, f, indent=2)
        except Exception as e:
            print(f"error removing task from task.json: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("to-do.qss", "r") as f:
      app.setStyleSheet(f.read())
    widget = ToDoCard()
    widget.show()
    app.exec()