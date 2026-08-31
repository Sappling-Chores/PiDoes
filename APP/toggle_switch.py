from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRectF, Signal
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QAbstractButton, QApplication
import sys

class ToggleSwitch(QAbstractButton):
    toggled_signal = Signal(bool)

    def __init__(self, parent=None, width=44, height=22):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(width, height)

        # Colors — tweak these to match your theme
        self._track_off = QColor("#45475a")
        self._track_on = QColor("#2196F3")
        self._knob_color = QColor("#ffffff")

        self._knob_pos = 2  # x-offset of the knob, animated

        self._anim = QPropertyAnimation(self, b"knob_pos", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        self.toggled_signal.emit(self.isChecked())
        end = self.width() - self.height() + 2 if self.isChecked() else 2
        self._anim.stop()
        self._anim.setStartValue(self._knob_pos)
        self._anim.setEndValue(end)
        self._anim.start()

    # --- animatable property ---
    def get_knob_pos(self):
        return self._knob_pos

    def set_knob_pos(self, pos):
        self._knob_pos = pos
        self.update()

    knob_pos = Property(float, get_knob_pos, set_knob_pos)

    # --- painting ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        track_rect = QRectF(0, 0, self.width(), self.height())
        track_color = self._track_on if self.isChecked() else self._track_off
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, self.height() / 2, self.height() / 2)

        knob_diameter = self.height() - 4
        knob_rect = QRectF(self._knob_pos, 2, knob_diameter, knob_diameter)
        knob_color = QColor("#000000") if self.isChecked() else self._knob_color
        painter.setBrush(knob_color)
        painter.drawEllipse(knob_rect)

    def setChecked(self, checked):
        super().setChecked(checked)
        self._knob_pos = (self.width() - self.height() + 2) if checked else 2
        self.update()


if __name__ == "__main__":
  try:
    from paths import SETTING_QSS
  except ImportError:
    from APP.paths import SETTING_QSS

  app = QApplication(sys.argv)
  
  if SETTING_QSS.exists():
    with open(SETTING_QSS, "r") as f:
      app.setStyleSheet(f.read())
  window = ToggleSwitch()
  window.show()
  
  app.exec()