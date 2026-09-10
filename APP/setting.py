# This file would contain every setting of the PIDOES

import sys
from PySide6.QtWidgets import (
    QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QApplication, QWidget,
    QFrame, QLabel, QCheckBox, QPushButton, QButtonGroup
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QByteArray, Signal
from PySide6.QtSvg import QSvgRenderer
import json
try:
    from toggle_switch import ToggleSwitch
except ImportError:
    from APP.toggle_switch import ToggleSwitch


try:
    from paths import ARROW_LEFT_SVG, SETTING_JSON, SETTING_QSS
except ImportError:
    from APP.paths import ARROW_LEFT_SVG, SETTING_JSON, SETTING_QSS


class SettingWindow(QWidget):
  back_clicked = Signal()

  def __init__(self):
    super().__init__()
    self.setWindowTitle("Setting-Panel")
    
    if SETTING_QSS.exists():
      with open(SETTING_QSS, "r", encoding="utf-8") as f:
        self.setStyleSheet(f.read())

    self.label = QLabel("Settings")
    self.label.setObjectName("setting-label")
    
    back_arrow_icon = QIcon(str(ARROW_LEFT_SVG))
    back_arrow_button = QPushButton()
    back_arrow_button.setObjectName("back-arrow-button")
    back_arrow_button.setIcon(back_arrow_icon)
    back_arrow_button.setFixedSize(44, 44)
    back_arrow_button.clicked.connect(self.back_clicked)
    
    label_frame = QFrame()
    label_frame.setObjectName("setting-label-frame")
    label_frame.setFixedHeight(80)
    h_label_layout = QHBoxLayout(label_frame)
    h_label_layout.addWidget(back_arrow_button)
    h_label_layout.addStretch(1)
    h_label_layout.addWidget(self.label)
    h_label_layout.addStretch(75)

    
    divider = QFrame()
    divider.setObjectName("divider-line")
    divider.setFixedHeight(1)
    
    
    list_frame = QFrame()
    list_frame.setObjectName("list-frame")
    list_frame.setFixedWidth(560)
    v_list_layout = QVBoxLayout(list_frame)
    label_general = QLabel("General")
    label_general.setObjectName("sub-label")
    
    label_completion_sound = QLabel("Play completion sound")
    label_completion_sound.setObjectName("normal-label")
    self.toggle_completion_sound = ToggleSwitch()
    
    label_confirm_delete = QLabel("Confirm before deletion")
    label_confirm_delete.setObjectName("normal-label")
    self.toggle_confirm_delete = ToggleSwitch()
    
    label_newtask_top = QLabel("Add new task on top")
    label_newtask_top.setObjectName("normal-label")
    self.toggle_newtask_top = ToggleSwitch()
    
    label_pin_taskbar = QLabel("Pin Pidoes to task bar")
    label_pin_taskbar.setObjectName("normal-label")
    self.toggle_pin_taskbar = ToggleSwitch()
    
    label_themes = QLabel("Themes")
    label_themes.setObjectName("sub-label")

    # Theme choice: mutually exclusive checkboxes (Light / Dark / Device).
    # QButtonGroup with exclusive=True enforces the single-selection
    # behavior even though these are QCheckBox, not QRadioButton.
    self.theme_group = QButtonGroup(self)
    self.theme_group.setExclusive(True)

    self.checkbox_theme_light = QCheckBox("Light")
    self.checkbox_theme_light.setObjectName("theme-checkbox")

    self.checkbox_theme_dark = QCheckBox("Dark")
    self.checkbox_theme_dark.setObjectName("theme-checkbox")

    self.checkbox_theme_device = QCheckBox("Device")
    self.checkbox_theme_device.setObjectName("theme-checkbox")

    self.theme_group.addButton(self.checkbox_theme_light)
    self.theme_group.addButton(self.checkbox_theme_dark)
    self.theme_group.addButton(self.checkbox_theme_device)

    label_mode = QLabel("Mode")
    label_mode.setObjectName("sub-label")

    label_troll_mode = QLabel("Troll mode")
    label_troll_mode.setObjectName("normal-label")
    self.toggle_troll_mode = ToggleSwitch()

    label_notification = QLabel("Notification")
    label_notification.setObjectName("sub-label")
    
    label_allow_notification = QLabel("Allow notification")
    label_allow_notification.setObjectName("normal-label")
    self.toggle_allow_notification = ToggleSwitch()
    
    # Load settings from file and apply to UI
    self.load_settings()

    # Connect signals to automatically save settings when changed
    self.toggle_completion_sound.toggled_signal.connect(self.save_settings)
    self.toggle_confirm_delete.toggled_signal.connect(self.save_settings)
    self.toggle_newtask_top.toggled_signal.connect(self.save_settings)
    self.toggle_pin_taskbar.toggled_signal.connect(self.save_settings)
    self.toggle_troll_mode.toggled_signal.connect(self.save_settings)
    self.toggle_allow_notification.toggled_signal.connect(self.save_settings)

    self.checkbox_theme_light.stateChanged.connect(self.save_settings)
    self.checkbox_theme_dark.stateChanged.connect(self.save_settings)
    self.checkbox_theme_device.stateChanged.connect(self.save_settings)
        
    def make_divider():
      d = QFrame()
      d.setObjectName("divider-line")
      d.setFixedHeight(1)
      return d
       
    v_list_layout.addWidget(label_general)
    v_list_layout.addWidget(label_completion_sound)
    v_list_layout.addWidget(self.toggle_completion_sound)
    v_list_layout.addWidget(label_confirm_delete)
    v_list_layout.addWidget(self.toggle_confirm_delete)
    v_list_layout.addWidget(label_newtask_top)
    v_list_layout.addWidget(self.toggle_newtask_top)
    v_list_layout.addWidget(label_pin_taskbar)
    v_list_layout.addWidget(self.toggle_pin_taskbar)
    v_list_layout.addWidget(make_divider())
    v_list_layout.addWidget(label_themes)
    v_list_layout.addWidget(self.checkbox_theme_light)
    v_list_layout.addWidget(self.checkbox_theme_dark)
    v_list_layout.addWidget(self.checkbox_theme_device)
    v_list_layout.addWidget(make_divider())
    v_list_layout.addWidget(label_mode)
    v_list_layout.addWidget(label_troll_mode)
    v_list_layout.addWidget(self.toggle_troll_mode)
    v_list_layout.addWidget(make_divider())
    v_list_layout.addWidget(label_notification)
    v_list_layout.addWidget(label_allow_notification)
    v_list_layout.addWidget(self.toggle_allow_notification)
    
      
    list_h_frame = QFrame()
    list_h_layout = QHBoxLayout(list_h_frame)
    list_h_layout.addStretch(1)
    list_h_layout.addWidget(list_frame)
    list_h_layout.addStretch(1)

    
    v_layout = QVBoxLayout()

    v_layout.addWidget(label_frame)
    v_layout.addWidget(divider)
    v_layout.addWidget(list_h_frame)
    v_layout.addStretch(0)
    
    self.setLayout(v_layout)
  
  def load_settings(self):
    settings = self.fetch_setting()
    if not settings:
      return

    gen = settings.get("general", {})
    self.toggle_completion_sound.setChecked(gen.get("play_completion_sound", False))
    self.toggle_confirm_delete.setChecked(gen.get("confirm_before_deletion", False))
    self.toggle_newtask_top.setChecked(gen.get("add_new_task_on_top", False))
    self.toggle_pin_taskbar.setChecked(gen.get("pin_pidoes_to_taskbar", False))

    themes = settings.get("themes", {})
    is_light = themes.get("light", False)
    is_dark = themes.get("dark", False)
    if is_light:
      self.checkbox_theme_light.setChecked(True)
    elif is_dark:
      self.checkbox_theme_dark.setChecked(True)
    else:
      self.checkbox_theme_device.setChecked(True)

    notification = settings.get("notification", {})
    self.toggle_allow_notification.setChecked(notification.get("allow_notification", False))

    mode = settings.get("mode", {})
    self.toggle_troll_mode.setChecked(mode.get("troll_mode", False))

  def save_settings(self, *args):
    settings = {
      "general": {
        "play_completion_sound": self.toggle_completion_sound.isChecked(),
        "confirm_before_deletion": self.toggle_confirm_delete.isChecked(),
        "add_new_task_on_top": self.toggle_newtask_top.isChecked(),
        "pin_pidoes_to_taskbar": self.toggle_pin_taskbar.isChecked()
      },
      "themes": {
        "dark": self.checkbox_theme_dark.isChecked(),
        "light": self.checkbox_theme_light.isChecked()
      },
      "notification": {
        "allow_notification": self.toggle_allow_notification.isChecked()
      },
      "mode": {
        "troll_mode": self.toggle_troll_mode.isChecked()
      }
    }
    try:
      SETTING_JSON.parent.mkdir(parents=True, exist_ok=True)
      with open(SETTING_JSON, "w") as f:
        json.dump(settings, f, indent=2)
    except Exception as e:
      print(f"Error saving setting.json: {e}")

  def fetch_setting(self):
    if SETTING_JSON.exists():
      with open(SETTING_JSON, "r") as f:
        setting_data = json.load(f)
      return setting_data
    return {}


if __name__ == "__main__":
  app = QApplication(sys.argv)
  
  if SETTING_QSS.exists():
    with open(SETTING_QSS, "r") as f:
      app.setStyleSheet(f.read())
  window = SettingWindow()
  window.show()
  
  app.exec()