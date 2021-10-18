# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form1.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import faulthandler
import re
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDir, QSize, Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal


import os

from transformers.master_sheet import MasterSheet
from transformers.spread_sheet import SpreadSheet
from transformers.student_list import StudentList
from transformers.list_upload import ListUpload
from transformers.summary_sheet import SummarySheet

from transformers.sample_data.result import user
from transformers.sample_data.courses import MEG, MCT

from models.result import Result
from models.student import Student
from database.base import Session, engine, Base
from utils import app_path
import time, math

import tkinter as tk
from tkinter import filedialog

Base.metadata.create_all(engine)
faulthandler.enable()

class HLayout(object):
    def __init__(self, parent, name, margin_top) -> None:
        super().__init__()
        self.widget = QtWidgets.QWidget(parent)
        self.widget.setObjectName(name)
        self.hlayout = QtWidgets.QHBoxLayout(self.widget)
        self.hlayout.setObjectName("horizontalLayout_{}".format(name))
        self.hlayout.setContentsMargins(0, margin_top, 0, 0)

class Ui_centralWidget(object):
    def setupUi(self, centralWidget):
        self.centralWidget = centralWidget
        centralWidget.setObjectName("centralWidget")
        # centralWidget.resize(2000, 1000)
        centralWidget.setStyleSheet("* {\n"
"  color: #000000;\n"
"  border: none;\n"
"}\n"
"#centralWidget {\n"
"  background: #4297A0;\n"
"}\n"
"\n"
"QLineEdit {\n"
"  background: transparent;\n"
" background: #EED6D3;\n"
"   border-style: outset;\n"
"  border-width: 2px;\n"
"  border-radius: 5px;\n"
"  border-color: black;\n"
"}\n"
"\n"
"#appHeader {\n"
"  color: #F4EAE6;\n"
"}\n"
"\n"
"QPushButton {\n"
"  background-color: #67595E;\n"
"  color: white;\n"
"  border-style: outset;\n"
"  border-width: 2px;\n"
"  border-radius: 15px;\n"
"  border-color: black;\n"
"  padding: 6px;\n"
"  min-width: 80px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #867c80;\n"
"}\n"
"#matNumberLineEdit {\n"
"  background: #F4EAE6;\n"
"  border-width: 2px;\n"
"border-color: black;\n"
"padding-left: 20px;\n"
"padding-right: 10px;\n"
"}\n"
"#mastersheet{\n"
"border-style: outset;\n"
"  border-width: 2px;\n"
"  border-radius: 15px;\n"
"  border-color: black;\n"
"}\n"
"#spreadsheet{\n"
"border-style: outset;\n"
"  border-width: 2px;\n"
"  border-radius: 15px;\n"
"  border-color: black;\n"
"}")
        self.horizontalLayout = QtWidgets.QHBoxLayout(centralWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainbody = QtWidgets.QWidget(centralWidget)
        self.mainbody.setObjectName("mainbody")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainbody)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerFrame = QtWidgets.QWidget(self.mainbody)
        self.headerFrame.setObjectName("headerFrame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.headerFrame)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.headerFrame)
        self.label_4.setMaximumSize(QtCore.QSize(65, 16777215))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("static/icon/monitor.svg"))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.appHeader = QtWidgets.QLabel(self.headerFrame)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.appHeader.setFont(font)
        self.appHeader.setObjectName("appHeader")
        self.horizontalLayout_4.addWidget(self.appHeader)
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
        self.mastersheet.setMinimumSize(QtCore.QSize(325, 0))
        self.mastersheet.setObjectName("mastersheet")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.mastersheet)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.headerWidget = QtWidgets.QWidget(self.mastersheet)
        self.headerWidget.setObjectName("headerWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.headerWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_6 = QtWidgets.QLabel(self.headerWidget)
        self.label_6.setMaximumSize(QtCore.QSize(65, 16777215))
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap("static/icon/codepen.svg"))
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
        self.widget_3.setMinimumSize(QtCore.QSize(250, 100))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_8 = QtWidgets.QLabel(self.widget_3)
        # self.label_8.setMaximumSize(QtCore.QSize(150, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_6.addWidget(self.label_8)
        self.comboBox = QtWidgets.QComboBox(self.widget_3)
        self.comboBox.setMinimumSize(QtCore.QSize(120, 0))
        # self.comboBox.setMaximumSize(QtCore.QSize(121, 16777215))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_6.addWidget(self.comboBox)
        self.verticalLayout_4.addWidget(self.widget_3)
        self.widget = QtWidgets.QWidget(self.mastersheet)
        self.widget.setObjectName("widget")
        self.formLayout = QtWidgets.QFormLayout(self.widget)
        self.formLayout.setObjectName("formLayout")
        # self.formLayout.setLabelAlignment(QtCore.Qt.AlignTop)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignBottom)
        self.formLayout.setAlignment(QtCore.Qt.AlignBottom)
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setMinimumSize(QtCore.QSize(200, 0))
        # self.label_5.setMaximumSize(QtCore.QSize(150, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        # font.setItalic(True)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.uploadButton = QtWidgets.QPushButton(self.widget)
        # self.uploadButton.setMinimumSize(QtCore.QSize(36, 50))
        # self.uploadButton.setMaximumSize(QtCore.QSize(166, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("static/icon/upload.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.uploadButton.setIcon(icon)
        self.uploadButton.setObjectName("uploadButton")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.uploadButton)


        self.label = QtWidgets.QLabel(self.widget)
        # self.label.setMaximumSize(QtCore.QSize(280, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label)
        self.selectFileButton = QtWidgets.QPushButton(self.widget)
        self.selectFileButton.setObjectName("selectFileButton")
        
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.selectFileButton)
        self.verticalLayout_4.addWidget(self.widget)
        self.horizontalLayout_2.addWidget(self.mastersheet, 0, QtCore.Qt.AlignLeft)
        self.spreadsheet = QtWidgets.QWidget(self.cardsFrame)
        self.spreadsheet.setMinimumSize(QtCore.QSize(331, 0))
        self.spreadsheet.setObjectName("spreadsheet")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.spreadsheet)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.headerWidget_2 = QtWidgets.QWidget(self.spreadsheet)
        self.headerWidget_2.setObjectName("headerWidget_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.headerWidget_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_7 = QtWidgets.QLabel(self.headerWidget_2)
        self.label_7.setText("")
        self.label_7.setPixmap(QtGui.QPixmap("static/icon/file-text.svg"))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_5.addWidget(self.label_7, 0, QtCore.Qt.AlignCenter)
        self.label_3 = QtWidgets.QLabel(self.headerWidget_2)
        self.label_3.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_5.addWidget(self.headerWidget_2)
        self.widget_2 = QtWidgets.QWidget(self.spreadsheet)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mechRadioButton = QtWidgets.QRadioButton(self.widget_2)
        self.mechRadioButton.setMinimumSize(QtCore.QSize(200, 0))
        font = QtGui.QFont()
        font.setBold(True)
        self.mechRadioButton.setFont(font)
        self.mechRadioButton.setObjectName("mechRadioButton")
        self.verticalLayout_2.addWidget(self.mechRadioButton)
        self.mctRadioButton = QtWidgets.QRadioButton(self.widget_2)
        self.mctRadioButton.setMinimumSize(QtCore.QSize(200, 0))
        self.mctRadioButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        self.mctRadioButton.setFont(font)
        self.mctRadioButton.setObjectName("mctRadioButton")
        self.verticalLayout_2.addWidget(self.mctRadioButton)
#       

        self.shButton = QtWidgets.QCheckBox(self.widget_2)
        self.shButton.setObjectName("shButton")
        self.shButton.setChecked(True)
        self.smButton = QtWidgets.QCheckBox(self.widget_2)
        self.smButton.setObjectName("smButton")

        self.widget_o = HLayout(self.widget_2, 'widget_o', 0)        
#

        self.matNumberLineEdit = QtWidgets.QLineEdit(self.widget_o.widget)
        self.matNumberLineEdit.setObjectName("matNumberLineEdit")
        self.widget_o.hlayout.addWidget(self.matNumberLineEdit, 1)

        self.label_b = QtWidgets.QLabel(self.widget_o.widget)
        # self.label_b.setMinimumSize(QtCore.QSize(200, 0))
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
        self.verticalLayout_2.addWidget(self.smButton)
        self.verticalLayout_5.addWidget(self.widget_2)
        self.widget_5 = QtWidgets.QWidget(self.spreadsheet)
        self.widget_5.setMinimumSize(QtCore.QSize(200, 0))
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
        self.horizontalLayout.addWidget(self.mainbody)

        self.retranslateUi(centralWidget)
        QtCore.QMetaObject.connectSlotsByName(centralWidget)
        centralWidget.setTabOrder(self.genSpreadsheetButton, self.mechRadioButton)
        centralWidget.setTabOrder(self.mechRadioButton, self.matNumberLineEdit)
        centralWidget.setTabOrder(self.matNumberLineEdit, self.mctRadioButton)

        centralWidget.setFixedSize(centralWidget.sizeHint())

        self.attach_event_handlers()
        self.files = None
        self.progress = ProgressDialog(centralWidget, self.get_size_from_ratio(2.5, 3.5))
        self.worker = None
        self.thread = None


    def retranslateUi(self, centralWidget):
        _translate = QtCore.QCoreApplication.translate
        centralWidget.setWindowTitle(_translate("centralWidget", "DataHub"))
        self.appHeader.setText(_translate("centralWidget", "DataHub"))
        self.label_2.setText(_translate("centralWidget", "File Upload              "))
        self.label_8.setText(_translate("centralWidget", "Select type:"))
        self.comboBox.setItemText(0, _translate("centralWidget", "SELECT"))
        self.comboBox.setItemText(1, _translate("centralWidget", "Master sheet"))
        self.comboBox.setItemText(2, _translate("centralWidget", "Biodata"))
        self.label_5.setText(_translate("centralWidget", "0 files selected"))
        self.uploadButton.setText(_translate("centralWidget", " Upload"))
        self.label.setText(_translate("centralWidget", "Select excel files:"))
        self.selectFileButton.setText(_translate("centralWidget", "select"))
        self.label_3.setText(_translate("centralWidget", "Spreadsheet Generator"))
        self.mechRadioButton.setText(_translate("centralWidget", "Mechanical Engineering"))
        self.mctRadioButton.setText(_translate("centralWidget", "Mechatronics Engineering"))
        
        self.uploadButtonx.setText(_translate("centralWidget", " Select File "))
        self.label_b.setText(_translate("centralWidget", "or"))
        self.shButton.setText(_translate("centralWidget", "Generate spreadheet"))
        self.smButton.setText(_translate("centralWidget", "Generate summary"))
        
        self.matNumberLineEdit.setPlaceholderText(_translate("centralWidget", "Input MAT No.s (e.g U2015/3025001,...)"))
        self.genSpreadsheetButton.setText(_translate("centralWidget", "Generate"))

    def attach_event_handlers(self):
        self.selectFileButton.clicked.connect(self.select_handler)
        self.uploadButton.clicked.connect(self.upload_handler)
        self.genSpreadsheetButton.clicked.connect(self.spreadsheet_handler)
        self.uploadButtonx.clicked.connect(self.uploadlist_handler)

    def create_thread(self, worker, exec):
        self.thread = QThread()
        worker.moveToThread(self.thread)
        self.thread.started.connect(exec)
        worker.finished.connect(self.thread.quit)
        worker.finished.connect(worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        worker.show_message.connect(self.show_message)
        worker.reset_files.connect(self.reset_files)
        worker.set_mat_no_list.connect(self.set_mat_no_list)
        worker.show_progress.connect(self.progress.show)
        worker.update_progress.connect(self.progress.update)
        worker.cancel_progress.connect(self.progress.close)
        return self.thread

    def spreadsheet_handler(self):
        self.worker = Worker(self)
        self.thread = self.create_thread(worker = self.worker, exec = self.worker.spreadsheet_handler)
        self.thread.start()

    def upload_handler(self):
        self.worker = Worker(self)
        self.thread = self.create_thread(worker = self.worker, exec = self.worker.upload_handler)
        self.thread.start()

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
    
    def show_message(self, mes, long = True):
        if long:
            result = ScrollMessageBox(mes, self.get_size_from_ratio(2, 2))
            result.setWindowTitle("Info")
            result.exec_()
        else:
            QMessageBox.information(self.centralWidget, 'Info', mes)

    def get_text_file(self):
        root = tk.Tk()
        root.withdraw()
        return( filedialog.askopenfilenames() )

    def reset_files(self):
        self.files = None
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

class Worker(QObject):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.session = Session()

    finished = pyqtSignal()
    show_message = pyqtSignal(str, bool)
    set_mat_no_list = pyqtSignal(str)
    reset_files = pyqtSignal()
    show_progress = pyqtSignal(int)
    update_progress = pyqtSignal(int)
    cancel_progress = pyqtSignal()

    def create_folder(self, folder):
        try:
            os.mkdir(folder)
            print('{} directory created'.format(folder))
        except:
            print('{} directory already exists, skipping'. format(folder))
    
    def get_time_suffix(self):
        return str(math.floor(time.time()) % 10000000)

    def spreadsheet_handler(self):
        mats = self.app.matNumberLineEdit.text().upper().rstrip(',')
        mat_list = set(re.split('\s*,\s*', mats))
        suffix = self.get_time_suffix()

        gensh = self.app.shButton.isChecked()
        gensm = self.app.smButton.isChecked()

        operations = [gensh, gensm]
        
        if not gensh and not gensm:
            self.show_message.emit('Please select at least one \'Generate\' operation', False)
            self.finished.emit()
            return 
        
        folder = 'output/'
        self.create_folder(folder)
        if (len(mat_list) > 1 and gensh) or operations.count(True) > 1:
            folder = 'output/Output_Batch_{}/'.format(suffix)
            self.create_folder(folder)

        group = {
            'no_result': {'v': [], 'i': 'No result', 's': 'No results found'}, 'no_dept': {'v': [], 'i': 'Unkown department', 's': 'Student\'s department unknown. Please select a department'},
            'invalid': {'v': [], 'i': 'Invalid Mat no', 's': 'Please input a valid Matric number'}, 'success': {'v': []},
            'error': {'v': [], 'i': 'Error'},'no_courses': {'v': [], 'i': 'No course list'}
        }
        responses = []
        spread_sheet = None
        output = None
        self.show_progress.emit(len(mat_list) + operations.count(True) + 1)

        for mat_no in mat_list:
            if re.fullmatch('^[u,U]\d{4}/\d{7}$', mat_no) != None:
                _record = self.session.query(Result).filter(Result.mat_no == mat_no).all()

                record = []
                # import transformers.sample_data.result as rs 
                # record = rs.result
                if len(_record) > 0:
                    for r in _record:
                        record.append({'session': r.session,'courseCode': r.courseCode, 'score': r.score})

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

                    if student['department'] == None or student['department'] == '':
                        if self.app.mechRadioButton.isChecked():
                            courses = MEG
                            student['department'] == 'MEG'
                        elif self.app.mctRadioButton.isChecked():
                            courses = MCT
                            student['department'] == 'MCT'
                        else:
                            group['no_dept']['v'].append(mat_no)
                            self.update_progress.emit(1)
                            continue
                    elif re.search('(^meg$)|mechanical', student['department'].lower())  != None:
                        courses = MEG
                    elif re.search('(^mct$)|mechatronic', student['department'].lower())  != None:
                        courses = MCT
                    else:
                        group['no_courses']['v'].append('{}: {}'.format(mat_no, student['department']))
                        group['no_courses']['s'] = 'Course list unavailable for {}'.format(student['department'])
                        self.update_progress.emit(1)
                        continue

                    template = app_path('static/excel/templates/spreadsheet_template.xlsx')
                    if not gensh:
                        template = None
                    spread_sheet = SpreadSheet()
                    output = folder + mat_no.replace('/', '-') + '_spreadsheet_'+ suffix + '.xlsx'
                    response = spread_sheet.generate(
                        student, record, courses, 
                        filename = app_path(output),
                        template = template,
                    )

                    print(response)
                    if response['status'] == 'error':
                        group['error']['v'].append(mat_no)
                        group['error']['s'] = response['message']
                    else:
                        responses.append(response)
                        group['success']['v'].append('{}: {}'.format(mat_no, len(spread_sheet.scored_results)))
                else:
                    group['no_result']['v'].append(mat_no)
            else:
                group['invalid']['v'].append(mat_no)
            self.update_progress.emit(1)

        # TODO do magic here
        if gensm and len(group['success']['v']) > 0:
            output = folder + 'summary_'+ suffix + '.xlsx'
            summary = SummarySheet()
            summary.generate(
                responses, 
                template = app_path('static/excel/templates/summarysheet_template.xlsx'),
                filename = app_path(output)
            )
            self.update_progress.emit(1)
        
        if len(mat_list) == 1:
            if len(group['success']['v']) > 0:
                path = output
                if operations.count(True) > 1:
                    path = folder
                self.show_message.emit('Operation complete!\n\nResult count: {}\n\nSaved at:\n{}'.format(len(spread_sheet.scored_results), app_path(path)), False)
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
                msg += 'Saved at:\n{}\n\n'.format(app_path(path))
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


    def table_upload(self, mapper, object, delete):
        if self.app.files != None and len(self.app.files) > 0:
            success = 0
            failure = 0
            update = 0
            deleted = 0
            batch = mapper('').batchId

            self.show_progress.emit(1+ len(self.app.files) * 1000000)

            for file in self.app.files:
                master = mapper(file)
                master.batchId = batch
                results = master.get_data()
                # import transformers.sample_data.result as sr
                # results = sr.result
                inc = math.floor(1000000 / max(len(results), 1))
                
                for data in results:
                    # data['batchId'] = batch
                    record = object(data)
                    if data.get('delete') != None and str(data.get('delete')).lower() == 'true':
                        delt = delete(data, self.session)
                        if delt > 0:
                            deleted += 1
                            data['status'] = "deleted"
                            self.session.commit()
                        else:
                            data['status'] = "not_found"
                    else:
                        self.session.add(record)
                        try:
                            self.session.commit()
                            data['status'] = "created"
                            success += 1
                        except Exception as e:
                            self.session.rollback()
                            try:
                                delete(data, self.session)
                                self.session.commit()
                                self.session.add(record)
                                self.session.commit()
                                data['status'] = "updated"
                                update += 1
                            except Exception as e:
                                self.session.rollback()
                                data['status'] = "error"
                                data['error'] = e
                                failure += 1
                    print(data)
                    self.update_progress.emit(inc)
            self.cancel_progress.emit()
            self.reset_files.emit()
            self.show_message.emit('Operation completed\n\nAdded: {}\nUpdated: {}\nDeleted: {}\nFailed: {}\n\nBatch ID: {}'.format(success, update, deleted, failure, batch), False)
        else:
            self.show_message.emit('No file selected, please select a file', False)

    def mastersheet_upload(self):
        self.table_upload(
            mapper = lambda file: MasterSheet(file),
            object = lambda data: Result(
                resultId = data['resultId'],
                batchId = data['batchId'],
                session = data['session'],
                courseId = data['courseId'],
                courseCode = data['courseCode'],
                mat_no = data['mat_no'],
                annotation = data['annotation'],
                score = data['score'],
            ),
            delete = lambda data, session: session.query(Result)
                .filter(Result.resultId == data['resultId']).delete()
        )
            
    def biodata_upload(self):
        self.table_upload(
            mapper = lambda file: StudentList(file),
            object = lambda data: Student(
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
            ),
            delete = lambda data, session: session.query(Student)
                .filter(Student.mat_no == data['mat_no']).delete()
        )
        
    def upload_handler(self):
        index = self.app.comboBox.currentIndex()
        if index == 0:
            self.show_message.emit('Please select an upload type', False)
        elif index == 1:
            # thread = threading.Thread(target=self.mastersheet_upload, args=())
            # thread.start()
            self.mastersheet_upload()
        elif index == 2:
            self.biodata_upload()
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
        
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("static/icon/monitor.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

    app.setWindowIcon(icon)
    centralWidget = QtWidgets.QWidget()
    ui = Ui_centralWidget()
    ui.setupUi(centralWidget)
    centralWidget.show()
    sys.exit(app.exec_())