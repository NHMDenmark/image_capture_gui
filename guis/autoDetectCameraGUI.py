#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:38:47 2018

@author: robertahunt
"""

from PyQt5 import QtWidgets
from basicGUI import basicGUI

class autoDetectCameraGUI(basicGUI):
    def __init__(self):
        super(autoDetectCameraGUI, self).__init__()
        self.initUI()
    
    def initUI(self):
        auto_detect_output = self.testDetectCamera()
        auto_detect = QtWidgets.QLabel(auto_detect_output)
        self.grid.addWidget(auto_detect)
        self.setLayout(self.grid) 
        
