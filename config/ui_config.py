from config.profile import ProfileManager
from models.department import Department
from PyQt5 import QtWidgets
from services.crypto import CryptoManager
from ui.loading_dialog import LoaderHandler

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import math
from PyQt5.QtCore import QSize


class UI_Config(object):
    def __init__(self, ui, profile: ProfileManager) -> None:
        super().__init__()
        self.ui = ui
        self.profile = profile
        self.dpts = []
        self.loading_profile = False
        self.dpt_profile = None
        self.loader = LoaderHandler(self.ui.window)

    def load_profiles(self, settings):
        if settings.read_only:
            self.ui.mastersheet.hide()
        else: self.ui.mastersheet.show()

        if settings.allow_no_verify:
            self.ui.vButton.show()
        else:
            self.ui.vButton.setChecked(True)
            self.ui.vButton.hide()
        
        session = self.profile.pdb.Session()
        index = 0
        self.loading_profile = True
        for i in range(0, len(self.profile.profiles)):
            self.ui.profileSel.removeItem(i)
        for i in range(self.ui.profileSel.count()):
            self.ui.profileSel.removeItem(i)
        for i in range(0, len(self.profile.profiles)):
            pr = self.profile.profiles[i]
            if str(pr.id) == str(self.profile.profile.id):
                index = i
            if self.ui.profileSel.itemText(i) != "":
                self.ui.profileSel.setItemText(i, pr.name)
            else:
                self.ui.profileSel.addItem(pr.name)
        session.close()
        self.ui.profileSel.setCurrentIndex(index)
        self.load_departments(profile=str(self.profile.profile.id))
        self.loading_profile = False

    def load_departments(self, profile = None):
        c_code = ""
        index = 0
        c_dpt = self.ui.comboBoxz.currentIndex()
        if c_dpt > 0 and len(self.dpts) > 0:
            c_code = str(self.dpts[c_dpt - 1].code)
        is_init = profile != self.dpt_profile and profile != None
        for i in range(1, len(self.dpts) + 1):
            self.ui.comboBoxz.removeItem(i)
        session = self.profile.pdb.Session()
        self.dpts = session.query(Department).all()
        self.ui.dpts = self.dpts
        if profile != self.dpt_profile and len(self.dpts) == 1:
            index = 1
        for i in range(1, self.ui.comboBoxz.count()):
            self.ui.comboBoxz.removeItem(i)
        for i in range(1, self.ui.comboBoxz.count()):
            self.ui.comboBoxz.removeItem(i)
        for i in range(len(self.dpts)):
            dpt = self.dpts[i]
            if self.ui.comboBoxz.itemText(i + 1) != "":
                self.ui.comboBoxz.setItemText(i + 1, '{}: {}'.format(dpt.department, dpt.code))
            else:
                self.ui.comboBoxz.addItem('{}: {}'.format(dpt.department, dpt.code))
            if str(dpt.code) == c_code and not is_init:
                index = i + 1
        session.close()
        self.ui.comboBoxz.setCurrentIndex(index)
        if profile != None:
            self.dpt_profile = profile

    def validate_password(self, crypto: CryptoManager, mode, is_remote_write, on_status = lambda s: None):
        def on_load(status, passwd = None):
            self.loader.finish()
            if status == "none" or status == "wrong":
                title = "Password?" if passwd == None else "Password? (Incorrect, Try Again!)"
                text, ok = QtWidgets.QInputDialog.getText(self.ui.centralWidget, "Attention", title, QtWidgets.QLineEdit.Password)
                if ok:
                    self.loader.start()
                    passwd = text
                    self.thread, self.worker = crypto.new_crypto_worker(lambda worker: worker.load_crypto, lambda status: on_load(status, passwd), passwd)
                    return

            if status == 'default' and (mode == "local" or mode == "write"):
                self.password_update(is_remote_write, crypto, lambda: on_status(status))
            else:
                on_status(status)
        self.loader.start()
        self.thread, self.worker = crypto.new_crypto_worker(lambda worker: worker.load_crypto, on_load)

    def password_update(self, is_remote_write, crypto: CryptoManager, on_finish = lambda: None):
        if not crypto.is_loaded():
            return on_finish()
        new, ok = QtWidgets.QInputDialog.getText(self.ui.centralWidget, "Attention", "New Password?", QtWidgets.QLineEdit.Password)
        if not ok:
            # self.ui.show_message('Cancelled', False)
            return on_finish()
        passwd = None
        while True:
            title = "Confirm New Password" if passwd == None else "Confirm New Password (Incorrect, Try Again!)"
            confirm, ok = QtWidgets.QInputDialog.getText(self.ui.centralWidget, "Attention", title, QtWidgets.QLineEdit.Password)
            passwd = confirm
            if not ok:
                self.show_message('Cancelled', False) 
                return on_finish()
            if passwd == new:
                self.loader.start()
                def finish(_):
                    self.loader.finish()
                    on_finish()
                self.thread, self.worker = crypto.new_crypto_worker(lambda worker: worker.set_password, finish, passwd, is_remote_write)
                # self.ui.show_message('Password change success!', False)
                break

    def show_message(self, mes, long = True, error = False):
        if long:
            result = ScrollMessageBox(mes, self.get_size_from_ratio(2, 2))
            result.setWindowTitle("Info")
            result.exec_()
        elif not error:
            QMessageBox.information(self.ui.centralWidget, 'Info', mes)
        else:
            QMessageBox.critical(self.ui.centralWidget, 'Error', mes)
    
    def get_size_from_ratio(self, w = 1, h = 1):
        size = self.ui.centralWidget.sizeHint()
        return QSize(math.floor(size.width() / w), math.floor(size.height() / h))


class ScrollMessageBox(QMessageBox):
    def __init__(self, message, size):
        QMessageBox.__init__(self)
        self.setIcon(QMessageBox.Icon.Information)
        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QtWidgets.QWidget()
        scroll.setWidget(self.content)
        lay = QtWidgets.QVBoxLayout(self.content)
        text = QtWidgets.QLabel(message, self)
        lay.addWidget(text, 0, QtCore.Qt.AlignTop)
        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        scroll.setMinimumSize(size)
