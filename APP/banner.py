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
from PySide6.QtCore import Qt, QSize, Signal

try:
    from wallpaper_dialog import WallpaperDialog
    from paths import BANNER_QSS, WALLPAPER_URLS_JSON, DOTS_THREE_SVG, GEAR_SVG, SUN_SVG, STAR_SVG, NOTEPAD_SVG
except ImportError:
    from APP.wallpaper_dialog import WallpaperDialog
    from APP.paths import BANNER_QSS, WALLPAPER_URLS_JSON, DOTS_THREE_SVG, GEAR_SVG, SUN_SVG, STAR_SVG, NOTEPAD_SVG

date = datetime.now()
day_date = date.strftime("%A, %d %B").lstrip()

def fetch_urls():
    try:
        with open(WALLPAPER_URLS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("wallpapers", {})
    except Exception:
        return {}

class BannerFrame(QWidget):
    settings_clicked = Signal()  # connect this to open settings

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BannerFrame")
        self.current_wallpaper = None

        if BANNER_QSS.exists():
            with open(BANNER_QSS, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.frame = QFrame()
        v_layout = QVBoxLayout(self.frame)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)
        self.frame.setFixedSize(1280, 800)

        self.image_label = QLabel(self.frame)
        self.image_label.setFixedSize(1280, 800)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_layout = QVBoxLayout(self.image_label)
        image_layout = self.image_layout
        image_layout.setContentsMargins(32, 24, 32, 24)

        icon_path = DOTS_THREE_SVG

        self.wallpaper_btn = QPushButton(self.image_label)
        self.wallpaper_btn.setObjectName("wallpaper-btn")
        if icon_path.exists():
            self.wallpaper_btn.setIcon(QIcon(str(icon_path)))
            self.wallpaper_btn.setIconSize(QSize(32, 32))
        else:
            self.wallpaper_btn.setText("...")
        self.wallpaper_btn.setFixedSize(44, 44)
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

        # ── Left sidebar ─────
        sun_path = SUN_SVG
        star_path = STAR_SVG
        notepad_path = NOTEPAD_SVG
        gear_path = GEAR_SVG

        sidebar = QWidget()
        sidebar.setMinimumWidth(130)
        sidebar.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QPushButton {
                background: transparent;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                color: #333333;
                text-align: left;
                padding: 0 8px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 30);
                border-radius: 6px;
                color: #000000;
            }
            QPushButton:pressed {
                background: rgba(0, 0, 0, 55);
            }
            QPushButton[active="true"] {
                background: rgba(0, 0, 0, 25);
                border-radius: 6px;
                color: #000000;
                font-weight: bold;
            }
            QPushButton#sidebar-last-week-btn, QPushButton#sidebar-older-btn {
                padding-left: 28px;
                font-size: 12px;
                color: #555555;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 16)

        # 1. My Day button
        self.my_day_btn = QPushButton()
        self.my_day_btn.setObjectName("sidebar-my-day-btn")
        self.my_day_btn.setFixedHeight(40)
        if sun_path.exists():
            self.my_day_btn.setIcon(QIcon(str(sun_path)))
            self.my_day_btn.setIconSize(QSize(20, 20))
        self.my_day_btn.setText(" My Day")
        self.my_day_btn.setProperty("active", True)
        sidebar_layout.addWidget(self.my_day_btn)

        # 2. Important button
        self.important_btn = QPushButton()
        self.important_btn.setObjectName("sidebar-important-btn")
        self.important_btn.setFixedHeight(40)
        if star_path.exists():
            self.important_btn.setIcon(QIcon(str(star_path)))
            self.important_btn.setIconSize(QSize(20, 20))
        self.important_btn.setText(" Important")
        self.important_btn.setProperty("active", False)
        sidebar_layout.addWidget(self.important_btn)

        # 3. Old Tasks button
        self.old_tasks_btn = QPushButton()
        self.old_tasks_btn.setObjectName("sidebar-old-tasks-btn")
        self.old_tasks_btn.setFixedHeight(40)
        if notepad_path.exists():
            self.old_tasks_btn.setIcon(QIcon(str(notepad_path)))
            self.old_tasks_btn.setIconSize(QSize(20, 20))
        self.old_tasks_btn.setText(" Old Tasks")
        self.old_tasks_btn.setProperty("active", False)
        sidebar_layout.addWidget(self.old_tasks_btn)

        # 3a. Last Week (subcategory)
        self.last_week_btn = QPushButton()
        self.last_week_btn.setObjectName("sidebar-last-week-btn")
        self.last_week_btn.setFixedHeight(32)
        self.last_week_btn.setText(" Last Week")
        self.last_week_btn.setProperty("active", False)
        sidebar_layout.addWidget(self.last_week_btn)

        # 3b. Older (subcategory)
        self.older_btn = QPushButton()
        self.older_btn.setObjectName("sidebar-older-btn")
        self.older_btn.setFixedHeight(32)
        self.older_btn.setText(" Older")
        self.older_btn.setProperty("active", False)
        sidebar_layout.addWidget(self.older_btn)

        sidebar_layout.addStretch(1)  # push settings button to the bottom

        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("sidebar-settings-btn")
        self.settings_btn.setFixedHeight(40)
        if gear_path.exists():
            self.settings_btn.setIcon(QIcon(str(gear_path)))
            self.settings_btn.setIconSize(QSize(20, 20))
        self.settings_btn.setText(" Setting")
        self.settings_btn.clicked.connect(self.settings_clicked)
        sidebar_layout.addWidget(self.settings_btn)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)

        # Default wallpaper: blue-violet
        self.apply_wallpaper({"type": "color", "value": "#7c90db"})

    def set_view(self, mode: str):
        if mode == "my_day":
            self.label.setText("My Day")
            self.date_label.setVisible(True)
        elif mode == "important":
            self.label.setText("Important")
            self.date_label.setVisible(False)
        elif mode in ("old_tasks", "last_week", "older"):
            title_map = {
                "old_tasks": "Old Tasks",
                "last_week": "Last Week Tasks",
                "older": "Older Tasks"
            }
            self.label.setText(title_map[mode])
            self.date_label.setVisible(False)

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
        dialog = WallpaperDialog(parent_window, current_wallpaper=self.current_wallpaper)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.wallpaper_selected.connect(self.apply_wallpaper)

        btn = self.wallpaper_btn
        btn_global_bottom_right = btn.mapToGlobal(btn.rect().bottomRight())
        dialog_x = btn_global_bottom_right.x() - dialog.width()
        dialog_y = btn_global_bottom_right.y() + 6
        dialog.move(dialog_x, dialog_y)

        if dialog.exec() == QDialog.Accepted:
            selected = dialog.get_selected()
            if selected:
                self.apply_wallpaper(selected)
        else:
            if old_wallpaper:
                self.apply_wallpaper(old_wallpaper)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if BANNER_QSS.exists():
        with open(BANNER_QSS, "r") as f:
            app.setStyleSheet(f.read())
    window = BannerFrame()
    urls = fetch_urls()
    if urls and "japan" in urls:
        window.load_image_from_url(urls["japan"])
    window.show()
    app.exec()