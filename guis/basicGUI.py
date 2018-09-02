#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 19:27:30 2018

@author: robertahunt
"""

import warnings
import subprocess

from PyQt5 import QtGui, QtWidgets, QtCore

class ClickableIMG(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.objectName())

class basicGUI(QtWidgets.QWidget):
    def __init__(self):
        super(basicGUI, self).__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

    def headerLabel(self, text):
        headerLabel = QtWidgets.QLabel(text)
        headerFont = QtGui.QFont("Times", 20, QtGui.QFont.Bold) 
        headerLabel.setFont(headerFont)
        return headerLabel

    def commandLine(self, args):
        assert isinstance(args,list)
        
        if ('captureThread' in globals()) & (args[0] == 'gphoto2'):
            captureThread.pause()

        try:
            output = subprocess.check_output(args)
            if ('captureThread' in globals()) & (args[0] == 'gphoto2'):
                captureThread.resume()
            return output
        except Exception as ex:
            self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))
            if ('captureThread' in globals()) & (args[0] == 'gphoto2'):
                captureThread.resume()
            return ex
        
    def warn(self, msg):
        warnings.warn(msg)
        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle('Warning Encountered')
        warning.setText(msg)
        warning.exec_()
        
    def testCameraConnection(self):
        output = self.commandLine(['gphoto2','--list-config'])
        if 'Error' in output:
            self.warn('''There is a problem sending commands to camera.
                      Please check usb cable, unplug and replug and try again''')
            
    def testDetectCamera(self):
        auto_detect_output = 'Cameras Detected: \n%s'%self.commandLine(['gphoto2','--auto-detect'])
        if len(auto_detect_output) <= 126:
            warning = 'Error xkcd1314: No cameras detected'
            self.warn(warning)
            sys.exit()
            return auto_detect_output + warning
        return auto_detect_output
    
    #def closeEvent(self, event):
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        #    event.accept()
        #else:
        #    event.ignore()
        
