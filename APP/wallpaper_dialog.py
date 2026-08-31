# This file is AI generated

import sys
import os
import json
from typing import Optional, Dict, Any, List

try:
    from paths import URLS_JSON
except ImportError:
    from APP.paths import URLS_JSON

from PySide6.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QScrollArea, QFrame, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRectF, QSize, QUrl
from PySide6.QtGui import QPainter, QColor, QPixmap, QPen, QBrush, QPainterPath
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Curated static theme colors (matching the reference palette)
STATIC_COLORS = [
    "#7c90db",  # Blue-Violet
    "#b877bf",  # Purple / Lavender
    "#e76a8b",  # Coral Pink
    "#e7675e",  # Salmon Red
    "#47a979",  # Emerald Green
    "#3a9688",  # Teal / Seafoam
    "#87959e",  # Slate Grey
    "#91c7f6",  # Sky Blue
    "#cbb8e4",  # Soft Violet
    "#f3adbe",  # Light Pink
    "#f0b798",  # Peach
    "#92d7b4",  # Mint Green
    "#6fd3c6",  # Cyan / Turquoise
    "#b8cdd6",  # Ice Blue
]

# Fallback unsplash image URLs matching the reference design
FALLBACK_URLS = [
    "https://images.unsplash.com/photo-1482784160316-6eb046863ece?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1475776408506-9a5371e7a068?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1484995978482-cf913162930c?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1495710388177-22c73fa5f84e?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1707653056955-1835d800f4f7?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1617396900799-f4ec2b43c7ae?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1518495973542-4542c06a5843?crop=entropy&cs=srgb&fm=jpg&w=400&q=80",
    "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?crop=entropy&cs=srgb&fm=jpg&w=400&q=80"
]


class WallpaperTile(QWidget):
    """
    A square preview tile representing either a static color or an image wallpaper.
    Acts like an interactive button with hover and active selection ring styling.
    """
    clicked = Signal(dict)

    def __init__(
        self,
        tile_type: str,  # 'color' or 'image'
        value: str,      # hex code or image URL
        network_manager: Optional[QNetworkAccessManager] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.tile_type = tile_type
        self.value = value
        self.network_manager = network_manager

        self.pixmap: Optional[QPixmap] = None
        self.is_selected = False
        self.is_hovered = False
        self.is_loading = False

        self.setFixedSize(56, 56)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        if self.tile_type == "image" and self.network_manager:
            self._fetch_image()

    def _fetch_image(self):
        self.is_loading = True
        self.update()

        request = QNetworkRequest(QUrl(self.value))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._on_image_downloaded(reply))

    def _on_image_downloaded(self, reply: QNetworkReply):
        self.is_loading = False
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                self.pixmap = pixmap
        reply.deleteLater()
        self.update()

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            payload = {"type": self.tile_type, "value": self.value}
            self.clicked.emit(payload)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect())

        # 1. Base Tile Content
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)

        painter.save()
        painter.setClipPath(path)

        if self.tile_type == "color":
            painter.fillRect(rect, QColor(self.value))
        elif self.tile_type == "image":
            if self.pixmap and not self.pixmap.isNull():
                scaled = self.pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                x = (self.width() - scaled.width()) / 2
                y = (self.height() - scaled.height()) / 2
                painter.drawPixmap(int(x), int(y), scaled)
            else:
                painter.fillRect(rect, QColor("#e5e5e5"))
                if self.is_loading:
                    pen = QPen(QColor("#888888"), 2)
                    painter.setPen(pen)
                    painter.drawText(rect, Qt.AlignCenter, "...")

        # 2. Hover overlay tint
        if self.is_hovered and not self.is_selected:
            painter.fillRect(rect, QColor(255, 255, 255, 40))

        painter.restore()

        # 3. Selection Indicator Ring
        if self.is_selected:
            ring_pen = QPen(QColor("#0078d4"), 3)
            painter.setPen(ring_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 8, 8)


