# This file would contain every setting of the PIDOES

import sys
from PySide6.QtWidgets import (
    QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QApplication, QWidget,
    QFrame, QLabel, QCheckBox, QPushButton, QButtonGroup
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QByteArray
from PySide6.QtSvg import QSvgRenderer
import json

from toggle_switch import ToggleSwitch

class SettingWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Setting-Panel")
    self.label = QLabel("Settings")
    self.label.setObjectName("setting-label")
    
    back_arrow_icon = QIcon("../assets/arrow-left-bold.svg")
    back_arrow_button = QPushButton()
    back_arrow_button.setObjectName("back-arrow-button")
    back_arrow_button.setIcon(back_arrow_icon)
    back_arrow_button.setFixedSize(44, 44)
    
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
    toggle_completion_sound = ToggleSwitch()
    
    label_confirm_delete = QLabel("Confirm before deletion")
    label_confirm_delete.setObjectName("normal-label")
    toggle_confirm_delete = ToggleSwitch()
    
    label_newtask_top = QLabel("Add new task on top")
    label_newtask_top.setObjectName("normal-label")
    toggle_newtask_top = ToggleSwitch()
    
    label_pin_taskbar = QLabel("Pin Pidoes to task bar")
    label_pin_taskbar.setObjectName("normal-label")
    toggle_pin_taskbar = ToggleSwitch()
    
    label_themes = QLabel("Themes")
    label_themes.setObjectName("sub-label")

    # Theme choice: mutually exclusive checkboxes (Light / Dark / Device).
    # QButtonGroup with exclusive=True enforces the single-selection
    # behavior even though these are QCheckBox, not QRadioButton.
    self.theme_group = QButtonGroup(self)
    self.theme_group.setExclusive(True)

    checkbox_theme_light = QCheckBox("Light")
    checkbox_theme_light.setObjectName("theme-checkbox")

    checkbox_theme_dark = QCheckBox("Dark")
    checkbox_theme_dark.setObjectName("theme-checkbox")

    checkbox_theme_device = QCheckBox("Device")
    checkbox_theme_device.setObjectName("theme-checkbox")
    checkbox_theme_device.setChecked(True)  # sensible default

    self.theme_group.addButton(checkbox_theme_light)
    self.theme_group.addButton(checkbox_theme_dark)
    self.theme_group.addButton(checkbox_theme_device)

    label_mode = QLabel("Mode")
    label_mode.setObjectName("sub-label")

    label_troll_mode = QLabel("Troll mode")
    label_troll_mode.setObjectName("normal-label")
    toggle_troll_mode = ToggleSwitch()

    label_notification = QLabel("Notification")
    label_notification.setObjectName("sub-label")
    
    label_allow_notification = QLabel("Allow notification")
    label_allow_notification.setObjectName("normal-label")
    toggle_allow_notification = ToggleSwitch()
    
    
        
    def make_divider():
      d = QFrame()
      d.setObjectName("divider-line")
      d.setFixedHeight(1)
      return d
       
    v_list_layout.addWidget(label_general)
    v_list_layout.addWidget(label_completion_sound)
    v_list_layout.addWidget(toggle_completion_sound)
    v_list_layout.addWidget(label_confirm_delete)
    v_list_layout.addWidget(toggle_confirm_delete)
    v_list_layout.addWidget(label_newtask_top)
    v_list_layout.addWidget(toggle_newtask_top)
    v_list_layout.addWidget(label_pin_taskbar)
    v_list_layout.addWidget(toggle_pin_taskbar)
    v_list_layout.addWidget(make_divider())
    v_list_layout.addWidget(label_themes)
    v_list_layout.addWidget(checkbox_theme_light)
    v_list_layout.addWidget(checkbox_theme_dark)
    v_list_layout.addWidget(checkbox_theme_device)
    v_list_layout.addWidget(make_divider())
    v_list_layout.addWidget(label_mode)
    v_list_layout.addWidget(label_troll_mode)
    v_list_layout.addWidget(toggle_troll_mode)
    v_list_layout.addWidget(make_divider())
    v_list_layout.addWidget(label_notification)
    v_list_layout.addWidget(label_allow_notification)
    v_list_layout.addWidget(toggle_allow_notification)
    
      
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



if __name__ == "__main__":
  app = QApplication(sys.argv)
  
  with open("setting.qss", "r") as f:
    app.setStyleSheet(f.read())
  window = SettingWindow()
  window.show()
  
  app.exec()