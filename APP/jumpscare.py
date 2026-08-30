import time as t
import datetime
import smtplib
import requests
from PySide6.QtWidgets import QFrame, QMainWindow, QApplication, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QPixmap, QIcon
import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
image_path = BASE_DIR / "Assets" / "scary.png"
print(image_path)


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Scary")
    self.frame = QFrame()
    self.setWindowFlag(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    self.frame.setStyleSheet(
      """
      QFrame{
        background:black;
      }
      """
      
    )
    h_layout = QHBoxLayout(self.frame)
    label = QLabel()
    pixmap = QPixmap(str(image_path))
    scaled = pixmap.scaled(
      self.size(),
      Qt.KeepAspectRatio,
      Qt.SmoothTransformation
    )
    label.setStyleSheet(
      """
      QLabel{
        background: #000000;
      }
      """
      
    )
    self.sound = QSoundEffect()
    self.sound.setSource(QUrl.fromLocalFile("./Assets/scary.wav"))
    self.sound.setVolume(1)
    self.sound.play()
    label.setPixmap(scaled)
    h_layout.addStretch(1)
    h_layout.addWidget(label)
    h_layout.addStretch(1)
    self.setCentralWidget(self.frame)
    QTimer.singleShot(5000, self.close)
    
if __name__ == "__main__":
  app = QApplication(sys.argv)

  window = MainWindow()
  window.showFullScreen()
  window.show()

  app.exec()