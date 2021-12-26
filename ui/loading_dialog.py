from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from ui.waiting_spinner import QtWaitingSpinner

class LoaderHandler(object):

    def __init__(self, parent) -> None:
        super().__init__()
        self.finished = True
        self.loader = None
        self.parent = parent

    def start(self, reopen = False):
        if self.finished or reopen:
            self.finished = False
            self.loader = LoadingDialog(self.parent, self.on_close)
            self.loader.show()

    def finish(self):
        if not self.finished:
            self.finished = True
            if self.loader != None:
                self.loader.close()

    def on_close(self):
        if not self.finished:
            self.start(reopen=True)

class LoadingDialog(QDialog):

    def __init__(self, parent_, closed):
        super(LoadingDialog, self).__init__(parent_)
        self.parent_ = parent_
        self.is_finished = False
        self.closed = closed

        self.setWindowTitle(" ")
        self.setFixedSize(500, 100)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        self.loader = QtWaitingSpinner(centerOnParent=False)
        self.loader.setColor(QColor(Qt.black))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.loader)
        mainLayout.addWidget(QLabel("Loading, Please wait..."))
        mainLayout.setContentsMargins(80, 0, 50, 0)
        self.setLayout(mainLayout)
        self.loader.start()
        self.rejected.connect(self.on_close)

    def on_close(self):
        self.closed()
