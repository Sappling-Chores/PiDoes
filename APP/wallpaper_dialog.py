# This file is AI generated

import sys
import os
import json
from typing import Optional, Dict, Any, List

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
    clicked = Signal(dict)  # Emits tile info payload dict on click

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

        self._selected = False
        self._hovered = False
        self.pixmap: Optional[QPixmap] = None
        self.is_loading = False

        self.setFixedSize(56, 56)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        if self.tile_type == "image" and self.network_manager:
            self._load_remote_image()

    def _load_remote_image(self):
        """Fetch remote image asynchronously using QNetworkAccessManager."""
        if not self.value or not self.network_manager:
            return
        self.is_loading = True
        request = QNetworkRequest(QUrl(self.value))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._on_image_downloaded(reply))

    def _on_image_downloaded(self, reply: QNetworkReply):
        self.is_loading = False
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pix = QPixmap()
            if pix.loadFromData(data):
                self.pixmap = pix
                self.update()
        reply.deleteLater()

    def set_selected(self, selected: bool):
        if self._selected != selected:
            self._selected = selected
            self.update()

    def is_selected(self) -> bool:
        return self._selected

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
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
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = self.rect()
        margin = 4 if self._selected else 2
        content_rect = QRectF(rect).adjusted(margin, margin, -margin, -margin)
        corner_radius = 4.0

        # Create rounded clipping path for content
        path = QPainterPath()
        path.addRoundedRect(content_rect, corner_radius, corner_radius)

        painter.save()
        painter.setClipPath(path)

        if self.tile_type == "color":
            color = QColor(self.value)
            painter.fillRect(content_rect, color)
        elif self.tile_type == "image":
            if self.pixmap and not self.pixmap.isNull():
                # Center-crop & scale image to fill tile
                scaled = self.pixmap.scaled(
                    int(content_rect.width()),
                    int(content_rect.height()),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                x = content_rect.x() + (content_rect.width() - scaled.width()) / 2.0
                y = content_rect.y() + (content_rect.height() - scaled.height()) / 2.0
                painter.drawPixmap(int(x), int(y), scaled)
            else:
                # Loading / placeholder style
                painter.fillRect(content_rect, QColor("#2d2d3a"))
                if self.is_loading:
                    painter.setPen(QColor("#666677"))
                    painter.drawText(content_rect, Qt.AlignCenter, "...")
        painter.restore()

        # Draw borders & selection indicators
        if self._selected:
            # Outer selection ring (Windows 11 double border highlight)
            ring_rect = QRectF(rect).adjusted(1, 1, -1, -1)
            pen = QPen(QColor("#409eff"), 2.5)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(ring_rect, corner_radius + 2, corner_radius + 2)

            # Inner subtle contrast border
            inner_pen = QPen(QColor("#ffffff"), 1.0)
            painter.setPen(inner_pen)
            painter.drawRoundedRect(content_rect, corner_radius, corner_radius)

        elif self._hovered:
            pen = QPen(QColor("#ffffff"), 1.5)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(content_rect, corner_radius, corner_radius)
        else:
            # Subtle default border for static colors
            border_color = QColor("#000000")
            border_color.setAlpha(60)
            pen = QPen(border_color, 1.0)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(content_rect, corner_radius, corner_radius)


class WallpaperDialog(QDialog):
    """
    A PySide6 Dialog displaying a grid of clickable solid color & image wallpaper previews.
    """
    wallpaper_selected = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Theme")
        self.setMinimumSize(340, 400)
        self.resize(360, 440)
        self.setStyleSheet("""
            QDialog {
                background-color: #202020;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #3c3c3c;
                border-radius: 12px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: 500;
                color: #ffffff;
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
                background-color: #333333;
                color: #ffffff;
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
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton#cancelButton:hover {
                background-color: #383838;
                color: white;
            }
        """)

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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 14)
        main_layout.setSpacing(12)

        # Dialog Title & Close Button Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Theme", self)
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        close_btn = QPushButton("✕", self)
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)

        main_layout.addLayout(header_layout)

        # Scrollable Grid Area
        self.scroll_area = QScrollArea(self)
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

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.apply_button = QPushButton("Select", self)
        self.apply_button.setObjectName("applyButton")
        self.apply_button.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_button)

        main_layout.addLayout(button_layout)

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

        # Pre-select sky blue by default (matching the reference image highlight)
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
