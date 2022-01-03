from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel
from services.settings import Settings

class StatusBarManager(object):
    def __init__(self, ph, statusBar: QtWidgets.QHBoxLayout) -> None:
        super().__init__()
        self.statusBar = statusBar
        self.ph = ph
        label1 = QLabel("Status: ")
        self.conn_status = QtWidgets.QPushButton()
        self.conn_status.setText("Offline    ")
        syncIcon = self.getIcon("static/icon/cloud-sync.svg")
        self.syncIcon = syncIcon
        self.push_status = QLabel("  0/0")
        self.statusBar.addWidget(label1, 0, alignment= QtCore.Qt.AlignLeft)
        self.statusBar.addWidget(self.conn_status, 0, alignment= QtCore.Qt.AlignLeft)
        self.statusBar.addWidget(syncIcon, 0, alignment= QtCore.Qt.AlignLeft)
        self.statusBar.addWidget(self.push_status, 0, alignment= QtCore.Qt.AlignLeft)
        upIcon = self.getIcon("static/icon/up-arrow.svg")
        self.upIcon = upIcon
        self.statusBar.addWidget(upIcon, 0, alignment= QtCore.Qt.AlignLeft)
        self.pull_status = QLabel("  Pending")
        self.statusBar.addWidget(self.pull_status, 0, alignment= QtCore.Qt.AlignLeft)
        downIcon = self.getIcon("static/icon/down-arrow.svg")
        self.downIcon = downIcon
        self.statusBar.addWidget(downIcon, 0, alignment= QtCore.Qt.AlignLeft)
        self.statusBar.addStretch(0)

        self.sync_status = QtWidgets.QPushButton()
        self.sync_status.setText("Syncronizing    ")
        self.statusBar.addWidget(self.sync_status, 0, alignment= QtCore.Qt.AlignRight)

        self.unlock = QtWidgets.QPushButton()
        self.unlock.setText('Unlock to push')
        icon = QtGui.QIcon()
        icon.addPixmap(self.getPixMap("static/icon/lock.svg"))

        self.unlock.setIcon(icon)
        self.unlock.setObjectName("newprofile")
        self.statusBar.addWidget(self.unlock, 0, alignment= QtCore.Qt.AlignLeft)

        self.conn_status_info = ""
        self.sync_status_info = ""

        self.attach_listeners()

    def getPixMap(self, file):
        pix = QtGui.QPixmap(file)
        pix.setDevicePixelRatio(2.5)
        return pix

    def getIcon(self, file):
        icon = QtGui.QIcon()
        icon.addPixmap(self.getPixMap(file), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        button = QtWidgets.QPushButton()
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-style: none;
                border-width: 0px;
                border-radius: 0px;
                padding: 0px;
                min-width: 0px;
            }
            QPushButton:hover {
                background-color: transparent;
            }
            """
        )
        button.setIcon(icon)
        return button
        

    def attach_listeners(self):
        self.conn_status.clicked.connect(lambda: self.ph.ui_config.show_message(self.conn_status_info, long=False))
        self.sync_status.clicked.connect(lambda: self.ph.ui_config.show_message(self.sync_status_info, long=False))
        self.unlock.clicked.connect(lambda: self.ph.decrypt_write_config())

    def set_conn_status(self, status, info = None):
        self.conn_status.setText("{}    ".format(status))
        if info == None:
            info = status
        self.conn_status_info = info

    def set_sync_status(self, status, info = None):
        self.sync_status.setText("{}    ".format(status))
        if info == None:
            info = status
        self.sync_status_info = info

    def set_pull_status(self, status):
        self.pull_status.setText("  {}".format(status))

    def set_push_status(self, status):
        self.push_status.setText("  {}".format(status))

    def show_unlock(self):
        self.unlock.show()

    def hide_unlock(self):
        self.unlock.hide()

    def initialise(self, settings: Settings):
        self.set_pull_status('Pending')
        self.set_push_status('0/0')
        self.syncIcon.show()
        self.push_status.show()
        self.upIcon.show()
        self.pull_status.show()
        self.downIcon.show()
        self.sync_status.show()
        self.unlock.hide()
        self.set_conn_status('Offline')

        if settings.is_write_encrypted():
            self.show_unlock()
        else: self.hide_unlock()

        if settings.is_local():
            self.set_conn_status('Local')
            self.syncIcon.hide()
            self.push_status.hide()
            self.upIcon.hide()
            self.pull_status.hide()
            self.downIcon.hide()
            self.sync_status.hide()
        elif settings.is_remote_read():
            self.push_status.hide()
            self.upIcon.hide()
        