class WallpaperDialog(QDialog):
    """
    A PySide6 Dialog displaying a grid of clickable solid color & image wallpaper previews.
    """
    wallpaper_selected = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None, current_wallpaper: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self._current_wallpaper = current_wallpaper
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Theme")
        self.setMinimumSize(340, 400)
        self.resize(360, 440)

        self.network_manager = QNetworkAccessManager(self)
        self.tiles: List[WallpaperTile] = []
        self.selected_item: Optional[Dict[str, Any]] = None

        self._init_ui()
        self._load_wallpapers()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def _init_ui(self):
        # Outer dialog layout
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)

        # Solid background container card
        self.container_frame = QFrame(self)
        self.container_frame.setObjectName("dialogContainer")
        self.container_frame.setStyleSheet("""
            QFrame#dialogContainer {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 12px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: 600;
                color: #1a1a1a;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton#closeButton {
                background: transparent;
                color: #888888;
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton#closeButton:hover {
                background-color: #f0f0f0;
                color: #333333;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#scrollContainer {
                background-color: transparent;
            }
            QPushButton#applyButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 6px 18px;
                font-size: 12px;
            }
            QPushButton#applyButton:hover {
                background-color: #106ebe;
            }
            QPushButton#applyButton:pressed {
                background-color: #005a9e;
            }
            QPushButton#cancelButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton#cancelButton:hover {
                background-color: #e8e8e8;
                color: #1a1a1a;
            }
        """)

        main_layout = QVBoxLayout(self.container_frame)
        main_layout.setContentsMargins(18, 18, 18, 14)
        main_layout.setSpacing(12)

        # Dialog Title & Close Button Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Theme", self.container_frame)
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        close_btn = QPushButton("✕", self.container_frame)
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)

        main_layout.addLayout(header_layout)

        # Scrollable Grid Area
        self.scroll_area = QScrollArea(self.container_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.scroll_container = QWidget()
        self.scroll_container.setObjectName("scrollContainer")
        self.grid_layout = QGridLayout(self.scroll_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(8)
        self.grid_layout.setVerticalSpacing(8)

        self.scroll_area.setWidget(self.scroll_container)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # Bottom Button Bar
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.cancel_button = QPushButton("Cancel", self.container_frame)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.apply_button = QPushButton("Select", self.container_frame)
        self.apply_button.setObjectName("applyButton")
        self.apply_button.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_button)

        main_layout.addLayout(button_layout)
        dialog_layout.addWidget(self.container_frame)

    def _load_urls_from_json(self) -> List[str]:
        """Loads wallpaper URLs from urls.json (checks local dir and APP/urls.json) and deduplicates against fallbacks."""
        possible_paths = [
            "urls.json",
            os.path.join("APP", "urls.json"),
            os.path.join(os.path.dirname(__file__), "urls.json"),
            os.path.join(os.path.dirname(__file__), "APP", "urls.json")
        ]

        loaded_urls: List[str] = []
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    urls_entry = data.get("urls", [])
                    if isinstance(urls_entry, list) and len(urls_entry) > 0:
                        url_dict = urls_entry[0]
                        if isinstance(url_dict, dict):
                            loaded_urls = list(url_dict.values())
                            break
                except Exception as e:
                    print(f"[WallpaperDialog] Error reading {path}: {e}")

        def get_base_id(url_str: str) -> str:
            return url_str.split("?")[0].strip()

        seen_base_ids = set()
        deduped_urls: List[str] = []

        for u in loaded_urls:
            base_id = get_base_id(u)
            if base_id not in seen_base_ids:
                seen_base_ids.add(base_id)
                deduped_urls.append(u)

        for u in FALLBACK_URLS:
            base_id = get_base_id(u)
            if base_id not in seen_base_ids:
                seen_base_ids.add(base_id)
                deduped_urls.append(u)

        return deduped_urls

    def _load_wallpapers(self):
        """Populates the grid with static colors followed by image wallpapers."""
        columns = 5
        row = 0
        col = 0

        # 1. Populate Static Colors
        for color_hex in STATIC_COLORS:
            tile = WallpaperTile("color", color_hex, parent=self.scroll_container)
            tile.clicked.connect(self._on_tile_clicked)
            self.grid_layout.addWidget(tile, row, col)
            self.tiles.append(tile)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        # 2. Populate Image Wallpapers from urls.json / fallbacks
        image_urls = self._load_urls_from_json()
        for url in image_urls:
            tile = WallpaperTile("image", url, network_manager=self.network_manager, parent=self.scroll_container)
            tile.clicked.connect(self._on_tile_clicked)
            self.grid_layout.addWidget(tile, row, col)
            self.tiles.append(tile)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        # Pre-select tile matching current wallpaper; fall back to sky blue or first tile
        matched = False
        if self._current_wallpaper:
            ctype = self._current_wallpaper.get("type")
            cval = self._current_wallpaper.get("value")
            for tile in self.tiles:
                if tile.tile_type == ctype and tile.value == cval:
                    self._select_tile(tile)
                    matched = True
                    break
        if not matched:
            if len(self.tiles) > 7:
                self._select_tile(self.tiles[7])
            elif self.tiles:
                self._select_tile(self.tiles[0])

    def _on_tile_clicked(self, payload: dict):
        sender = self.sender()
        if isinstance(sender, WallpaperTile):
            self._select_tile(sender)
        self.selected_item = payload
        self.wallpaper_selected.emit(payload)

    def _select_tile(self, target_tile: WallpaperTile):
        for tile in self.tiles:
            tile.set_selected(tile == target_tile)
        self.selected_item = {"type": target_tile.tile_type, "value": target_tile.value}

    def get_selected(self) -> Optional[Dict[str, Any]]:
        """Returns the currently selected item payload dict."""
        return self.selected_item


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = WallpaperDialog()

    def on_selected(payload):
        print(f"Selected wallpaper: {payload}")

    dialog.wallpaper_selected.connect(on_selected)
    dialog.exec()
