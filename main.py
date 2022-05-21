from PyQt5.QtWidgets import QApplication, QMainWindow

from src.ui import App


if __name__ == '__main__':
    app = QApplication([])
    window = QMainWindow()
    window.setGeometry(0, 1000, 2000, 1000)
    window.show()
    ex = App(window)
    app.exec()
