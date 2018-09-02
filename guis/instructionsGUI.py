#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:01:42 2018

@author: robertahunt
"""

from PyQt5 import QtWidgets
from basicGUI import basicGUI

class instructionsGUI(basicGUI):
    def __init__(self):
        super(instructionsGUI, self).__init__()
        
        self.inst_title = self.headerLabel('Instructions')
        self.inst_desc = QtWidgets.QLabel(
'''
1. Make sure camera is on, usb cable is connected, 
and camera is set to auto-focus.

2. 

If you have any questions, 
shoot roberta a mail: ngw861@alumni.ku.dk. 
If it is urgent, call her: 91 93 20 26
''')
        self.initUI()
        
    def initUI(self):
        self.grid.addWidget(self.inst_title)
        self.grid.addWidget(self.inst_desc)
        self.setLayout(self.grid)
