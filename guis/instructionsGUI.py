#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:01:42 2018

@author: robertahunt
"""

from PyQt5 import QtWidgets
from guis.basicGUI import basicGUI


class progressDialog(basicGUI, QtWidgets.QMainWindow):
    def __init__(self):
        super(progressDialog, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.text = QtWidgets.QLabel('Working.')
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0,100)
        self.grid.addWidget(self.text)
        self.grid.addWidget(self.progressBar)
        self.setLayout(self.grid)
        
    def _open(self):
        self.progressBar.setValue(0)
        QtWidgets.QApplication.processEvents()
        self.raise_()
        self.show()
        QtWidgets.QApplication.processEvents()
        
    def update(self, value, text = None):
        if text is not None:
            self.text.setText(text)
        else:
            newText = self.text.text() + '.'
            self.text.setText(newText)
            
        self.progressBar.setValue(value)
        
        QtWidgets.QApplication.processEvents()

class instructionsGUI(basicGUI):
    def __init__(self):
        super(instructionsGUI, self).__init__()
        self.progress = progressDialog()
        self.inst_title = self.headerLabel('Instructions')
        self.inst_desc = QtWidgets.QLabel(
'''
If you have any questions, 
shoot Roberta a mail: ngw861@alumni.ku.dk. 
or if you want a timely reply, call her: 91 93 20 26


When Leaving:
Please turn off camera, computer, motor controller
and set camera battery bank to 'Charge'
''')
        self.initUI()
        
    def initUI(self):
        self.button = QtWidgets.QPushButton('Test Things')
        self.button.clicked.connect(self.test_things)
        self.grid.addWidget(self.inst_title)
        self.grid.addWidget(self.inst_desc)
        self.grid.addWidget(self.button)
        self.setLayout(self.grid)
        
    def test_things(self):
    
        self.progress._open()
        self.commandLine(['timeout','3'])
        print('Thinking')
        self.progress.update(30,'Thinking 1')
        self.commandLine(['timeout','3'])
        print('Thinking')
        self.progress.update(70,'Thinking 2')
        self.commandLine(['timeout','3'])
        print('Thinking')
        self.progress.update(100,'Thinking 3')
        self.progress.close()
        

    