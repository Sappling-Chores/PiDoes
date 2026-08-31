import sys
import os

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

try:
    from banner import BannerFrame
    from todo import ToDoCard
    from paths import APP_ICON
    from setting import SettingWindow
except ImportError:
    from APP.banner import BannerFrame
    from APP.todo import ToDoCard
    from APP.paths import APP_ICON
    from APP.setting import SettingWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi-Dos")
        if APP_ICON and APP_ICON.exists():
            self.setWindowIcon(QIcon(str(APP_ICON)))

        self.stacked_widget = QStackedWidget()

        # Banner is the background: renders wallpaper and header
        self.banner = BannerFrame()

        # Embedded todo card layout
        self.todo = ToDoCard()
        self.todo.setAttribute(Qt.WA_TranslucentBackground)
        self.banner.image_layout.insertWidget(1, self.todo)
        self.banner.image_layout.addWidget(self.todo.add_bar)

        self.setting_panel = SettingWindow()

        self.stacked_widget.addWidget(self.banner)
        self.stacked_widget.addWidget(self.setting_panel)

        # Switch to settings page
        self.banner.settings_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        # Return to main page
        self.setting_panel.back_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Left sidebar navigation connections
        self.banner.my_day_btn.clicked.connect(lambda: self.switch_view("my_day"))
        self.banner.important_btn.clicked.connect(lambda: self.switch_view("important"))
        self.banner.old_tasks_btn.clicked.connect(lambda: self.switch_view("old_tasks"))
        self.banner.last_week_btn.clicked.connect(lambda: self.switch_view("last_week"))
        self.banner.older_btn.clicked.connect(lambda: self.switch_view("older"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def switch_view(self, mode):
        self.banner.set_view(mode)
        self.todo.set_view_mode(mode)
        
        # Update active states on sidebar buttons
        self.banner.my_day_btn.setProperty("active", mode == "my_day")
        self.banner.important_btn.setProperty("active", mode == "important")
        self.banner.old_tasks_btn.setProperty("active", mode == "old_tasks")
        self.banner.last_week_btn.setProperty("active", mode == "last_week")
        self.banner.older_btn.setProperty("active", mode == "older")
        
        # Polish/unpolish to trigger styling updates
        for btn in (self.banner.my_day_btn, self.banner.important_btn, self.banner.old_tasks_btn,
                    self.banner.last_week_btn, self.banner.older_btn):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def closeEvent(self, event):
        event.ignore()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()