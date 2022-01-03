import re, sys, math, os

os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

from transformers.master_sheet import MasterSheet
from transformers.spread_sheet import SpreadSheet
from transformers.student_list import StudentList
from transformers.list_upload import ListUpload
from transformers.summary_sheet import SummarySheet
from transformers.course_list import CourseList
from transformers.sample_data.result import user

from models.result import Result
from models.student import Student
from models.course import Course
from models.department import Department
from config.profile_handler import ProfileHandler
from services.storage import Storage
from services.time import Time
from services.stager import Stager
from services.crypto import CryptoManager

import tkinter as tk
from tkinter import filedialog

from json.decoder import JSONDecoder

class HLayout(object):
    def __init__(self, parent, name, margin_top) -> None:
        super().__init__()
        self.widget = QtWidgets.QWidget(parent)
        self.widget.setObjectName(name)
        self.hlayout = QtWidgets.QHBoxLayout(self.widget)
        self.hlayout.setObjectName("horizontalLayout_{}".format(name))
        self.hlayout.setContentsMargins(0, margin_top, 0, 0)

class Ui_centralWidget(object):
    def setupUi(self, window):
        window.setObjectName("window")
        self.window = window
        centralWidget = QtWidgets.QWidget(window)
        self.centralWidget = centralWidget
        window.setCentralWidget(centralWidget)
        centralWidget.setObjectName("centralWidget")
        centralWidget.setStyleSheet("""
            * {
                color: #000000;
                border: none;
            }
            #centralWidget {
                background: #4297A0;
            }
            QLineEdit {
                background: transparent;
                background: #EED6D3;
                border-style: outset;
                border-width: 0.83px;
                border-radius: 2.08px;
                border-color: black;
                min-width: 250px;
            }
            #appHeader {
                color: #F4EAE6;
            }
            QPushButton {
                background-color: #67595E;
                color: white;
                border-style: outset;
                border-width: 0.83px;
                border-radius: 6.25px;
                border-color: black;
                padding: 2.5px;
                min-width: 33.33px;
            }
            QPushButton:hover {
                background-color: #867c80;
            }
            #matNumberLineEdit {
                background: #F4EAE6;
                border-width: 0.83px;
                border-color: black;
                padding-left: 8.33px;
                padding-right: 4.16px;
            }
            #mastersheet{
                border-style: outset;
                border-width: 0.83px;
                border-radius: 6.25px;
                border-color: black;
            }
            #spreadsheet{
                border-style: outset;
                border-width: 0.83px;
                border-radius: 6.25px;
                border-color: black;
            }"""
        )

        self.menubar = QtWidgets.QMenuBar(window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 243, 7))
        self.menubar.setObjectName("menubar")
        self.menubar.setStyleSheet("""
                #menubar {
                    border-style: outset;
                    border-width: 0.83px;
                    border-color: grey white grey white;
                }
        
            """
        )
        self.menuPreferences = QtWidgets.QMenu(self.menubar)
        self.menuPreferences.setObjectName("menuPreferences")
        window.setMenuBar(self.menubar)

        self.setPreferencesAction = QtWidgets.QAction(window)
        self.setPreferencesAction.setObjectName("setPreferencesAction")
        self.menuPreferences.addAction(self.setPreferencesAction)

        self.setPreferencesAction2 = QtWidgets.QAction(window)
        self.setPreferencesAction2.setObjectName("setPreferencesAction2")
        self.menuPreferences.addAction(self.setPreferencesAction2)

        self.menubar.addAction(self.menuPreferences.menuAction())

        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.actionAbout = QtWidgets.QAction(window)
        self.actionAbout.setObjectName("actionAbout")
        self.menuHelp.addAction(self.actionAbout)

        self.actionHelp = QtWidgets.QAction(window)
        self.actionHelp.setObjectName("actionHelp")
        self.menuHelp.addAction(self.actionHelp)

        self.menubar.addAction(self.menuHelp.menuAction())


        self.verticalMain = QtWidgets.QVBoxLayout(centralWidget)
        self.verticalMain.setContentsMargins(0, 0, 0, 0)
        self.verticalMain.setSpacing(0)
        self.verticalMain.setObjectName("horizontalLayout")
        self.mainbody = QtWidgets.QWidget(centralWidget)
        self.mainbody.setObjectName("mainbody")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainbody)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerFrame = QtWidgets.QWidget(self.mainbody)
        self.headerFrame.setObjectName("headerFrame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.headerFrame)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = self.getIcon("static/icon/monitor.svg")
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.appHeader = QtWidgets.QLabel(self.headerFrame)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.appHeader.setFont(font)
        self.appHeader.setObjectName("appHeader")
        self.horizontalLayout_4.addWidget(self.appHeader, 1)
######

        self.profileSel = QtWidgets.QComboBox(self.headerFrame)
        self.profileSel.setMinimumSize(QtCore.QSize(200, 0))
        self.profileSel.setObjectName("profileSel")
        self.horizontalLayout_4.addWidget(self.profileSel, 0, QtCore.Qt.AlignRight)
        
        self.newprofile = QtWidgets.QPushButton(self.headerFrame)
        icon = QtGui.QIcon()
        icon.addPixmap(self.getPixMap("static/icon/add.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.newprofile.setIcon(icon)
        self.newprofile.setObjectName("newprofile")
        self.newprofile.setMinimumWidth(0)
        self.horizontalLayout_4.addWidget(self.newprofile, 0, QtCore.Qt.AlignRight)

        self.password = QtWidgets.QPushButton(self.headerFrame)
        icon = QtGui.QIcon()
        icon.addPixmap(self.getPixMap("static/icon/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.password.setIcon(icon)
        self.password.setObjectName("password")
        self.password.setMinimumWidth(0)
        self.horizontalLayout_4.addWidget(self.password, 0, QtCore.Qt.AlignRight)
######
        self.verticalLayout.addWidget(self.headerFrame)
        self.cardsFrame = QtWidgets.QWidget(self.mainbody)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cardsFrame.sizePolicy().hasHeightForWidth())
        self.cardsFrame.setSizePolicy(sizePolicy)
        self.cardsFrame.setObjectName("cardsFrame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.cardsFrame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.mastersheet = QtWidgets.QWidget(self.cardsFrame)
        self.mastersheet.setMinimumSize(QtCore.QSize(135, 0))
        self.mastersheet.setObjectName("mastersheet")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.mastersheet)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.headerWidget = QtWidgets.QWidget(self.mastersheet)
        self.headerWidget.setObjectName("headerWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.headerWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_6 = self.getIcon("static/icon/codepen.svg")
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6, 0, QtCore.Qt.AlignCenter)
        self.label_2 = QtWidgets.QLabel(self.headerWidget)
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2, 0, QtCore.Qt.AlignCenter)
        self.verticalLayout_4.addWidget(self.headerWidget, 0, QtCore.Qt.AlignTop)
        self.widget_3 = QtWidgets.QWidget(self.mastersheet)
        self.widget_3.setMinimumSize(QtCore.QSize(104, 42))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_8 = QtWidgets.QLabel(self.widget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_6.addWidget(self.label_8)
        self.comboBox = QtWidgets.QComboBox(self.widget_3)
        self.comboBox.setMinimumSize(QtCore.QSize(50, 0))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_6.addWidget(self.comboBox)
        self.verticalLayout_4.addWidget(self.widget_3)
        self.widget = QtWidgets.QWidget(self.mastersheet)
        self.widget.setObjectName("widget")
        self.formLayout = QtWidgets.QFormLayout(self.widget)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setFormAlignment(QtCore.Qt.AlignBottom)
        self.formLayout.setAlignment(QtCore.Qt.AlignBottom)
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setMinimumSize(QtCore.QSize(83, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
#       
        self.delButton = QtWidgets.QCheckBox(self.widget)
        self.delButton.setObjectName("delButton")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.delButton)

        self.uploadButton = QtWidgets.QPushButton(self.widget)
        icon = QtGui.QIcon()
        icon.addPixmap(self.getPixMap("static/icon/upload.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.uploadButton.setIcon(icon)
        self.uploadButton.setObjectName("uploadButton")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.uploadButton)

        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.selectFileButton = QtWidgets.QPushButton(self.widget)
        self.selectFileButton.setObjectName("selectFileButton")
        
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.selectFileButton)
        self.verticalLayout_4.addWidget(self.widget)
        self.horizontalLayout_2.addWidget(self.mastersheet, 0, QtCore.Qt.AlignLeft)
        self.spreadsheet = QtWidgets.QWidget(self.cardsFrame)
        self.spreadsheet.setMinimumSize(QtCore.QSize(138, 0))
        self.spreadsheet.setObjectName("spreadsheet")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.spreadsheet)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.headerWidget_2 = QtWidgets.QWidget(self.spreadsheet)
        self.headerWidget_2.setObjectName("headerWidget_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.headerWidget_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_7 = self.getIcon("static/icon/file-text.svg")
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_5.addWidget(self.label_7, 0, QtCore.Qt.AlignCenter)
        self.label_3 = QtWidgets.QLabel(self.headerWidget_2)
        self.label_3.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3, 1, QtCore.Qt.AlignTop)
        self.verticalLayout_5.addWidget(self.headerWidget_2)
        self.widget_2 = QtWidgets.QWidget(self.spreadsheet)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.widget_z = HLayout(self.widget_2, 'widget_z', 0)        

        self.label_z = QtWidgets.QLabel(self.widget_z.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_z.setFont(font)
        self.label_z.setObjectName("label_z")

        self.comboBoxz = QtWidgets.QComboBox(self.widget_z.widget)
        self.comboBoxz.setObjectName("comboBoxz")
        self.comboBoxz.addItem("Select Department:")

        self.widget_z.hlayout.addWidget(self.comboBoxz, 4)
        self.verticalLayout_2.addWidget(self.widget_z.widget, 0, QtCore.Qt.AlignTop)

        self.shButton = QtWidgets.QCheckBox(self.widget_2)
        self.shButton.setObjectName("shButton")
        self.shButton.setChecked(True)
        self.vButton = QtWidgets.QCheckBox(self.widget_2)
        self.vButton.setObjectName("vButton")
        self.vButton.setChecked(True)
        self.smButton = QtWidgets.QCheckBox(self.widget_2)
        self.smButton.setObjectName("smButton")

        self.widget_o = HLayout(self.widget_2, 'widget_o', 41)
#
        self.matNumberLineEdit = QtWidgets.QLineEdit(self.widget_o.widget)
        self.matNumberLineEdit.setObjectName("matNumberLineEdit")
        self.widget_o.hlayout.addWidget(self.matNumberLineEdit, 1)

        self.label_b = QtWidgets.QLabel(self.widget_o.widget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_b.setFont(font)
        self.label_b.setObjectName("label_b")
        self.widget_o.hlayout.addWidget(self.label_b, 0)

        self.uploadButtonx = QtWidgets.QPushButton(self.widget_o.widget)
        self.uploadButtonx.setObjectName("uploadButtonx")
        self.widget_o.hlayout.addWidget(self.uploadButtonx, 0)

        self.verticalLayout_2.addWidget(self.widget_o.widget)
##
        self.verticalLayout_2.addWidget(self.shButton)
        self.verticalLayout_2.addWidget(self.vButton)
        self.verticalLayout_2.addWidget(self.smButton)
        self.verticalLayout_5.addWidget(self.widget_2)
        self.widget_5 = QtWidgets.QWidget(self.spreadsheet)
        self.widget_5.setMinimumSize(QtCore.QSize(83, 0))
        self.widget_5.setObjectName("widget_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.genSpreadsheetButton = QtWidgets.QPushButton(self.widget_5)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        self.genSpreadsheetButton.setFont(font)
        self.genSpreadsheetButton.setObjectName("genSpreadsheetButton")
        self.verticalLayout_3.addWidget(self.genSpreadsheetButton)
       
        self.verticalLayout_5.addWidget(self.widget_5)
        self.horizontalLayout_2.addWidget(self.spreadsheet)
        self.verticalLayout.addWidget(self.cardsFrame, 0, QtCore.Qt.AlignLeft)


        self.statusBar = HLayout(self.centralWidget, 'statusBar', 0)
        self.statusBar.hlayout.setContentsMargins(4, 1, 4, 1)
        self.statusBar.hlayout.setSpacing(0)
        self.statusBar.widget.setStyleSheet("""
                #statusBar {
                    background: white;
                    border-style: outset;
                    border-width: 0.83px;
                    border-color: grey white white white;
                    padding: 8.33px;
                }
                QPushButton {
                  background-color: white;
                  color: black;
                  border-style: solid;
                  border-width: 0.83px;
                  border-color: white white white grey;
                  border-radius: 0px;
                  padding: 2.5px;
                  min-width: 33.33px;
                }
                QPushButton:hover {
                    background-color: rgb(200, 197, 197);
                }
            """
        )
        self.verticalMain.addWidget(self.mainbody)
        self.verticalMain.addWidget(self.statusBar.widget)

        self.retranslateUi(window)
        # QtCore.QMetaObject.connectSlotsByName(window)
####
        self.dpts = []
        self.configure_profile()
        self.attach_event_handlers()
        self.files = None
        self.progress = ProgressDialog(centralWidget, self.get_size_from_ratio(2.5, 3.5))
        self.worker = None
        self.thread = None

        centralWidget.setFixedSize(centralWidget.sizeHint())
        window.setFixedSize(window.sizeHint())

        self.initialize_profile()

    def retranslateUi(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("window", "DataHub"))
        self.appHeader.setText(_translate("centralWidget", "DataHub"))
        self.label_2.setText(_translate("centralWidget", "File Upload              "))
        self.label_8.setText(_translate("centralWidget", "Select type:"))
        self.comboBox.setItemText(0, _translate("centralWidget", "SELECT"))
        self.comboBox.setItemText(1, _translate("centralWidget", "Master sheet"))
        self.comboBox.setItemText(2, _translate("centralWidget", "Biodata"))
        self.comboBox.setItemText(3, _translate("centralWidget", "Dept & Courses"))
        self.label_5.setText(_translate("centralWidget", "0 files selected"))
        self.uploadButton.setText(_translate("centralWidget", " Upload"))
        self.label.setText(_translate("centralWidget", "Select excel files:"))
        self.selectFileButton.setText(_translate("centralWidget", "select"))
        self.label_3.setText(_translate("centralWidget", "Spreadsheet Generator"))

        self.label_z.setText(_translate("centralWidget", ""))

        self.uploadButtonx.setText(_translate("centralWidget", " Select File "))
        self.label_b.setText(_translate("centralWidget", "or"))
        self.shButton.setText(_translate("centralWidget", "Generate spreadheet"))
        self.vButton.setText(_translate("centralWidget", "Verify results"))
        self.smButton.setText(_translate("centralWidget", "Generate summary"))
        self.delButton.setText(_translate("centralWidget", "Delete"))
        
        self.matNumberLineEdit.setPlaceholderText(_translate("centralWidget", "Input MAT No.s (e.g U2015/3025001,...)"))
        self.genSpreadsheetButton.setText(_translate("centralWidget", "Generate"))

        self.newprofile.setText(_translate("centralWidget", " New profile"))

        self.menuPreferences.setTitle(_translate("window", "Profiles"))
        self.setPreferencesAction.setText(_translate("window", "New"))
        self.setPreferencesAction2.setText(_translate("window", "Import"))

        self.menuHelp.setTitle(_translate("window", "Help"))
        self.actionHelp.setText(_translate("window", "Help"))
        self.actionAbout.setText(_translate("window", "About"))

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

    def attach_event_handlers(self):
        self.selectFileButton.clicked.connect(self.select_handler)
        self.uploadButton.clicked.connect(self.upload_handler)
        self.genSpreadsheetButton.clicked.connect(self.spreadsheet_handler)
        self.uploadButtonx.clicked.connect(self.uploadlist_handler)
        self.password.clicked.connect(self.profile_handler.update_profile_settings)
        self.profileSel.currentIndexChanged.connect(self.profile_handler.change_profile)
        self.newprofile.clicked.connect(self.profile_handler.create_new_profile)
        self.setPreferencesAction.triggered.connect(self.profile_handler.create_new_profile)
        self.setPreferencesAction2.triggered.connect(self.profile_handler.import_profile)

    def configure_profile(self):
        self.profile_handler = ProfileHandler(self)

    def initialize_profile(self):
        self.profile_handler.initialize()

    def create_thread(self, worker, exec):
        self.thread = QThread()
        worker.moveToThread(self.thread)
        self.thread.started.connect(exec)
        worker.finished.connect(self.thread.quit)
        worker.finished.connect(worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        worker.show_message.connect(self.profile_handler.ui_config.show_message)
        worker.reset_files.connect(self.reset_files)
        worker.set_mat_no_list.connect(self.set_mat_no_list)
        worker.show_progress.connect(self.progress.show)
        worker.update_progress.connect(self.progress.update)
        worker.cancel_progress.connect(self.progress.close)
        worker.load_departments.connect(self.profile_handler.ui_config.load_departments)
        return self.thread

    def spreadsheet_handler(self):
        crypto = CryptoManager(self.profile_handler.profile.pdb.Session)
        self.worker = Worker(self, crypto)
        self.thread = self.create_thread(worker = self.worker, exec = self.worker.spreadsheet_handler)
        self.thread.start()

    def upload_handler(self):
        index = self.comboBox.currentIndex()
        if index == 0:
            self.profile_handler.ui_config.show_message('Please select an upload type', False)
        else:
            if self.files == None or len(self.files) == 0:
                self.profile_handler.ui_config.show_message('No file selected, please select a file', False)
                return
            
            def on_status(status):
                if status == 'correct' or status == 'default':
                    self.worker = Worker(self, crypto)
                    self.profile_handler.decrypt_write_config(crypto)
                    self.thread = self.create_thread(worker = self.worker, exec = self.worker.upload_handler)
                    self.thread.start()

            crypto = CryptoManager(self.profile_handler.profile.pdb.Session)
            self.profile_handler.ui_config.validate_password(crypto, 'no-reset', False, on_status)
            
    def uploadlist_handler(self):
        self.mat_files = self.get_text_file()
        self.worker = Worker(self)
        self.thread = self.create_thread(worker = self.worker, exec = self.worker.uploadlist_handler)
        self.thread.start()

    def set_mat_no_list(self, mat_nos):
        _translate = QtCore.QCoreApplication.translate
        self.matNumberLineEdit.setText(_translate("centralWidget", mat_nos))

    def select_handler(self):
        files = self.get_text_file()
        if len(files) > 0:
            self.files = files
            _translate = QtCore.QCoreApplication.translate
            self.label_5.setText(_translate("centralWidget", str(len(files)) + " file(s) selected"))
    
    def get_text_file(self):
        root = tk.Tk()
        root.withdraw()
        return( filedialog.askopenfilenames(filetypes= [('Excel files', '.xlsx .xls .xlsm')]) )

    def reset_files(self):
        self.files = None
        self.delButton.setChecked(False)
        _translate = QtCore.QCoreApplication.translate
        self.label_5.setText(_translate("centralWidget", "0 file(s) selected"))


    def get_size_from_ratio(self, w = 1, h = 1):
        size = self.centralWidget.sizeHint()
        return QSize(math.floor(size.width() / w), math.floor(size.height() / h))

    def show_progress(self, stop):
        self.progress.show(stop)

    def update_progress(self):
        self.progress.update()

class ProgressDialog(object):
    def __init__(self, parent, size):
        super().__init__()
        self.parent = parent
        self.size = size

    def show(self, stop, value = 0):
        try:
            self.progress = QtWidgets.QProgressDialog('Operation processing, please wait...', None, 0, stop, self.parent)
            self.progress.setWindowTitle("Processing")
            self.progress.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress.canceled.connect(self.onCancelled)
            self.progress.setMinimumSize(self.size)
            self.stop = stop
            self.value = value
            self.progress.show()
            self.update()
        except Exception as e:
            errBox = QMessageBox()
            errBox.setWindowTitle('Error')
            errBox.setText('An error occured {}'.format(e))
            errBox.addButton(QMessageBox.Ok)
            errBox.exec()
            return
            
    def onCancelled(self):
        if self.value < self.stop:
            self.show(self.stop, self.value - 1)
        else:
            self.value = 0
            self.stop = 0

    def update(self, value = 1):
        self.value += value
        if not self.progress.wasCanceled():
            self.progress.setValue(self.value)
        if self.value >= self.stop:
            self.close()

    def close(self):
        self.value = 0
        self.stop = 0
        if not self.progress.wasCanceled():
            self.progress.cancel()

class Worker(QObject):
    def __init__(self, app, cryptoMan = None) -> None:
        super().__init__()
        self.app = app
        self.Session = app.profile_handler.getSession()
        self.cryptoMan = cryptoMan
        self.timer = Time()

    finished = pyqtSignal()
    show_message = pyqtSignal(str, bool)
    set_mat_no_list = pyqtSignal(str)
    reset_files = pyqtSignal()
    show_progress = pyqtSignal(int)
    update_progress = pyqtSignal(int)
    cancel_progress = pyqtSignal()
    load_departments = pyqtSignal()
    
    def get_time_suffix(self):
        return str((math.floor(self.timer.get_time_in_micro() / 1000000)) % 10000000)

    def spreadsheet_handler(self):
        mats = self.app.matNumberLineEdit.text().upper().rstrip(',')
        mat_list = set(re.split('\s*,\s*', mats))
        suffix = self.get_time_suffix()

        gensh = self.app.shButton.isChecked()
        gensm = self.app.smButton.isChecked()
        verify = self.app.vButton.isChecked()

        operations = [gensh, gensm]
        
        if not gensh and not gensm:
            self.show_message.emit('Please select at least one \'Generate\' operation', False)
            self.finished.emit()
            return 
        
        self.session = self.Session()
        store = Storage()
        output_path = store.get_outpur_dir()
        folder = output_path
        if (len(mat_list) > 1 and gensh) or operations.count(True) > 1:
            folder = output_path + 'Output_Batch_{}/'.format(suffix)
            folder = store.sep(folder)
            store.create_folder(folder)

        group = {
            'no_result': {'v': [], 'i': 'No result', 's': 'No results found'}, 'no_dept': {'v': [], 'i': 'Unkown department', 's': 'Student\'s department unknown. Please select a department'},
            'invalid': {'v': [], 'i': 'Invalid Mat no', 's': 'Please input a valid Matric number'}, 'success': {'v': []},
            'error': {'v': [], 'i': 'Error'},'no_courses': {'v': [], 'i': 'No course list'}
        }
        responses = []
        spread_sheet = None
        output = None
        self.show_progress.emit(len(mat_list) + operations.count(True) + 1)
        _department = None
        dpt = self.app.comboBoxz.currentIndex()
        if dpt != 0:
            _department = self.app.dpts[dpt - 1]
        for mat_no in mat_list:
            if re.fullmatch('^[u,U]\d{4}/\d{7}$', mat_no) != None:
                _record = self.session.query(Result).filter(Result.mat_no == mat_no).all()

                record = []
                if len(_record) > 0:
                    for r in _record:
                        _r = {'session': r.session,'courseCode': r.courseCode, 'score': r.score, 'mat_no': r.mat_no, 'verified': True}
                        if self.cryptoMan != None and verify:
                            _r['verified'] = self.cryptoMan.verify_signature(r, r._signature_)
                        record.append(_r)

                    record.sort(key = lambda i: (i['session']))

                    user['mat_no'] = mat_no
                    student = {}
                    student.update(user)
                    _user = self.session.query(Student).filter(Student.mat_no == mat_no).first()
                    if _user != None:
                        student = {
                            'first_name': _user.first_name, 'last_name': _user.last_name,
                            'other_names': _user.other_names, 'state': _user.state,
                            'mat_no': _user.mat_no, 'sex': _user.sex,
                            'marital_status': _user.marital_status, 'department': _user.department
                        }
                        if str(_user.annotation).startswith('{'):
                            ant = JSONDecoder().decode(str(_user.annotation))
                            if ant.get('missed_sessions') != None:
                                student['missed_sessions'] = ant.get('missed_sessions')
                    department = None
                    if student['department'] == None or student['department'] == '':
                        if _department == None:
                            group['no_dept']['v'].append(mat_no)
                            self.update_progress.emit(1)
                            continue
                        department = _department
                    else:
                        for dpt in self.app.dpts:
                            if student['department'].lower() == dpt.code.lower():
                                department = dpt
                                break
                        if department == None:
                            group['no_courses']['v'].append('{}: {}'.format(mat_no, student['department']))
                            group['no_courses']['s'] = 'Department, {} is unavailable'.format(student['department'])
                            self.update_progress.emit(1)
                            continue

                    student['department'] = department.code
                    if _department == None or department.levels > _department.levels:
                        _department = department
                    _courses = self.session.query(Course).filter(Course.department == department.code).all()
                    courses = {}
                    
                    if len(_courses) > 0:
                        for course in _courses:
                            courses[str(course.id)] = { 'properties': course.properties,  'level': course.level * 100, 'sem': course.sem, 'title': course.title, 'code': course.code, 'cu': course.cu }
                    else:
                        group['no_courses']['v'].append('{}: {}'.format(mat_no, student['department']))
                        group['no_courses']['s'] = 'No course list available for department, {}'.format(student['department'])
                        self.update_progress.emit(1)
                        continue
                    spread_sheet = SpreadSheet()
                    output = folder + mat_no.replace('/', '-') + '_spreadsheet_'+ suffix + '.xlsx'
                    filename = output
                    if not gensh:
                        filename = None
                    response = spread_sheet.generate(
                        student, record, courses, department,
                        filename = filename,
                    )

                    print(response)
                    if response['status'] == 'error':
                        group['error']['v'].append(mat_no)
                        group['error']['s'] = response['message']
                    else:
                        responses.append(response)
                        total_r = len(spread_sheet.scored_results)
                        unkown_r = len(spread_sheet.invalid_results)
                        group['success']['v'].append('{}: {}/{}'.format(mat_no, total_r - unkown_r, total_r))
                else:
                    group['no_result']['v'].append(mat_no)
            else:
                group['invalid']['v'].append(mat_no)
            self.update_progress.emit(1)

        # TODO do magic here
        if gensm and len(group['success']['v']) > 0:
            output = folder + 'summary_'+ suffix + '.xlsm'
            summary = SummarySheet()
            summary.generate(
                responses,
                _department,
                filename = output
            )
            self.update_progress.emit(1)
        
        if len(mat_list) == 1:
            if len(group['success']['v']) > 0:
                path = output
                if operations.count(True) > 1:
                    path = folder
                total_r = len(spread_sheet.scored_results)
                unkown_r = len(spread_sheet.invalid_results)
                self.show_message.emit('Operation complete!\n\nResult count: {}/{}\n\nSaved at:\n{}'.format(total_r - unkown_r, total_r, path), False)
            else:
                for key in group.keys():
                    if key != 'success':
                        if len(group[key]['v']) > 0:
                            self.show_message.emit(group[key]['s'], False)
                            break
        elif len(mat_list) > 1:
            for key in group.keys():
                if key != 'invalid':
                    group[key]['v'].sort(key = lambda e: (int(re.split('^[u,U](\d{4})/\d{4}(\d{3}).*$',e)[1]), int(re.split('^[u,U](\d{4})/\d{4}(\d{3}).*$',e)[2])))
            msg = 'Operation complete!\n\nSuccess: {}\n'.format(len(group['success']['v']))
            if len(group['success']['v']) > 0:
                msg += '{}'.format(group['success']['v'])
            msg += '\n\n'
            if len(group['success']['v']) > 0:
                path = output
                if operations.count(True) > 1 or gensh:
                    path = folder
                msg += 'Saved at:\n{}\n\n'.format(path)
            for key in group.keys():
                if key != 'success':
                    if len(group[key]['v']) > 0:
                        msg += '{}: {}\n{}\n\n'.format(group[key]['i'], len(group[key]['v']), group[key]['v'])
            self.show_message.emit(msg, True)
        else:
            self.show_message.emit('Please input a valid Matric number', False)
        
        self.cancel_progress.emit()
        self.session.close()
        self.finished.emit()


    def table_upload(self, key, mapper, object, delete, get):
        if self.app.files != None and len(self.app.files) > 0:
            success = 0
            failure = 0
            update = 0
            deleted = 0
            batch = mapper('').batchId

            isDelete = self.app.delButton.isChecked()
            self.show_progress.emit(1+ len(self.app.files) * 1000000)

            is_remote_write = self.app.profile_handler.settings.is_remote_write()
            stager = Stager(self.session, is_remote_write)
            for file in self.app.files:
                master = mapper(file)
                master.batchId = batch
                results = master.get_data()
                inc = math.floor(1000000 / max(len(results), 1))
                
                for data in results:
                    _isdelete = (data.get('delete') != None and str(data.get('delete')).lower() == 'true') or isDelete
                    record = object(data, _isdelete)
                    record._timestamp_ = self.timer.get_next_time_in_micro()
                    if self.cryptoMan != None:
                        record._signature_ = self.cryptoMan.sign(record)
                    if _isdelete:
                        delt = delete(data, self.session, stager)
                        if delt > 0:
                            deleted += delt
                            data['status'] = "deleted"
                            stager.stage_record(record, key(data), self.cryptoMan)
                        else:
                            data['status'] = "not_found"
                    else:
                        try:
                            rc = get(data, self.session, stager)
                            self.session.merge(record)
                            stager.stage_record(record, key(data), self.cryptoMan)
                            if rc == None:
                                data['status'] = "created"
                                success += 1
                            else:
                                data['status'] = "updated"
                                update += 1
                        except Exception as e:
                            data['status'] = "error"
                            data['error'] = e
                            failure += 1
                    print(data)
                    self.update_progress.emit(inc)
            self.session.commit()
            
            self.cancel_progress.emit()
            self.reset_files.emit()
            self.show_message.emit('Operation completed\n\nAdded: {}\nUpdated: {}\nDeleted: {}\nFailed: {}\n\nBatch ID: {}'.format(success, update, deleted, failure, batch), False)
        else:
            self.show_message.emit('No file selected, please select a file', False)

    def mastersheet_upload(self):
        self.table_upload(
            key = lambda data: 'resultId',
            mapper = lambda file: MasterSheet(file),
            object = lambda data, delete: Result(
                resultId = data['resultId'],
                batchId = data['batchId'],
                session = data['session'],
                courseId = data['courseId'],
                courseCode = data['courseCode'],
                mat_no = data['mat_no'] if not delete else data['mat_no'] + '_',
                annotation = data['annotation'],
                score = data['score'],
                status = "UP" if not delete else "DELETE",
            ),
            delete = lambda data, session, stager: session.query(Result)
                .filter(Result.resultId == data['resultId']).delete(),
            get = lambda data, session, stager: session.query(Result).filter(Result.resultId == data['resultId']).first()
        )

    def department_upload(self):
        self.table_upload(
            key = lambda data: 'courseId' if data['type'] == 'course' else 'id',
            mapper = lambda file: CourseList(file),
            object = self.department_object,
            delete = self.del_dept,
            get = self.get_dept
        )
        self.load_departments.emit()
            
    def get_dept(self, data, session, stager: Stager):
        if data['type'] == 'course':
            return session.query(Course).filter(Course.id == data['courseId']).first()
        else:
            if stager.is_writer:
                crs = session.query(Course).filter(Course.department == data['id']).all()
                for c in crs:
                    obj, strg = stager.serialize_object(c)
                    obj['type'] = 'course'
                    obj = self.department_object(obj, True)
                    obj._timestamp_ = self.timer.get_next_time_in_micro()
                    if self.cryptoMan != None:
                        obj._signature_ = self.cryptoMan.sign(obj)
                    stager.stage_record(obj, 'courseId', self.cryptoMan)

            session.query(Course).filter(Course.department == data['id']).delete()
            return session.query(Department).filter(Department.id == data['id']).first()

    def del_dept(self, data, session, stager):
        if data['type'] == 'course':
            return session.query(Course).filter(Course.courseId == data['courseId']).delete()
        else:
            if stager.is_writer:
                crs = session.query(Course).filter(Course.department == data['id']).all()
                for c in crs:
                    obj, strg = stager.serialize_object(c)
                    obj['type'] = 'course'
                    obj = self.department_object(obj, True)
                    obj._timestamp_ = self.timer.get_next_time_in_micro()
                    if self.cryptoMan != None:
                        obj._signature_ = self.cryptoMan.sign(obj)
                    stager.stage_record(obj, 'courseId', self.cryptoMan)
            c = session.query(Course).filter(Course.department == data['id']).delete()
            return int(session.query(Department).filter(Department.id == data['id']).delete()) + int(c)

    def department_object(self, data, delete):
        if data['type'] == 'course':
            return Course(
                courseId = data['courseId'],
                id = data['id'],
                code = data['code'],
                title = data['title'],
                cu = data['cu'],
                properties = data['properties'],
                level = data['level'],
                sem = data['sem'],
                department = data['department'] if not delete else data['department'] + "_",
                status = "UP" if not delete else "DELETE",
            )
        else:
            return Department(
                id = data['id'],
                faculty = data['faculty'],
                department = data['department'],
                department_long = data['department_long'],
                code = data['code'],
                hod = data['hod'],
                semesters = data['semesters'],
                levels = data['levels'],
                summary = data['summary'],
                spreadsheet = data['spreadsheet'],
                max_cu = data['max_cu'],
                status = "UP" if not delete else "DELETE",
            )

    def biodata_upload(self):
        self.table_upload(
            key = lambda data: 'mat_no',
            mapper = lambda file: StudentList(file),
            object = lambda data, delete: Student(
                batchId = data['batchId'],
                mat_no = data['mat_no'],
                state = data['state'],
                sex = data['sex'],
                marital_status = data['marital_status'],
                department = data['department'],
                annotation = data['annotation'],
                last_name = data['last_name'],
                first_name = data['first_name'],
                other_names = data['other_names'],
                status = "UP" if not delete else "DELETE",
            ),
            delete = lambda data, session, stager: session.query(Student)
                .filter(Student.mat_no == data['mat_no']).delete(),
            get = lambda data, session, stager: session.query(Student).filter(Student.mat_no == data['mat_no']).first()
        )
        
    def upload_handler(self):
        self.session = self.Session()
        index = self.app.comboBox.currentIndex()
        if index == 0:
            self.show_message.emit('Please select an upload type', False)
        elif index == 1:
            self.mastersheet_upload()
        elif index == 2:
            self.biodata_upload()
        elif index == 3:
            self.department_upload()
        self.session.close()
        self.finished.emit()

    def uploadlist_handler(self):
        if len(self.app.mat_files) > 0:
            mat_nos = ''
            count = 0
            for file in self.app.mat_files:
                ls = ListUpload(file)
                data = ls.get_data()

                for mat in data:
                    if re.search(mat['mat_no'], mat_nos) == None:
                        mat_nos += mat['mat_no'] + ','
                        count += 1
            mat_nos = mat_nos.rstrip(',')

            self.show_message.emit('{} Matric numbers found'.format(count), False)
            self.set_mat_no_list.emit(mat_nos)
        self.finished.emit()

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_centralWidget()
        self.ui.setupUi(self)

    @QtCore.pyqtSlot(bool)
    def on_setPreferencesAction_triggered(self, triggered):
        pass

    @QtCore.pyqtSlot(bool)
    def on_setPreferencesAction2_triggered(self, triggered):
        pass

        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    icon = QtGui.QIcon()
    pix = QtGui.QPixmap("static/icon/monitor.svg")
    pix.setDevicePixelRatio(2.5)
    icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)

    app.setWindowIcon(icon)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
