#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 19:47:41 2021

@author: ken

A graphical user interface for the bomcheck.py program.

"""

__version__ = '1.9.1'
__author__ = 'Kenneth E. Carlton'


import ast
import sys
import os
sys.path.insert(0, '/media/sf_shared/projects/bomcheck/src')
import bomcheck
import qtawesome as qta
import webbrowser
import os.path
from bomcheck import export2excel
from PyQt5 import QtPrintSupport
from PyQt5.QtCore import (QAbstractTableModel, Qt)
from PyQt5.QtGui import (QColor, QFont, QKeySequence, QPainter, QTextCursor,
                         QTextDocument, QTextTableFormat)
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QMainWindow, QMessageBox, QPushButton, QStatusBar,
                             QTableView, QTextEdit, QToolBar, QVBoxLayout)

printStrs = []

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(qta.icon("fa5s.check", color="#228B22"))

        try:
            self.configdb = get_configfn()
            with open(self.configdb, 'r') as file:
                x = file.read()
            self.dbdic = ast.literal_eval(x)
        except Exception as e:
            msg = ("Error 101:\n\n"
                   "Unable to open config.txt file which allows the program\n"
                   "to remember user settings.  Default settings will be used.\n"
                   "Otherwise the program will run as normal.\n\n" + str(e))
            msgtitle = 'Warning'
            message(msg, msgtitle, msgtype='Warning', showButtons=False)
            self.dbdic = {'udrop': '3*-025', 'uexceptions': '', 'ask': False,
                          'overwrite': True, 'folder': '', 'file2save2': 'bomcheck'}
            self.configdb = ''

        self.folder = self.dbdic.get('folder')

        file_menu = self.menuBar().addMenu('&File')
        help_menu = self.menuBar().addMenu('&Help')
        self.setWindowTitle('bomcheck')
        self.setMinimumSize(925, 300)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        btn_ac_execute = QAction(qta.icon("fa5s.check", color="#228B22"), 'Execute', self)
        btn_ac_execute.triggered.connect(self.execute)
        btn_ac_execute.setStatusTip('Do a bomcheck of the files listed in the drag-drop zone.')
        toolbar.addAction(btn_ac_execute)

        btn_ac_clear = QAction(qta.icon("mdi.wiper", color="#228B22"), 'Clear', self)
        btn_ac_clear.triggered.connect(self.clear)
        btn_ac_clear.setStatusTip('Clear the drag-drop zone of data.')
        toolbar.addAction(btn_ac_clear)

        btn_ac_folder = QAction(qta.icon("ei.folder-open", color="#228B22"), "Open the folder", self)
        btn_ac_folder.triggered.connect(self.openfolder)
        btn_ac_folder.setStatusTip('Open the the most recently active BOM folder.')
        toolbar.addAction(btn_ac_folder)

        empty_label1 = QLabel()
        empty_label1.setText('   ')
        toolbar.addWidget(empty_label1)

        self.drop_chkbox = QCheckBox('Activate the drop list')
        self.drop_chkbox.setChecked(False)
        self.drop_chkbox.setStatusTip('Ignore pt. nos of SW parts that are in the drop list.  See File>Settings.')
        toolbar.addWidget(self.drop_chkbox)

        empty_label1 = QLabel()
        empty_label1.setText('   ')
        toolbar.addWidget(empty_label1)

        self.across_chkbox = QCheckBox('Output to multiple sheets')
        self.across_chkbox.setChecked(False)
        self.across_chkbox.setStatusTip('Break up results across multiple sheets within the output Excel file.')
        toolbar.addWidget(self.across_chkbox)

        execute_action = QAction(qta.icon("fa5s.check", color="#228B22"), 'Execute', self)
        execute_action.triggered.connect(self.execute)
        file_menu.addAction(execute_action)

        settings_action = QAction(qta.icon("fa.gear", color="#228B22"), 'Settings', self)
        settings_action.triggered.connect(self.settings)
        file_menu.addAction(settings_action)

        quit_action = QAction(qta.icon("mdi.location-exit", color="#CC0000"), '&Quit', self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_action = QAction(qta.icon("fa5s.caret-right", color="#228B22"), 'bomcheck_help', self)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self._help)
        help_menu.addAction(help_action)

        helpgui_action = QAction(qta.icon("fa5s.caret-right", color="#228B22"), 'bomcheckgui help', self)
        helpgui_action.triggered.connect(self._helpgui)
        help_menu.addAction(helpgui_action)

        helptrb_action = QAction(qta.icon("fa5s.caret-right", color="#228B22"), 'Troubleshoot', self)
        helptrb_action.triggered.connect(self._helptroubleshoot)
        help_menu.addAction(helptrb_action)

        bcgui_license = QAction(qta.icon("fa5s.caret-right", color="#228B22"), 'License', self)
        bcgui_license.triggered.connect(self._bcgui_license)
        help_menu.addAction(bcgui_license)

        softwareHomeSite = QAction(qta.icon("fa5s.caret-right", color="#228B22"), "bomcheck's web site", self)
        softwareHomeSite.triggered.connect(self._softwareHomeSite)
        help_menu.addAction(softwareHomeSite)

        about_action = QAction(qta.icon("ei.info-circle", color="#228B22"), '&About', self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.lstbox_view = ListboxWidget(self)
        self.lstbox_view.setWordWrap(True)
        self.setCentralWidget(self.lstbox_view)

    def openfolder(self):
        ''' Open the folder determined by variable "self.folder"'''

        err = False
        try:   # get BOM folder name from 1st item in drag/drop list
            self.folder = os.path.dirname(self.lstbox_view.item(0).text())
            with open(self.configdb, 'r+') as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                self.dbdic['folder'] = self.folder
                file.seek(0)
                file.write(str(self.dbdic))
                file.truncate()
            self.folder = self.dbdic['folder']
            os.system(cmdtxt(self.folder))
        except Exception as e:  # it an error occured, most likely and AttributeError
            print("error2 at MainWindow/openfolder", e)
            print("error2 at MainWindow/openfolder... possibly due to no data in drag&drop zone")
            err = True

        if err:
            try:
                with open(self.configdb, 'r') as file:
                    x = file.read()
                    self.dbdic = ast.literal_eval(x)
                self.folder = self.dbdic.get('folder', '')
                if self.folder:
                    os.system(cmdtxt(self.folder))
                else:
                    msg = ('Drag in some files first.  Thereafter\n'
                       'clicking the folder icon will open the\n'
                       'folder where BOMs are located.')
                    msgtitle = 'Folder location not set'
                    message(msg, msgtitle, msgtype='Information')
            except Exception as e:  # it an error occured, moset likely and AttributeError
                print("Error 103 at MainWindow/openfolder", e)

    def execute(self):
        global printStrs, standardflow

        try:
            with open(self.configdb, 'r+') as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                try:
                    self.folder = os.path.dirname(self.lstbox_view.item(0).text())
                    self.dbdic['folder'] = self.folder
                    file.seek(0)
                    file.write(str(self.dbdic))
                    file.truncate()
                except Exception as e:  # it an error occured, moset likely and AttributeError
                    print("error4 at MainWindow/execute", e)
        except Exception as e:  # it an error occured, moset likely and AttributeError
            print("error5 at MainWindow/execute", e)

        ask = self.dbdic.get('ask', False)
        defaultfname = self.getdefaultfname()
        if ask:
            standardflow = False
            # AskDialog sets standardflow, a global variable, to True if user hits the OK button
            dlg = AskDialog(defaultfname)  # call up the dialog box to add a new record.
            dlg.exec_()
            try:
                with open(self.configdb, 'r') as file:
                    x = file.read()
                    self.dbdic = ast.literal_eval(x)
            except Exception as e:  # it an error occured, moset likely and AttributeError
                print("error10 at MainWindow/execute", e)
        else:
            standardflow = True
            try:
                with open(self.configdb, 'r+') as file:
                    x = file.read()
                    self.dbdic = ast.literal_eval(x)
                    self.dbdic['file2save2'] = defaultfname
                    file.seek(0)
                    file.write(str(self.dbdic))
                    file.truncate()
            except Exception as e:  # it an error occured, moset likely and AttributeError
                   msg = ("Error 102:\n\n"
                   "Unable to read/write to config.txt in order to record the\n"
                   "folder location the last folder containing BOMs.\n"
                   "Otherwise the program will run as normal.\n\n" + str(e))
                   msgtitle = 'Warning'
                   message(msg, msgtitle, msgtype='Warning', showButtons=False)

        self.createdfile = ''
        files = []
        n = self.lstbox_view.count()
        for i in range(n):
            files.append(self.lstbox_view.item(i).text())

        if standardflow == True:
            dfs, df, msg = bomcheck.bomcheck(files, d=self.drop_chkbox.isChecked(),
                               b=self.across_chkbox.isChecked(),
                               dbdic = self.dbdic, x=self.dbdic['autosave'])
        else:
            msg = []

        createdfile = 'Created file: unknown'
        for x in msg:
            if 'Created file:' in x and len(x) > 4:
                k = x.strip('\n')
                if '/' in k:
                    lst = k.split('/')
                    createdfile = 'Created file: .../' + '/'.join(lst[-3:])
                elif '\\' in k:
                    lst = k.split('\\')
                    createdfile = 'Created file: ...\\' + '\\'.join(lst[-3:])
            elif 'Created file:' in x:
                createdfile = x

        if len(msg) == 1 and  'Created file:' in msg[0]:
            del msg[0]

        self.statusbar.showMessage(createdfile, 1000000)
        if msg:
            msgtitle = 'bomcheck discrepancy warning'
            message(str(''.join(msg)), msgtitle)
        if 'DataFrame' in str(type(df)):
            df_window = DFwindow(df, self)
            df_window.resize(1175, 800)
            df_window.setWindowTitle('Checked BOMs')
            df_window.show()
        if 'DataFrame' in str(type(dfs)):
            df_window = DFwindow(dfs, self)
            df_window.resize(775, 800)
            df_window.setWindowTitle('CAD BOMs for which corresponding ERP BOMs not supplied')
            df_window.show()

    def clear(self):
        self.lstbox_view.clear()

    def _help(self):
        webbrowser.open('https://htmlpreview.github.io/?https://github.com/kcarlton55/bomcheck/blob/master/help_files/bomcheck_help.html')

    def _helpgui(self):
        webbrowser.open('https://htmlpreview.github.io/?https://github.com/kcarlton55/bomcheck/blob/master/help_files/bomcheckgui_help.html')

    def _helptroubleshoot(self):
        webbrowser.open('https://htmlpreview.github.io/?https://github.com/kcarlton55/bomcheck/blob/master/help_files/bomcheck_troubleshoot.html')

    def _bcgui_license(self):
        webbrowser.open('https://github.com/kcarlton55/bomcheckgui/blob/main/LICENSE.txt')

    def _softwareHomeSite(self):
        webbrowser.open('https://github.com/kcarlton55/bomcheck')

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def settings(self):
        dlg = SettingsDialog()
        dlg.exec_()

    def getdefaultfname(self):
        '''Look at the list of filenames that have been dropped.  From that
        list look for a name that ends with '_sl.xlsx', and extract a potential
        name to assign to the bomcheck output file.  E.g. from 093345_sl.xlsx,
        present to the user: 093345_bomcheck.  If no filename found ending
        with _sl.xlsx, or if more than one such file, then present the name:
        bomcheck.

        Returns
        -------
        defaultFname: str
            default filename for the output xlsx file that bomcheck creates.
        '''
        j = 0
        files = []
        found = None
        n = self.lstbox_view.count()
        for i in range(n):
            files.append(self.lstbox_view.item(i).text())
        for f in files:
            if '_sl.xls' in f.lower():
                found = os.path.splitext(os.path.basename(f))[0]  # name sripped of path and extension
                found = found[:-3]  # take the _sl characters off the end
                j += 1
        if found and j == 1:
            defaultFname = found + '_bomcheck'
        else:
            defaultFname = 'bomcheck'
        return defaultFname


class AskDialog(QDialog):
    ''' A dialog box asking the user what the output filename should be.
    '''
    def __init__(self, default):
        super(AskDialog, self).__init__()

        global standardflow
        standardflow = False  # Assumes that the user won't hit the OK button

        self.setWindowTitle('Filename for results?')
        self.setFixedWidth(350)
        self.setFixedHeight(150)

        layout = QVBoxLayout()

        self.fnameinput = QLineEdit()
        self.fnameinput.setPlaceholderText('Filename for the bomcheck file')
        self.fnameinput.setMaxLength(40)
        self.fnameinput.setText(default)
        layout.addWidget(self.fnameinput)

        self.QBtn = QPushButton('text-align:center')
        self.QBtn.setText("OK")
        self.QBtn.setMaximumWidth(75)
        self.QBtn.clicked.connect(self.fname)

        hbox = QHBoxLayout()
        hbox.addWidget(self.QBtn)
        layout.addLayout(hbox)
        self.setLayout(layout)

    def fname(self):
        global standardflow

        askfname = self.fnameinput.text()
        if askfname.strip() == '':
            askfname = 'bomcheck'
        askfname = os.path.splitext(os.path.basename(askfname))[0]

        configdb = get_configfn()
        try:
            with open(configdb, 'r+') as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                self.dbdic['file2save2'] = askfname
                file.seek(0)
                file.write(str(self.dbdic))
                file.truncate()
        except Exception as e:  # if an error occured, moset likely and AttributeError
            print("Error 103 at AskDialog\n\n", e)
        standardflow = True
        self.close()


class SettingsDialog(QDialog):
    ''' A dialog box asking the user what the settings he would like to make.
    '''
    def __init__(self):
        super(SettingsDialog, self).__init__()

        self.setWindowTitle('Settings')
        self.setFixedWidth(450)
        self.setFixedHeight(500)  # was 150

        layout = QVBoxLayout()

        self.configdb = ''
        try:
            self.configdb = get_configfn()
            with open(self.configdb, 'r') as file: # Use file to refer to the file object
                x = file.read()
            self.dbdic = ast.literal_eval(x)
        except Exception as e:  # it an error occured, moset likely and AttributeError
            print("error8 at SettingsDialog", e)

        self.ask_chkbox = QCheckBox('Ask what name the bomcheck file should be.')
        _bool = self.dbdic.get('ask', False)
        self.ask_chkbox.setChecked(_bool)
        layout.addWidget(self.ask_chkbox)

        self.overwrite_chkbox = QCheckBox('Allow overwrite of existing bomcheck file.')
        _bool = self.dbdic.get('overwrite', True)
        self.overwrite_chkbox.setChecked(_bool)
        layout.addWidget(self.overwrite_chkbox)

        self.autosave_chkbox = QCheckBox('Automatically save results to an csv file.')
        _bool = self.dbdic.get('autosave', False)
        self.autosave_chkbox.setChecked(_bool)
        layout.addWidget(self.autosave_chkbox)

        hbox1 = QHBoxLayout()

        self.decplcs = QComboBox()
        self.decplcs.addItems(['0', '1', '2', '3', '4', '5'])
        _decplcs = str(self.dbdic.get('accuracy', 2))
        self.decplcs.setCurrentText(_decplcs)
        hbox1.addWidget(self.decplcs)
        decplcs_label = QLabel()
        decplcs_label.setText('Round SW converted lengths to X decimal plcs.')
        hbox1.addWidget(decplcs_label)

        layout.addLayout(hbox1)

        hbox2 =  QHBoxLayout()

        self.swum = QComboBox()
        self.swum.addItems(['in', 'ft', 'yd', 'mm', 'cm', 'm'])
        _from_um = str(self.dbdic.get('from_um', 'in'))
        self.swum.setCurrentText(_from_um)
        hbox2.addWidget(self.swum)
        swum_label = QLabel()
        swum_label.setText('SolidWorks U/M' + 10*' ')
        hbox2.addWidget(swum_label)

        empty_label1 = QLabel()
        empty_label1.setText('   ')
        hbox2.addWidget(empty_label1)

        self.slum = QComboBox()
        self.slum.addItems(['in', 'ft', 'yd', 'mm', 'cm', 'm'])
        _to_um = str(self.dbdic.get('to_um', 'ft'))
        self.slum.setCurrentText(_to_um)
        hbox2.addWidget(self.slum)
        slum_label = QLabel()
        slum_label.setText('SyteLine U/M' + 20*' ')
        hbox2.addWidget(slum_label)

        layout.addLayout(hbox2)

        drop_label = QLabel()
        drop_label.setText('drop list (Ignore these pt. nos. shown in BOMs):')
        layout.addWidget(drop_label)

        self.drop_input = QTextEdit()
        self.drop_input.setPlaceholderText('Separate pt. nos. with commas and/or spaces.  Letters are case sensitive')
        if 'udrop' in self.dbdic:
            self.drop_input.setPlainText(self.dbdic.get('udrop', ''))
        layout.addWidget(self.drop_input)

        exceptions_label = QLabel()
        exceptions_label.setText('exceptions list (exceptions to pt. nos. in the drop list):')
        layout.addWidget(exceptions_label)

        self.exceptions_input = QTextEdit()
        self.exceptions_input.setPlaceholderText('Separate pt. nos. with commas and/or spaces.  Letters are case sensitive.')
        if 'uexceptions' in self.dbdic:
            self.exceptions_input.setPlainText(self.dbdic.get('uexceptions', ''))
        layout.addWidget(self.exceptions_input)

        ## added 2/23/22
        cfgpathname_label = QLabel()
        cfgpathname_label.setText('pathname of bomcheck.cfg file')
        layout.addWidget(cfgpathname_label)

        self.cfgpathname_input = QTextEdit()
        self.cfgpathname_input.setPlaceholderText('e.g.: C:\\Users\\Documents\\bomcheck.cfg')
        if 'cfgpathname' in self.dbdic:
            self.cfgpathname_input.setPlainText(self.dbdic.get('cfgpathname', ''))
        layout.addWidget(self.cfgpathname_input)
        ##

        ############################################################
        authorname_label = QLabel()
        authorname_label.setText('Author: ')
        layout.addWidget(authorname_label)

        self.authorname_input = QLineEdit()
        self.authorname_input.setPlaceholderText(get_author(forPlaceHolder=True))
        if 'author' in self.dbdic:
            self.author =  self.dbdic.get('author')
            self.authorname_input.setText(self.author)
        layout.addWidget(self.authorname_input)

        ############################################################


        self.QBtnOK = QPushButton('text-align:center')
        self.QBtnOK.setText("OK")
        self.QBtnOK.setMaximumWidth(75)
        self.QBtnOK.clicked.connect(self._done)

        self.QBtnCancel = QPushButton('text-align:center')
        self.QBtnCancel.setText("Cancel")
        self.QBtnCancel.setMaximumWidth(75)
        self.QBtnCancel.clicked.connect(self.cancel)

        hbox = QHBoxLayout()
        hbox.addWidget(self.QBtnOK)
        hbox.addWidget(self.QBtnCancel)
        layout.addLayout(hbox)
        self.setLayout(layout)

    def _done(self):
        try:
            with open(self.configdb, "r+") as file:
                x = file.read()
                self.dbdic = ast.literal_eval(x)
                if self.ask_chkbox.isChecked():
                    self.dbdic['ask'] = True
                else:
                    self.dbdic['ask'] = False
                if self.overwrite_chkbox.isChecked():
                    self.dbdic['overwrite'] = True
                else:
                    self.dbdic['overwrite'] = False
                if self.autosave_chkbox.isChecked():
                    self.dbdic['autosave'] = True
                else:
                    self.dbdic['autosave'] = False

                drp = self.drop_input.toPlainText()
                self.dbdic['udrop'] = drp
                excep = self.exceptions_input.toPlainText()
                self.dbdic['uexceptions'] = excep
                cfgpn = self.cfgpathname_input.toPlainText()
                self.dbdic['cfgpathname'] = cfgpn

                self.dbdic['accuracy'] = int(self.decplcs.currentText())
                self.dbdic['from_um'] = self.swum.currentText()
                self.dbdic['to_um'] = self.slum.currentText()

                self.authorname = self.authorname_input.text().strip()
                if not self.authorname:
                    self.authorname = get_author(True)

                self.dbdic['author'] = self.authorname


                file.seek(0)
                file.write(str(self.dbdic))
                file.truncate()
        except Exception as e:  # it an error occured, most likely and AttributeError
            msg =  "error9 at SettingsDialog.  " + str(e)
            print(msg)
            message(msg, 'Error', msgtype='Warning', showButtons=False)
        self.close()

    def cancel(self):
        self.close()


class AboutDialog(QDialog):
    ''' Show company name, logo, program author, program creation date
    '''
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        if __version__ == bomcheck.get_version():
            msg = ('Description: A program to compare Bills of\n'
                     'Materials (i.e., BOMs)\n\n'
                     'Version: ' + __version__ + '\n\n'
                     'Author: Ken Carlton, 1/27/2021\n'
                     'kencarlton55@gmail.com')
        else:
            msg = ('Description: A program to compare Bills of\n'
                     'Materials (i.e., BOMs)\n\n'
                     'bomcheckgui version: ' + __version__ + '\n'
                     'bomcheck version: ' + bomcheck.get_version() + '\n'
                     '(bomcheck is incorporated within bomcheckgui)\n\n'
                     'Author: Ken Carlton, 1/27/2021\n'
                     'kencarlton55@gmail.com')
        self.setFixedHeight(320)
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle('About')
        layout = QVBoxLayout()
        layout.addWidget(QLabel(msg))
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class ListboxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._placeholder_text = "Drag & Drop"

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        #global folder
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))

            self.addItems(links)

        else:
            event.ignore()

    # https://stackoverflow.com/questions/60076333/how-to-set-the-placeholder-text-in-the-center-when-the-qlistwidget-is-empty
    @property
    def placeholder_text(self):
        return self._placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, text):
        self._placeholder_text = text
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.setPen(QColor(192, 192, 192))
            painter.setFont(QFont('Decorative', 20, QFont.Bold))
            painter.save()
            fm = self.fontMetrics()
            elided_text = fm.elidedText(
                self.placeholder_text, Qt.ElideRight, self.viewport().width()
            )
            painter.drawText(self.viewport().rect(), Qt.AlignCenter, elided_text)
            painter.restore()


def cmdtxt(foldr):
    ''' Create a dirpath name based on a URI type scheme.  Put in front of
    it the command that will be capable of opening it in file manager program.

    e.g. in Windows:
        exlorer file:///C:/SW_Vault/CAD%20Documents/PRODUCTION%20SYSTEMS

    e.g. on my Ubuntu Linux system:
        thunar file:///home/ken/tmp/bom%20files

    Where %20 is equivalent to a space character.
    referece: https://en.wikipedia.org/wiki/File_URI_scheme
    '''
    if sys.platform[:3] == 'win':
        foldr = foldr.replace(' ', '%20')
        command = 'explorer file:///' + foldr
    elif sys.platform[:3] == 'lin':
        homedir = os.path.expanduser('~')
        foldr = os.path.join(homedir, foldr)
        foldr = foldr.replace(' ', '%20')
        command = 'thunar file:///' + foldr  # thunar is the name of a file manager
    return command


def message(msg, msgtitle, msgtype='Warning', showButtons=False):
    '''
    UI message to show to the user

    Parameters
    ----------
    msg: str
        Message presented to the user.
    msgtitle: str
        Title of the message.
    msgtype: str, optional
        Type of message.  Currenly only valid input is 'Warning'.
        The default is 'Warning'.
    showButtons: bool, optional
        If True, show OK and Cancel buttons. The default is False.

    Returns
    -------
    retval: QMessageBox.StandardButton
        "OK" or "Cancel" is returned
    '''
    msgbox = QMessageBox()
    if msgtype == 'Warning':
        msgbox.setIcon(QMessageBox.Warning)
    elif msgtype == 'Information':
        msgbox.setIcon(QMessageBox.Information)
    msgbox.setWindowTitle(msgtitle)
    msgbox.setText(msg)
    if showButtons:
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retval = msgbox.exec_()
    return retval


def get_configfn():
    '''1. Get the pathname to store user defined settings.  The file will be
    named config.txt.  The pathname will be vary depending on who's logged in.
    It will look like: C:\\Users\\Ken\\AppData\\Local\\bomcheck\\config.txt.
    2.  If a Linux system is used, the pathname will look like:
    /home/Ken/.bomcheck/config.txt
    3.  If directories in the path do not already exists, crete them.
    4.  If the config.txt file doesn't already exist, create it and put in it
    some inital data: {'udrop':'3*-025'}
    '''
    if sys.platform[:3] == 'win':  # if a Window operating system being used.
        datadir = os.getenv('LOCALAPPDATA')
        path = os.path.join(datadir, 'bomcheck')
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        configdb = os.path.join(datadir, 'bomcheck', 'config.txt')

    elif sys.platform[:3] == 'lin':  # if a Linux operating system being used.
        homedir = os.path.expanduser('~')
        path = os.path.join(homedir, '.bomcheck')
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        configdb = os.path.join(homedir, '.bomcheck', 'config.txt')

    else:
        printStr = ('At method "get_configfn", a suitable path was not found to\n'
                    'create file config.txt.  Notify the programmer of this error.')
        print(printStr)
        return ""

    _bool = os.path.exists(configdb)
    if not _bool or (_bool and os.path.getsize(configdb) == 0):
        with open(configdb, 'w') as file:
            file.write("{'udrop':'3*-025'}")

    return configdb


def get_author(forPlaceHolder=False):
    # first assume that "author" name not in file containing user settings
    if os.getenv('USERNAME'):
        author = os.getenv('USERNAME')  # Works only on MS Windows
    elif sys.platform[:3] == 'lin':  # I'm working on my Linux system
        author = 'kcarlton'
    else:
        author = 'unknown'

    if forPlaceHolder:
        return author

    # if "author" is in the settings file:
    settingsfn = get_configfn()
    try:
        with open(settingsfn, 'r') as file:
            x = file.read()
            settingsdic = ast.literal_eval(x)
            author = settingsdic.get('author', author)
    except Exception as e:
        msg =  "error12 at get_author.  " + str(e)
        print(msg)
        message(msg, 'Error', msgtype='Warning', showButtons=False)
    return author


class DFwindow(QDialog):
    ''' Displays a Pandas DataFrame in a GUI window and shows three buttons
        below it: Print, Print Preview, and Save as .xlsx.
    '''
    def __init__(self, df, parent=None):
        super(DFwindow, self).__init__(parent)

        self.df_xlsx = df.copy()  # make a copy.  This will be used to save to an Excel file
        self.df = merge_index(df)  # use for disply to user and for printing
        self.columnLabels = self.df.columns
        model = DFmodel(self.df, self)

        self.view = QTableView(self)
        self.view.setModel(model)
        self.view.setShowGrid(False)
        self.view.setAlternatingRowColors(True)
        self.view.resizeColumnsToContents()
        header = self.view.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft)

        self.buttonPrint = QPushButton('&Print', self)
        self.buttonPrint.setShortcut('Ctrl+P')
        self.buttonPrint.clicked.connect(self.handlePrint)

        self.buttonPreview = QPushButton('Print Preview', self)
        self.buttonPreview.clicked.connect(self.handlePreview)

        self.save_as_xlsx = QPushButton('&Save as .csv', self)
        self.save_as_xlsx.setShortcut('Ctrl+S')
        self.save_as_xlsx.clicked.connect(self.save_xlsx)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.reject)

        layout = QGridLayout(self)
        layout.addWidget(self.view, 0, 0, 1, 4)
        layout.addWidget(self.buttonPrint, 1, 0)
        layout.addWidget(self.buttonPreview, 1, 1)
        layout.addWidget(self.save_as_xlsx, 1, 2)
        layout.addWidget(buttonBox, 1, 3)

    def handlePrint(self):
        printer = QtPrintSupport.QPrinter()
        printer.setPaperSize(printer.Letter)
        printer.setOrientation(printer.Landscape)
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            self.handlePaintRequest(dialog.printer())

    def handlePreview(self):
        printer = QtPrintSupport.QPrinter()
        printer.setPaperSize(printer.Letter)
        printer.setOrientation(printer.Landscape)
        dialog = QtPrintSupport.QPrintPreviewDialog(printer, self)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    def handlePaintRequest(self, printer):
        document = QTextDocument()
        cursor = QTextCursor(document)
        font = QFont()
        font.setPointSize(7)
        document.setDefaultFont(font)
        model = self.view.model()
        tableFormat = QTextTableFormat() # https://stackoverflow.com/questions/65744428/qtexttable-insert-a-line-in-a-cell
        tableFormat.setBorder(0)
        tableFormat.setCellPadding(2)

        cursor.insertTable(model.rowCount() + 1,  # the + 1 accounts for col labels that will be added
                           model.columnCount(), tableFormat)

        lst = []
        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                lst.append(model.item(row, column))
        for c in reversed(self.columnLabels):
            lst.insert(0, c)


        for l in lst:
            cursor.insertText(l)
            cursor.movePosition(QTextCursor.NextCell)

        printer.setPaperSize(QtPrintSupport.QPrinter.Letter)
        document.print_(printer)

    def save_xlsx(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', filter="csv (*.csv)",
                                    options=QFileDialog.DontConfirmOverwrite)
        dirname, f = os.path.split(filename)
        f, e = os.path.splitext(f)
        results2export = [('BOM Check', self.df_xlsx)]
        export2excel(dirname, f, results2export)


class DFmodel(QAbstractTableModel):
    ''' Enables a Pandas DataFrame to be able to be shown in a GUI window.
    '''
    def __init__(self, data, parent=None):
        super(DFmodel, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def item(self, row, col):
        return str(self._data.iat[row, col])


def merge_index(df):
    ''' This function will, first, take a pandas dataframe, df, whose index
    values are the assy and item no. colunns, and will merge those into the main
    body of the df object.  The new index will be the standard type of dataframe
    index, 0, 1, 2, 3, and so forth.  Panda's "reset_index" function is used
    to do this,  The resulting dataframe will look like this:

       assy                item
    0  0300-2022-384       6602-0400-000
    1  0300-2022-384       6602-0600-000
    2  2728-2020-908       6600-0025-001
    3  2730-2021-131       6600-0025-001
    4  2730-2021-131       6652-0025-005
    5  2730-2021-131       7215-0200-001
    6  6890-ACV0098372-01  2915-0050-000

    The column 0, 1, 2, 3,... is the index column.  Then, second, this function
    will remove duplicate assy nos. so that the data frame looks like this:

    assy                item
    0  0300-2022-384       6602-0400-000
    1                      6602-0600-000
    2  2728-2020-908       6600-0025-001
    3  2730-2021-131       6600-0025-001
    4                      6652-0025-005
    5                      7215-0200-001
    6  6890-ACV0098372-01  2915-0050-000
    '''
    if df.index.values.tolist()[0] != 0:
        df.reset_index(inplace=True)
    is_duplicated = df.iloc[:, 0].duplicated()  # False, True, False, False, True, True, False
    df.iloc[:, 0] = df.iloc[:, 0] * ~is_duplicated  # where df.iloc[:, 0] is 0300-2022-384, 0300-2022-384, 2728-2020-908, ...
    return df



app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())
