# coding=utf-8
import os
import sys
from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6.QtWidgets import QMainWindow
from ui import ui

DIRNAME = os.path.dirname(os.path.abspath(__file__))
VERSION = "0.0.1"


class MainWindow(QMainWindow):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"Sniffer v{VERSION}")
        self.setWindowIcon(QtGui.QIcon(os.path.join(DIRNAME, 'images/logo.png')))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
