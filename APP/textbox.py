import sys
import os
import datetime
from PySide6.QtWidgets import (
    QLineEdit, QVBoxLayout, QHBoxLayout, QApplication, QWidget,
    QFrame, QLabel, QPushButton, QDialog, QCalendarWidget,
    QTimeEdit, QDialogButtonBox, QStackedWidget
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QSize, Qt, QDate, QTime, Signal
import json

try:
    from paths import ASSETS_DIR, TASK_JSON
except ImportError:
    from APP.paths import ASSETS_DIR, TASK_JSON


def _asset_path(name):
    return str(ASSETS_DIR / name)


# â”€â”€ Shared style constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_BAR_HEIGHT = 56
_BAR_BG     = "rgba(255, 255, 255, 140)"
_ICON_BTN   = """
    QPushButton {
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 0px;
    }
    QPushButton:hover {
        background: rgba(0,0,0,15);
        border-radius: 8px;
    }
"""


class TextBox(QWidget):
    """Two-state add-task bar.

    Collapsed: shows "+ Add a task" prompt, calendar + clock icons on the right.
    Expanded:  shows QLineEdit that fills the full width; same calendar + clock icons
               stay on the right touching each other.  Clicking away or pressing Escape
               collapses back (unless there's text).
    """
    task_added = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("textbox-widget")
        self.setFixedHeight(_BAR_HEIGHT)
        self.setStyleSheet(f"""
            QWidget#textbox-widget {{
                background: {_BAR_BG};
                border-top: 1px solid rgba(0,0,0,18);
            }}
        """)

        self.selected_date = None
        self.selected_time = None
        self._expanded = False

        # â”€â”€ Collapsed row â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._collapsed_row = QWidget()
        self._collapsed_row.setStyleSheet(f"background: {_BAR_BG};")
        cl = QHBoxLayout(self._collapsed_row)
        cl.setContentsMargins(16, 0, 8, 0)
        cl.setSpacing(0)

        plus_label = QLabel("+")
        plus_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #2564CF;
                font-size: 20px;
                font-weight: 400;
                padding-right: 8px;
            }
        """)

        self._prompt_label = QLabel("Add a task")
        self._prompt_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #444;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        cl.addWidget(plus_label)
        cl.addWidget(self._prompt_label)
        cl.addStretch(1)
        cl.addWidget(self._make_calendar_btn())
        cl.addSpacing(2)
        cl.addWidget(self._make_clock_btn())
        cl.addSpacing(4)

        # Make the whole collapsed row clickable â†’ expand
        self._collapsed_row.mousePressEvent = lambda e: self.expand()

        # â”€â”€ Expanded row â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._expanded_row = QWidget()
        self._expanded_row.setStyleSheet(f"background: {_BAR_BG};")
        el = QHBoxLayout(self._expanded_row)
        el.setContentsMargins(16, 0, 8, 0)
        el.setSpacing(0)

        self._textbox = QLineEdit()
        self._textbox.setPlaceholderText("Add a task")
        self._textbox.setObjectName("text-box")
        self._textbox.setFixedHeight(36)
        self._textbox.setStyleSheet(f"""
            QLineEdit#text-box {{
                border: none;
                background: transparent;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #222;
                padding: 0px;
                margin: 0px;
            }}
        """)
        self._textbox.returnPressed.connect(self.dump_text)
        # Collapse back if user presses Escape and the field is empty
        self._textbox.installEventFilter(self)

        self._cal_btn2  = self._make_calendar_btn()
        self._clk_btn2  = self._make_clock_btn()

        el.addWidget(self._textbox, 1)
        el.addStretch(0)
        el.addWidget(self._cal_btn2)
        el.addSpacing(2)
        el.addWidget(self._clk_btn2)
        el.addSpacing(4)

        # â”€â”€ Stacked container â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._stack = QStackedWidget()
        self._stack.addWidget(self._collapsed_row)   # index 0
        self._stack.addWidget(self._expanded_row)    # index 1
        self._stack.setCurrentIndex(0)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._stack)
        self.setLayout(root)

    # â”€â”€ State transitions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def expand(self):
        self._expanded = True
        self._stack.setCurrentIndex(1)
        self._textbox.setFocus()

    def collapse(self):
        if self._textbox.text().strip():
            return           # Don't collapse if there's unsaved text
        self._expanded = False
        self._stack.setCurrentIndex(0)
        self._textbox.clear()

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj is self._textbox:
            if event.type() == QEvent.KeyPress:
                from PySide6.QtGui import QKeyEvent
                if event.key() == Qt.Key_Escape:
                    self._textbox.clear()
                    self.collapse()
                    return True
            elif event.type() == QEvent.FocusOut:
                self.collapse()
        return super().eventFilter(obj, event)

    # â”€â”€ Icon button factories â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _make_calendar_btn(self):
        btn = QPushButton()
        btn.setIcon(QIcon(_asset_path("calendar-dots-dark.svg")))
        btn.setIconSize(QSize(22, 22))
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(_ICON_BTN)
        btn.setToolTip("Set date")
        btn.clicked.connect(self.open_calendar)
        return btn

    def _make_clock_btn(self):
        btn = QPushButton()
        btn.setIcon(QIcon(_asset_path("alarm-light.svg")))
        btn.setIconSize(QSize(22, 22))
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(_ICON_BTN)
        btn.setToolTip("Set time")
        btn.clicked.connect(self.open_time_picker)
        return btn

    # â”€â”€ Calendar / Clock popups â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def open_calendar(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date")
        layout = QVBoxLayout(dialog)

        calendar = QCalendarWidget()
        if self.selected_date:
            day, month, year = self.selected_date
            calendar.setSelectedDate(QDate(year, month, day))
        layout.addWidget(calendar)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            qdate = calendar.selectedDate()
            self.selected_date = [qdate.day(), qdate.month(), qdate.year()]

    def open_time_picker(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Time")
        layout = QVBoxLayout(dialog)

        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        if self.selected_time:
            hour, minute = self.selected_time
            time_edit.setTime(QTime(hour, minute))
        else:
            time_edit.setTime(QTime.currentTime())
        layout.addWidget(time_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            qtime = time_edit.time()
            self.selected_time = [qtime.hour(), qtime.minute()]

    # â”€â”€ Task persistence â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _task_json_path(self):
        return str(TASK_JSON)

    def get_task_content(self):
        path = self._task_json_path()
        try:
            with open(path, "r") as f:
                content = json.load(f)
        except FileNotFoundError:
            content = {"task": {}}
        content.setdefault("task", {})
        return content

    def get_text(self):
        return self._textbox.text()

    def _resolve_target_day(self):
        if self.selected_date:
            day, month, year = self.selected_date
            try:
                return datetime.date(year, month, day).strftime("%A")
            except ValueError:
                pass
        return datetime.datetime.now().strftime("%A")

    @staticmethod
    def _today_date_list():
        today = datetime.date.today()
        return [today.day, today.month, today.year]

    def dump_text(self):
        task_content = self.get_task_content()
        text_content = self.get_text()
        list_trash = ["", ".", ","]
        added = False
        if text_content.strip() not in list_trash:
            target_day = self._resolve_target_day()
            day_tasks = task_content["task"].setdefault(target_day, [])
            next_id = max((t.get("id", 0) for t in day_tasks), default=0) + 1
            new_task = {
                "id": next_id,
                "task": text_content,
                "date": self.selected_date if self.selected_date else self._today_date_list(),
                "time": self.selected_time if self.selected_time else [],
                "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
                "done": False,
                "priority": False,
            }
            day_tasks.append(new_task)
            added = True
            self._textbox.clear()
            self.selected_date = None
            self.selected_time = None
            self.collapse()

        with open(self._task_json_path(), "w") as f:
            json.dump(task_content, f, indent=2)

        if added:
            self.task_added.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TextBox()
    widget.resize(800, _BAR_HEIGHT)
    widget.show()
    app.exec()

