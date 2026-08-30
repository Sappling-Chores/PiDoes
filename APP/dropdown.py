from PySide6.QtWidgets import QApplication, QWidget, QComboBox
import sys

app = QApplication(sys.argv)

window = QWidget()
window.resize(300, 200)

dropdown = QComboBox(window)

dropdown.addItems(["Apple", "Banana", "Orange", "Mango"])

dropdown.show()
window.show()

# This is a test file dont worry about this. 