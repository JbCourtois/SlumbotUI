from PyQt5.QtWidgets import QApplication

from src.ui import App


if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    app.exec_()
