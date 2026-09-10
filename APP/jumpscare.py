import sys
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QHBoxLayout
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import Qt, QTimer, QUrl

try:
  from paths import SCARY_IMAGE, JUMPSCARE_SOUND
except ImportError:
  from APP.paths import SCARY_IMAGE, JUMPSCARE_SOUND


class JumpscareWindow(QMainWindow):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Scary")
    self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

    self.frame = QFrame()
    self.frame.setStyleSheet(
      """
      QFrame{
        background:black;
      }
      """
    )

    h_layout = QHBoxLayout(self.frame)
    h_layout.setContentsMargins(0, 0, 0, 0)

    label = QLabel()
    if SCARY_IMAGE and Path(SCARY_IMAGE).exists():
      from PySide6.QtGui import QPixmap
      pixmap = QPixmap(str(SCARY_IMAGE))
      screen_size = QApplication.primaryScreen().size()
      scaled = pixmap.scaled(
        screen_size,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
      )
      label.setPixmap(scaled)
    label.setStyleSheet("QLabel { background-color: #000000; }")
    label.setAlignment(Qt.AlignCenter)

    h_layout.addStretch(1)
    h_layout.addWidget(label)
    h_layout.addStretch(1)
    self.setCentralWidget(self.frame)

    self.sound = QSoundEffect(self)
    if JUMPSCARE_SOUND and Path(JUMPSCARE_SOUND).exists():
      self.sound.setSource(QUrl.fromLocalFile(str(JUMPSCARE_SOUND)))
      self.sound.setVolume(1.0)
      self.sound.play()

    QTimer.singleShot(3000, self.close_jumpscare)

  def close_jumpscare(self):
    self.sound.stop()
    self.close()
    self.deleteLater()


def trigger_jumpscare():
  scare = JumpscareWindow()
  scare.showFullScreen()
  scare.show()
  return scare


if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = JumpscareWindow()
  window.showFullScreen()
  window.show()
  app.exec()