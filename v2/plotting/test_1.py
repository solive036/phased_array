import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Window')
        self.setGeometry(100, 100, 100, 100)
        layout = QVBoxLayout()
        self.label = QLabel('Hello')
        layout.addWidget(self.label)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())