# coding=utf-8
import os
import sys
import time
from queue import Queue

from scapy import all as cap
from scapy.all import IP
from scapy.all import Padding
from scapy.all import Raw
from scapy.utils import hexdump
from scapy.arch.common import compile_filter

from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6.QtWidgets import QTableWidgetItem as QTItem
from PySide6.QtWidgets import QListWidgetItem as QLItem

from PySide6.QtWidgets import QMainWindow
from ui import main as main_ui
from ui import about as about_ui
from logger import logger

DIRNAME = os.path.dirname(os.path.abspath(__file__))
VERSION = "0.0.1"
MAXSIZE = 16
LOGO = os.path.join(DIRNAME, 'images/logo.png')


class Signal(QtCore.QObject):

    recv = QtCore.Signal(None)


class MainWindow(QMainWindow):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.sniffer = None
        self.counter = 0
        self.start_time = 0
        self.signal = Signal()
        self.queue = Queue()
        self.about = None

        self.setWindowTitle(f"Sniffer v{VERSION}")
        self.setWindowIcon(QtGui.QIcon(LOGO))
        self.init_interfaces()

    def init_interfaces(self):
        for face in cap.get_working_ifaces():
            self.ui.interfaceBox.addItem(face.name)

        # todo remove after test
        self.ui.interfaceBox.setCurrentIndex(4)

        self.ui.startButton.clicked.connect(self.start_click)
        self.ui.filterEdit.textEdited.connect(self.validate_filter)

        self.ui.packetTable.horizontalHeader().setStretchLastSection(True)
        self.ui.packetTable.cellPressed.connect(self.update_content)

        self.signal.recv.connect(self.update_packet)

        self.ui.actionAbout.triggered.connect(self.show_about)

    def show_about(self):
        if self.about:
            self.about.show()
            return
        self.about = QtWidgets.QDialog(self)
        self.about.ui = about_ui.Ui_Dialog()
        self.about.ui.setupUi(self.about)
        self.about.ui.version_label.setText(f"Sniffer v{VERSION}")
        self.about.ui.image_label.setPixmap(QtGui.QPixmap(LOGO))
        self.about.ui.image_label.setScaledContents(True)
        self.about.show()

    def get_iface(self):
        idx = self.ui.interfaceBox.currentIndex()
        iface = cap.get_working_ifaces()[idx]
        return iface

    def validate_filter(self, exp):
        if not exp:
            self.ui.filterEdit.setStyleSheet('')
            self.ui.startButton.setEnabled(True)
            return

        try:
            compile_filter(filter_exp=exp)
            # 输入框背景变绿
            self.ui.filterEdit.setStyleSheet('QLineEdit { background-color: rgb(33, 186, 69);}')
            self.ui.startButton.setEnabled(True)
        except Exception:
            # 将输入框背景变红
            self.ui.startButton.setEnabled(False)
            self.ui.filterEdit.setStyleSheet('QLineEdit { background-color: rgb(219, 40, 40);}')
            return

    def get_packet_layers(self, packet):
        counter = 0
        while True:
            layer = packet.getlayer(counter)
            if layer is None:
                break
            yield layer
            counter += 1

    def update_content(self, x, y):
        logger.debug("%s, %s clicked", x, y)
        item = self.ui.packetTable.item(x, 6)
        if not hasattr(item, 'packet'):
            return
        logger.debug(item)
        logger.debug(item.text())
        packet = item.packet
        self.ui.contentEdit.setText(hexdump(packet, dump=True))

        self.ui.listWidget.clear()
        for layer in self.get_packet_layers(packet):
            self.ui.listWidget.addItem(QLItem(layer.summary()))

    def update_packet(self):
        packet = self.queue.get(False)
        if not packet:
            return

        if self.ui.packetTable.rowCount() >= MAXSIZE:
            self.ui.packetTable.removeRow(0)

        row = self.ui.packetTable.rowCount()
        self.ui.packetTable.insertRow(row)

        # No.
        self.counter += 1
        self.ui.packetTable.setItem(row, 0, QTItem(str(self.counter)))

        # Time
        elapse = time.time() - self.start_time
        self.ui.packetTable.setItem(row, 1, QTItem(f"{elapse:2f}"))

        # source
        if IP in packet:
            src = packet[IP].src
            dst = packet[IP].dst
        else:
            src = packet.src
            dst = packet.dst

        self.ui.packetTable.setItem(row, 2, QTItem(src))

        # destination
        self.ui.packetTable.setItem(row, 3, QTItem(dst))

        # protocol

        layer = None
        for var in self.get_packet_layers(packet):
            if not isinstance(var, (Padding, Raw)):
                layer = var

        protocol = layer.name
        self.ui.packetTable.setItem(row, 4, QTItem(str(protocol)))

        # length
        length = f"{len(packet)}"
        self.ui.packetTable.setItem(row, 5, QTItem(length))

        # info

        info = str(packet.summary())
        item = QTItem(info)
        item.packet = packet
        self.ui.packetTable.setItem(row, 6, item)
        # input()
        # logger.debug(pkg)

    def sniff_action(self, packet):
        if not self.sniffer:
            return

        self.queue.put(packet)
        self.signal.recv.emit()

    def start_click(self):
        logger.debug("start button was clicked")
        if self.sniffer:
            self.sniffer.stop()
            self.sniffer = None
            self.ui.startButton.setText("Start")
            self.ui.interfaceBox.setEnabled(True)
            self.ui.filterEdit.setEnabled(True)
            return

        exp = self.ui.filterEdit.text()
        logger.debug("filter expression %s", exp)

        iface = self.get_iface()
        logger.debug("sniffing interface %s", iface)

        self.sniffer = cap.AsyncSniffer(
            iface=iface,
            prn=self.sniff_action,
            filter=exp,
        )

        self.sniffer.start()
        self.counter = 0
        self.start_time = time.time()

        self.ui.startButton.setText("Stop")
        self.ui.interfaceBox.setEnabled(False)
        self.ui.filterEdit.setEnabled(False)
        self.ui.packetTable.clearContents()
        self.ui.packetTable.setRowCount(0)
        self.ui.listWidget.clear()
        self.ui.contentEdit.clear()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
