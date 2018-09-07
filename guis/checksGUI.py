#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 17:28:17 2018

@author: robertahunt
"""
from PyQt5 import QtCore, QtWidgets

from guis.basicGUI import basicGUI


class checksGUI(basicGUI):
    def __init__(self):
        super(checksGUI, self).__init__()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkDetectCamera)
        self.timer.timeout.connect(self.checkCameraConnection)
        self.timer.start(5000)
        
        self.initUI()
        
    def initUI(self):
        self.auto_detect_camera_check = QtWidgets.QLabel('Auto Detect Camera: Unknown')
        self.usb_connection_check = QtWidgets.QLabel('Camera Connection: Unknown')
        
        self.grid.addWidget(self.auto_detect_camera_check)
        self.grid.addWidget(self.usb_connection_check)
        self.setLayout(self.grid)
        
        
    def checkDetectCamera(self):
        output = self.testDetectCamera()
        
        if 'Sony' in output:
            self.auto_detect_camera_check.setText("Auto Detect Camera: <font color='green'> OK</font>")
        else:
            self.auto_detect_camera_check.setText("Auto Detect Camera: <font color='red'> Error</font>")
        self.setLayout(self.grid)
        
    def checkCameraConnection(self):
        output = self.testCameraConnection()
        
        if output is None:
            self.usb_connection_check.setText("Camera Connection: <font color='green'> OK</font>")
        else:
            self.usb_connection_check.setText("Camera Connection: <font color='red'> Error</font>")
        self.setLayout(self.grid)