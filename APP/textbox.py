import sys
import os
import datetime
from PySide6.QtWidgets import (
    QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QApplication, QWidget,
    QFrame, QLabel, QCheckBox, QPushButton, QDialog, QCalendarWidget,
    QTimeEdit, QDialogButtonBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QByteArray, Qt, QDate, QTime, Signal
from PySide6.QtSvg import QSvgRenderer
import json

class TextBox(QWidget):
  # Emitted after a task is successfully written to task.json, so a
  # container (e.g. ToDoCard) can refresh its task list.
  task_added = Signal()

  def __init__(self):
    super().__init__()
    self.setWindowTitle("textbox-preview")
    self.setObjectName("main-window")
    # self.setMaximumWidth(1120)
    # self.setMaximumHeight(128)
    h_layout = QHBoxLayout()
    h_layout.setSpacing(0)
    h_layout.setContentsMargins(0, 0, 0, 0)
    v_layout = QVBoxLayout()
    check_box = QCheckBox()
    check_box.setMaximumWidth(32)
    check_box.setStyleSheet(
      """
      QCheckBox {
        background:  #EAEBED;
        height: 64px;
        spacing: 8px;
        font-size: 14px;
        color: #333;
        padding-left: 8px;
        padding-right:16px;
        margin-right: 0px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 11px;     /* rounded or 9px for a circle */
        border: 2px solid #A7A7A7;
        background: white;
    }

    QCheckBox::indicator:hover {
        border-color: #666;
    }

    QCheckBox::indicator:unchecked {
        background: white;
    }

    QCheckBox::indicator:checked {
        background: #687681;
        image: url(./assets/tick.png);   /* custom checkmark icon */
    }

    QCheckBox::indicator:indeterminate {
        background: #FFC107;            /* for tri-state checkboxes */
    }

    QCheckBox::indicator:disabled {
        background: #eee;
        border-color: #ccc;
    }
      
      
      
      
      """
      
    )
    textbox = QLineEdit()
    textbox.setPlaceholderText("Type the task and set the time")
    textbox.setObjectName("text-box")
    textbox.setFixedHeight(64)
    textbox.setMaximumWidth(1000)
    
    textbox.setStyleSheet(
      """
      QLineEdit#text-box{
        border : none;
        background : #EAEBED;
        font-size : 20px;
        color : #414141;
        font-family : "Inter";
        margin-left : 0px;
      } 
      """ )  

    # Enter key inside the textbox submits the task
    textbox.returnPressed.connect(self.dump_text)
    
    def _asset_path(name):
      possible_paths = [
        os.path.join("assets", name),
        os.path.join("APP", "assets", name),
        os.path.join(os.path.dirname(__file__), "assets", name),
      ]
      for p in possible_paths:
        if os.path.exists(p):
          return p
      return os.path.join("assets", name)  # fall back to original relative guess

    calendar_icon = QIcon(_asset_path("calendar-dots-dark.svg"))
    button_calendar = QPushButton()
    button_calendar.setIcon(calendar_icon)
    button_calendar.setIconSize(QSize(28, 28))
    button_calendar.setFixedHeight(40)
    button_calendar.clicked.connect(self.open_calendar)
    button_calendar.setStyleSheet(
      """
      QPushButton{
        border-radius : none;
        padding-right : 2px;
        padding-left : 2px;
      }
      
      QPushButton:hover{
        background: white;
        border-radius : 8px;
      }
      
      """
      
    )
    calendar_frame = QFrame()
    calendar_frame.setObjectName("CalendarFrame")
    calendar_layout = QHBoxLayout(calendar_frame)
    calendar_layout.addWidget(button_calendar)
    calendar_frame.setFixedHeight(64)
    calendar_frame.setStyleSheet(
      """
        background :  #EAEBED;
        border-radius : none;
        padding-right : 2px;
        padding-left : 2px;
      
      """
      
    )
        
    
    clock_icon = QIcon(_asset_path("alarm-light.svg"))
    button_clock = QPushButton()
    button_clock.setIcon(clock_icon)
    button_clock.setIconSize(QSize(28, 28))
    button_clock.setFixedHeight(40)
    button_clock.clicked.connect(self.open_time_picker)
    button_clock.setStyleSheet(
      """
      
      QPushButton{
        border-radius : none;
        padding-right : 2px;
        padding-left : 2px;
      }
      
      QPushButton:hover{
        background :  white;
        border-radius : 8px;
        
      }
      
      """
      
    )

    clock_frame = QFrame()
    clock_frame.setObjectName("ClockFrame")
    clock_layout = QHBoxLayout(clock_frame)
    clock_layout.addWidget(button_clock)
    clock_frame.setFixedHeight(64)
    clock_frame.setStyleSheet(
      """
        background :  #EAEBED;
        border-radius : none;
        padding-right : 2px;
        padding-left : 2px;
      
      """
      
    )
    
    h_layout.addStretch(1)
    h_layout.addWidget(check_box, 0)
    h_layout.addWidget(textbox, 0)  # stretch factor 0 -> we control width manually now
    
    h_layout.addWidget(calendar_frame, 0) 
    h_layout.addWidget(clock_frame, 0)
    h_layout.addStretch(1)

    self.setLayout(h_layout)

    # keep references for resizeEvent to use
    self.textbox = textbox
    self.check_box = check_box
    self.WIDTH_PERCENT = 0.85   # textbox covers 85% of window width until it hits max width
    self.MAX_TEXTBOX_WIDTH = 1000

    # holds the date/time picked via the calendar/clock buttons,
    # until the task is actually submitted (Enter). Reset after each submit.
    self.selected_date = None   # e.g. [24, 8, 2026]  -> [day, month, year]
    self.selected_time = None   # e.g. [14, 30]       -> [hour, minute]
    
    self._update_textbox_width()

  def resizeEvent(self, event):
    self._update_textbox_width()
    super().resizeEvent(event)

  def _update_textbox_width(self):
    available_width = self.width() - self.check_box.maximumWidth()
    target_width = int(available_width * self.WIDTH_PERCENT)
    target_width = min(target_width, self.MAX_TEXTBOX_WIDTH)
    self.textbox.setFixedWidth(target_width)

  # ---------------- Calendar / Clock popups ----------------

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

  # ---------------- Task persistence ----------------
    
  def _task_json_path(self):
    possible_paths = [
      "task.json",
      os.path.join("APP", "task.json"),
      os.path.join(os.path.dirname(__file__), "task.json"),
    ]
    for p in possible_paths:
      if os.path.exists(p):
        return p
    # Nothing found yet -- create it next to this file so writes have a home.
    return os.path.join(os.path.dirname(__file__), "task.json")

  def get_task_content(self):
    path = self._task_json_path()
    try:
      with open(path, "r") as f:
        content = json.load(f)
    except FileNotFoundError:
      content = {"task": {}}
    # "task" is a dict keyed by weekday ("Monday", "Tuesday", ...) in the
    # real schema -- make sure it's always at least that shape.
    content.setdefault("task", {})
    return content
    
  def get_text(self):
    text_content = self.textbox.text()
    return text_content

  def _resolve_target_day(self):
    """Which weekday bucket a new task lands in: the picked date's own
    weekday if the user chose one via the calendar, otherwise today."""
    if self.selected_date:
      day, month, year = self.selected_date
      try:
        return datetime.date(year, month, day).strftime("%A")
      except ValueError:
        pass  # fall through to today if the picked date is somehow invalid
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

      # ids only need to be unique within a day's list, matching the
      # existing entries (each day currently starts its own id count).
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

      # clear the input and reset the picked date/time for the next task
      self.textbox.clear()
      self.selected_date = None
      self.selected_time = None
    

    with open(self._task_json_path(), "w") as f:
      json.dump(task_content, f, indent=2)

    if added:
      self.task_added.emit()

    
    
if __name__=="__main__":    
  app = QApplication(sys.argv)

  widget = TextBox()
  widget.show()

  app.exec()