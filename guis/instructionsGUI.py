#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:01:42 2018

@author: robertahunt
"""

from PyQt5 import QtWidgets
from guis.basicGUI import basicGUI
from guis.progressDialog import progressDialog

class instructionsGUI(basicGUI):
    def __init__(self):
        super(instructionsGUI, self).__init__()
        self.inst_title = self.headerLabel('Instructions')
        self.inst_desc = QtWidgets.QLabel(
'''
If you have any questions, 
shoot Roberta a mail: XX@XX.dk. 
or if you want a timely reply, call her: XX XX XX XX


When Leaving:
Please turn off camera, computer, motor controller
and set camera battery bank to 'Charge'
''')
        self.initUI()
        
    def initUI(self):
        self.grid.addWidget(self.inst_title)
        self.grid.addWidget(self.inst_desc)
        self.setLayout(self.grid)
        

    
