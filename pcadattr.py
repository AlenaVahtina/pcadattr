#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import loads, dumps
from datetime import datetime
import re, os, sys
from io import StringIO
import contextlib
import logging

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from PyQt5.QtSvg import *
from PyQt5 import uic

#pyinstaller pcadattr.py --add-data "main.ui;." -y --onefile --windowed

try:
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.dirname(os.path.realpath(__file__))

#Надеюсь, что эту строку гед-то здесь
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)

def Sandbox(code,obj):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()

    ns_globals = {}
    ns_locals = {}
    out, err, exc = None, None, None

    try:
        #print(code)
        exec(code, ns_globals, ns_locals)
    except:
        import traceback
        exc = traceback.format_exc()

    out = redirected_output.getvalue()
    err = redirected_error.getvalue()

    # reset outputs to the original values
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    print(out)

    return out, err, exc

def findAll(a,key,val = None):
    if val:
        return [x for x in a if x[0] == key and x[1] == val ]
    else:
        return [x for x in a if x[0] == key]


def find(a,key,val = None):
    return findAll(a,key,val)[0]


def findPath(a,path,lastval = None):
    b = a
    for x in path[:-1]:
        b = find(b,x)
    return findAll(b,path[-1],lastval)

def mfloat(s):
    if 'mm' in s:
        return float(s.replace('mm',''))/0.0254
    else:
        return float(s)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        Ui_MainWindow, QtBaseClass = uic.loadUiType(os.path.join(base_path,"main.ui"))
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.settings = QSettings("settingsDemo.conf")
        self.fdata = [] #readed array
        self.ui.listWidget.itemClicked.connect(self.showComent)
        self.execfuncs()

    def pdata(self,data,s,tabdepth,d=0):
        if type(data)==list:
            if d<tabdepth:
                if self.prev_str:
                    s.write('\n')
                s.write(' '*2*(d-1))
            if d:
                s.write('(')
            for x in data:
                self.pdata(x,s,tabdepth,d+1)
            if d:
                if d<(tabdepth-1) and (not self.prev_str ):
                    s.write(' '*2*(d-1))
                s.write(')')
            if d<tabdepth:
                s.write('\n')
            self.prev_str = False
        else:
            s.write(data)
            self.prev_str = True
            s.write(' ')

    @pyqtSlot()
    def on_pushButton_in_clicked(self):
        self.ui.lineEdit_in.setText(QFileDialog.getOpenFileName(self,"Open eagle cad file", QFileInfo(self.ui.lineEdit_in.text()).filePath(), "PCAD Files (*.pcb)")[0])
        if self.ui.lineEdit_in.text() != "" :
            self.ui.lineEdit_out.setText(self.ui.lineEdit_in.text())
            finf = QFileInfo(self.ui.lineEdit_out.text())
            self.ui.lineEdit_out.setText(finf.path()+"/"+''.join(finf.fileName().split(".")[:-1])+"_SB.pcb")

    @pyqtSlot()
    def on_pushButton_out_clicked(self):
        fileDialog = QFileDialog()
        fileDialog.setDefaultSuffix("pcb")
        self.ui.lineEdit_out.setText(fileDialog.getSaveFileName(self, "Save pcad file", QFileInfo(self.ui.lineEdit_out.text()).filePath(), "PCAD Files (*.pcb)")[0]);

    @pyqtSlot()
    def on_pushButton_clicked(self):
        if not self.ui.lineEdit_out.text() or not self.ui.lineEdit_in.text():
            # print("empty")
            logging.info(u'empty')
            return
        new_file = QFileInfo(self.ui.lineEdit_out.text())
        if new_file.exists():
            if(QMessageBox.information(self, "Converter","Output file already exists. Are you sure you want to continue?", QMessageBox.Ok|QMessageBox.Cancel)==QMessageBox.Cancel):
                return
        self.readfile()
        self.checkFunction()
        self.writefile()

        
    def writefile(self):
        self.prev_str = False #thing for writing
        b = StringIO()
        self.pdata(self.fdata,b,6)
        with open(self.ui.lineEdit_out.text(),'w', encoding="cp1251", errors="surrogateescape") as f:
            f.write(b.getvalue())
        #sys.stdout.write(b.getvalue())

    def readfile(self):
        self.fdata = []
        with open(str(self.ui.lineEdit_in.text()),'r',encoding="cp1251") as fl:
            data = fl.read()#.decode("utf-8", "replace")
            data = [p for p in re.split("(\s|\\\".*?\\\"|\)|\()", data) if p.strip()]
            self.fdata.append(list())
            for x in data:
                if x == '(':
                    self.fdata.append(list())
                elif x == ')':
                    d = self.fdata.pop()
                    self.fdata[-1].append(d)
                else:
                    self.fdata[-1].append(x)
        self.fdata = self.fdata[0]

    def execfuncs(self):
        global fdata 
        fdata = self.fdata
        for name in os.listdir(path="."): 
            if name.endswith('.fun'):
                file = open (name, 'r', encoding="utf8")
                fun=file.read()
                try:
                    exec(fun)
                    exec('self.'+name.split(".")[0]+"="+name.split(".")[0])
                    #try:
                    #    exec(name.split(".")[0]+"()")
                    #except:
                    #    print ("error of result")
                except:
                    print ("error of function")
                #add CheckBox
                item = QListWidgetItem(name.split(".")[0])
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                # item.setCheckState(Qt.Unchecked)
                is_set = int(self.settings.value(name.split(".")[0]))
                if is_set == 1:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                self.ui.listWidget.addItem(item)
        self.fdata = fdata

    @pyqtSlot()
    def checkFunction (self):
        for x in range(self.ui.listWidget.count()):
            fun = self.ui.listWidget.item(x)
            if fun.checkState() == Qt.Checked:
                exec('self.'+fun.text()+"(self)")
                self.settings.setValue(fun.text(), "1")
            else: 
                self.settings.setValue(fun.text(),"0")


    def addTable(self, a, tabname = "", columnName=[],rowName=[]):
        # Create table
        table    = QTableWidget()
        # Add table
        self.ui.tabWidget.addTab(table,tabname)
        # a = ([["1","2","3"],["4","5","6"]])
        table.setRowCount(len(a))
        table.setColumnCount(len(a[0]))
        # Hide row
        if columnName == []:
            table.horizontalHeader().hide()
        else:
            table.setHorizontalHeaderLabels(columnName)
        # Hide column
        if rowName == []: 
            table.verticalHeader().hide()
        else:
            table.setVerticalHeaderLabels(rowName)
        for row in range(len(a)):
            for element in range(len(a[row])):
                table.setItem(row,element, QTableWidgetItem(a[row][element]))

    @pyqtSlot(QListWidgetItem)
    def showComent (self, item):
        self.ui.plainTextEdit.clear()
        fun=open(item.text()+'.fun',"r", encoding="utf8")
        for line in fun:
            if line.startswith("#"):
                self.ui.plainTextEdit.setPlainText(self.ui.plainTextEdit.toPlainText()+line)
            else:
                return 

    def keyPressEvent(self,event):     
        if event.key()==Qt.Key_F5:
            self.ui.listWidget.clear()
            self.execfuncs()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
