from config.profile import ProfileManager
from models.department import Department
from PyQt5 import QtWidgets
from services.crypto import CryptoManager


class UI_Config(object):
    def __init__(self, ui, profile: ProfileManager) -> None:
        super().__init__()
        self.ui = ui
        self.profile = profile
        self.dpts = []
        self.loading_profile = False
        self.dpt_profile = None

    def load_profiles(self):
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

    def validate_password(self, crypto: CryptoManager, mode, is_remote_write):
        status = crypto.load_keys()
        if status == "none":
            passwd = None
            while True:
                title = "Current Password?" if passwd == None else "Current Password? (Incorrect, Try Again!)"
                text, ok = QtWidgets.QInputDialog.getText(self.ui.centralWidget, "Attention", title, QtWidgets.QLineEdit.Password)
                if not ok:
                    break
                passwd = text
                status = crypto.load_keys(passwd)
                if status == 'correct':
                    break

        if status == 'default' and (mode == "local" or mode == "write"):
            self.password_update(is_remote_write, crypto)
        return status

    def password_update(self, is_remote_write, crypto):
        if not crypto.is_loaded():
            return
        new, ok = QtWidgets.QInputDialog.getText(self.ui.centralWidget, "Attention", "New Password?", QtWidgets.QLineEdit.Password)
        if not ok:
            # self.ui.show_message('Cancelled', False)
            return
        passwd = None
        while True:
            title = "Confirm New Password" if passwd == None else "Confirm New Password (Incorrect, Try Again!)"
            confirm, ok = QtWidgets.QInputDialog.getText(self.ui.centralWidget, "Attention", title, QtWidgets.QLineEdit.Password)
            passwd = confirm
            if not ok:
                self.ui.show_message('Cancelled', False)
                return
            if passwd == new:
                crypto.set_password(passwd, is_remote_write)
                # self.ui.show_message('Password change success!', False)
                break
