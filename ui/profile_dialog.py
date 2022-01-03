import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from config.profile import ProfileManager
from database.profile import ProfileDb
from database.temp import TempDb
from services.crypto import CryptoManager
from services.settings import Settings, SettingsHandler
import tkinter
from tkinter import filedialog
from services.storage import Storage
from services.time import Time


class ProfileDialog(QDialog):

    def __init__(self, parent_, ph, mode, db = None, settings: Settings = None, crypto = None):
        super(ProfileDialog, self).__init__(parent_)
        self.parent_ = parent_
        self.ph = ph
        self.mode = mode
        self.db = db
        self.settings = settings
        self.crypto = crypto

        self.setWindowTitle("Profile")
        self.setMinimumSize(833, 250)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        self.formGroupBox = QGroupBox("Profile Settings")
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setFixedWidth(208)
        self.readLineEdit = QLineEdit()
        self.writeLineEdit = QLineEdit()
        self.showBtn = QPushButton('show')
        self.writeWidget = QWidget()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.writeLineEdit, 2)
        hlayout.addWidget(self.showBtn)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.writeWidget.setLayout(hlayout)
        self.modeCheck = QCheckBox()
        self.syncSpinBar = QSpinBox()
        self.syncSpinBar.setFixedWidth(83)
        self.syncSpinBar.setRange(0, 3600)
        self.createForm()

        self.actionGroupBox = QGroupBox("Actions")
        grid = QGridLayout()
        self.deleteBtn = QPushButton('Delete Profile')
        self.deleteBtn.setStyleSheet("""
                QPushButton {
                  color: red;
                }
            """
        )
        self.passwdBtn = QPushButton('Update Password')
        self.cloneBtn = QPushButton('Clone Profile')
        self.exportBtn = QPushButton('Export')
        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 4)
        grid.setColumnStretch(2, 4)
        grid.addWidget(self.deleteBtn,0,0)
        grid.addWidget(self.cloneBtn,0,1)
        grid.addWidget(self.exportBtn,0,2)
        grid.addWidget(self.passwdBtn,1,0)
        self.actionGroupBox.setLayout(grid)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.actionGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.attach_handlers()
        self.initialize()

    def attach_handlers(self):
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)
        self.cloneBtn.clicked.connect(self.clone_profile)
        self.deleteBtn.clicked.connect(self.delete_profile)
        self.passwdBtn.clicked.connect(self.change_password)
        self.showBtn.clicked.connect(self.decrypt_write_config)
        self.exportBtn.clicked.connect(self.export_profile)

    def get_time_suffix(self):
        return str(Time().get_time_in_micro() % 10000000)

    def export_profile(self):
        if type(self.db) is ProfileDb:
            try:
                storage = Storage()
                init = '{}_{}.backup.db'.format(self.db.name, self.get_time_suffix())
                root = tkinter.Tk()
                root.withdraw()
                file = filedialog.asksaveasfilename(initialdir=storage.get_backup_dir(), initialfile=init, filetypes= [('Database File', '.db')])
                if file != None and len(file) > 0:
                    if not file.endswith('.db'):
                        file = file + '.db'
                    self.db.export(file)
                print(file)
            except:
                pass

    def decrypt_write_config(self):
        crypto = CryptoManager(self.db.Session)
        def on_status(status):
            if status == 'correct' or status == 'default':
                config = self.settings.write_config.removeprefix('[REDACTED]')
                config = crypto.decrypt_with_key(config)
                self.writeLineEdit.setText(config)
        self.ph.ui_config.validate_password(crypto,  "no-reset", self.settings.is_remote_write(), on_status)

    def hide_write_show(self):
        self.showBtn.hide()

    def show_write_show(self):
        self.showBtn.show()

    def hide_actions(self):
        self.actionGroupBox.hide()

    def show_actions(self):
        self.actionGroupBox.show()

    def change_password(self):
        self.ph.ui_config.password_update(self.settings.is_remote_write, self.crypto)

    def get_text(self, input):
        text = None
        input = input.text()
        if input != None:
            input = str(input).strip()
        if input != "":
            text = input
        return text

    def clone_profile(self):
        old = self.settings.clone()
        old.name = None
        dialog = ProfileDialog(self.parent_, self.ph, 'new', self.db, old)
        self.close()
        dialog.show()
        print('show dialog')

    def delete_profile(self):
        result = QMessageBox.critical(self.parent_, 'Warning', '(Hint! You might want to export the profile before deleting)\n\nThis process is irreversible. Are you sure you want to delete this Profile?', QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            profile = ProfileManager()
            profile.delete_current_profile()
            self.ph.initialize()
            self.db.delete()
            self.close()

    def on_accept(self):
        name = self.get_text(self.nameLineEdit)
        read = self.get_text(self.readLineEdit)
        write = self.get_text(self.writeLineEdit)
        read_only = self.modeCheck.isChecked()
        sync = self.syncSpinBar.value() * 1000

        old = Settings()
        if self.mode == 'update':
            old = self.settings

        if name == None: return self.ph.ui_config.show_message("Please, enter a Profile Name", long=False, error = True)
        if read == None and write != None: return self.ph.ui_config.show_message("When including write config, read config should also be provided", long=False, error = True)

        new = old.clone()
        new.name = name
        new.read_config = read
        new.write_config = write
        new.read_only = read_only
        new.sync_rate = sync


        if not old.equal(new):
            db = self.db if self.db != None else TempDb().load()
            self.sh = SettingsHandler(self.ph.ui_config, old, new, db, self.ph, self.on_finish)
            self.sh.apply_settings()
        else: self.close()

    def on_finish(self):
        self.ph.initialize()
        self.close()

    def createForm(self):
        layout = QFormLayout()
        layout.addRow(QLabel("Profile Name"), self.nameLineEdit)
        layout.addRow(QLabel("Read Config"), self.readLineEdit)
        layout.addRow(QLabel("Write Config"), self.writeWidget)
        layout.addRow(QLabel("Read only"), self.modeCheck)
        layout.addRow(QLabel("Sync Rate (sec)"), self.syncSpinBar)
        self.formGroupBox.setLayout(layout)

    def initialize(self):
        if self.mode == 'update':
            if self.crypto == None or not self.crypto.is_loaded() or self.settings == None or self.db == None:
                self.close()
            if self.settings.is_remote_read() or self.settings.read_only:
                self.passwdBtn.hide()
            self.populate_form()
        if self.mode == 'new':
            if self.settings == None:
                self.close()
            self.hide_actions()
            self.populate_form()

    def populate_form(self):
        self.nameLineEdit.setText(self.settings.name)
        self.readLineEdit.setText(self.settings.read_config)
        self.modeCheck.setChecked(self.settings.read_only)
        self.syncSpinBar.setValue(math.floor(self.settings.sync_rate / 1000))
        if self.settings.is_write_encrypted():
            self.show_write_show()
            self.writeLineEdit.setText('[ENCRYPTED]')
        else:
            self.writeLineEdit.setText(self.settings.write_config)
            self.hide_write_show()
