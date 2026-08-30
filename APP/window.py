import sys
import os

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

try:
    from banner import BannerFrame
    from todo import ToDoCard
except ImportError:
    from APP.banner import BannerFrame
    from APP.todo import ToDoCard

ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "Pi-icon.png")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi-Dos")
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        # Banner is the background: it renders the wallpaper image and the
        # "My Day" header (title, date, wallpaper button) top-to-bottom.
        self.banner = BannerFrame()

        # The to-do card is embedded straight into the banner's own image
        # layout, below the header. Because it's a normal child widget (not
        # a full-window overlay), it only claims the screen space it
        # actually occupies. Everything above it -- including the wallpaper
        # button in the top-right -- is untouched and stays fully clickable.
        self.todo = ToDoCard()
        self.todo.setAttribute(Qt.WA_TranslucentBackground)
        self.banner.image_layout.addWidget(self.todo)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.banner)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()