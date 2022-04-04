# coding=utf-8
import os
import sys

from scapy import all as cap

from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6.QtWidgets import QMainWindow
from ui import ui
from logger import logger

DIRNAME = os.path.dirname(os.path.abspath(__file__))
VERSION = "0.0.1"


class MainWindow(QMainWindow):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"Sniffer v{VERSION}")
        self.setWindowIcon(QtGui.QIcon(os.path.join(DIRNAME, 'images/logo.png')))
        self.init_interfaces()
        self.sniffing = False

    def init_interfaces(self):
        for face in cap.get_working_ifaces():
            self.ui.interfaceBox.addItem(face.name)

        self.ui.startButton.clicked.connect(self.start_click)

    def get_iface(self):
        idx = self.ui.interfaceBox.currentIndex()
        iface = cap.get_working_ifaces()[idx]
        return iface

    def start_click(self):
        logger.debug("start button was clicked")
        if self.sniffing:
            self.ui.startButton.setText("Start")
            self.sniffing = False
            self.ui.interfaceBox.setEnabled(True)
            return

        self.ui.startButton.setText("Stop")
        self.ui.interfaceBox.setEnabled(False)
        self.sniffing = True

        iface = self.get_iface()
        logger.debug(iface)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
