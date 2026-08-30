import sys
import os
import requests
from datetime import datetime
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QLabel, QVBoxLayout, QWidget,
    QHBoxLayout, QPushButton, QDialog
)
from PySide6.QtGui import QPixmap, QIcon, QColor
from PySide6.QtCore import Qt, QSize

try:
    from wallpaper_dialog import WallpaperDialog
except ImportError:
    from APP.wallpaper_dialog import WallpaperDialog

date = datetime.now()
day_date = date.strftime("%A, %d %B").lstrip()

def fetch_urls():
    possible_paths = [
        "urls.json",
        os.path.join("APP", "urls.json"),
        os.path.join(os.path.dirname(__file__), "urls.json")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data["urls"][0]
            except Exception:
                pass
    return {}

class BannerFrame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BannerFrame")
        self.current_wallpaper = None

        qss_path = os.path.join(os.path.dirname(__file__), "banner.qss")
        if not os.path.exists(qss_path):
            qss_path = "banner.qss"
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        main_layout = QHBoxLayout()
        self.frame = QFrame()
        v_layout = QVBoxLayout(self.frame)
        self.frame.setFixedSize(1280, 800)

        self.image_label = QLabel(self.frame)
        self.image_label.setFixedSize(1280, 800)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Main layout over image_label for overlaying labels, the SVG button, and (optionally)
        # the to-do card directly on top of the banner image. Kept as self.image_layout so
        # other widgets (e.g. ToDoCard) can be embedded into it from outside this class.
        self.image_layout = QVBoxLayout(self.image_label)
        image_layout = self.image_layout
        image_layout.setContentsMargins(32, 24, 32, 24)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "dots-three.svg")
        if not os.path.exists(icon_path):
            icon_path = os.path.join("APP", "assets", "dots-three.svg")

        self.wallpaper_btn = QPushButton(self.image_label)
        self.wallpaper_btn.setObjectName("wallpaper-btn")
        if os.path.exists(icon_path):
            self.wallpaper_btn.setIcon(QIcon(icon_path))
            self.wallpaper_btn.setIconSize(QSize(32, 32))
        else:
            self.wallpaper_btn.setText("...")
        self.wallpaper_btn.setFixedSize(44, 44)
        self.wallpaper_btn.setCursor(Qt.PointingHandCursor)
        self.wallpaper_btn.setToolTip("Change Wallpaper")
        self.wallpaper_btn.clicked.connect(self.open_wallpaper_dialog)

        self.label = QLabel(self.image_label)
        h_layout = QHBoxLayout()
        self.label.setText("My Day")
        self.label.setObjectName("title-label")
        h_layout.addWidget(self.label)
        h_layout.addStretch(0)

        self.date_label = QLabel(self.image_label)
        self.date_label.setText(day_date)
        self.date_label.setObjectName("date-label")
        date_h_layout = QHBoxLayout()
        date_h_layout.addWidget(self.date_label)
        date_h_layout.addStretch(0)

        title_frame = QFrame(self.image_label)
        title_frame.setFixedHeight(90)
        title_frame.setObjectName("title-frame")
        title_v_layout = QVBoxLayout(title_frame)
        title_v_layout.setContentsMargins(0, 0, 0, 0)
        title_v_layout.addLayout(h_layout)
        title_v_layout.addLayout(date_h_layout)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title_frame)
        header_layout.addStretch(1)
        header_layout.addWidget(self.wallpaper_btn, 0, Qt.AlignTop)

        image_layout.addLayout(header_layout)
        image_layout.addStretch(1)

        v_layout.addWidget(self.image_label)
        v_layout.addStretch(0)
        main_layout.addStretch(1)
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)

    def load_image_from_url(self, image_url: str):
        response = requests.get(image_url)
        response.raise_for_status()

        pixmap = QPixmap()
        pixmap.loadFromData(response.content)

        scaled = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        self.current_wallpaper = {"type": "image", "value": image_url}

    def apply_wallpaper(self, payload: dict):
        if not payload:
            return
        wall_type = payload.get("type")
        val = payload.get("value")
        if wall_type == "color" and val:
            pixmap = QPixmap(self.image_label.size())
            pixmap.fill(QColor(val))
            self.image_label.setPixmap(pixmap)
            self.current_wallpaper = payload
        elif wall_type == "image" and val:
            if val.startswith("http://") or val.startswith("https://"):
                try:
                    self.load_image_from_url(val)
                except Exception as e:
                    print(f"Error loading image from URL: {e}")
            else:
                pixmap = QPixmap(val)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        self.image_label.size(),
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled)
                    self.current_wallpaper = payload

    def open_wallpaper_dialog(self):
        old_wallpaper = self.current_wallpaper
        parent_window = self.window() if self.window() else self
        dialog = WallpaperDialog(parent_window)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.wallpaper_selected.connect(self.apply_wallpaper)

        if dialog.exec() == QDialog.Accepted:
            selected = dialog.get_selected()
            if selected:
                self.apply_wallpaper(selected)
        else:
            if old_wallpaper:
                self.apply_wallpaper(old_wallpaper)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qss_path = "banner.qss" if os.path.exists("banner.qss") else os.path.join("APP", "banner.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    window = BannerFrame()
    urls = fetch_urls()
    if urls and "japan" in urls:
        window.load_image_from_url(urls["japan"])
    window.show()
    app.exec()