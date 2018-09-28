#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 19:27:30 2018

@author: robertahunt
"""
import sys

import warnings
import subprocess

from guis import captureThread
from serial import Serial
from serial.tools import list_ports
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
        print('Sent command: ' + ' '.join(args))
        if (args[0] == 'gphoto2'):
            captureThread.captureThread.pause()

        try:
            output = subprocess.check_output(args)
            if (args[0] == 'gphoto2'):
                captureThread.captureThread.resume()
            return output
        except Exception as ex:
            #self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))
            if (args[0] == 'gphoto2'):
                captureThread.captureThread.resume()
            return ex
        
    def warn(self, msg, _exit=False):
        warnings.warn(msg)
        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle('Warning Encountered')
        warning.setText(msg)
        warning.exec_()
        if _exit: 
            sys.exit()
        
    
    #def closeEvent(self, event):
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        #    event.accept()
        #else:
        #    event.ignore()
        
class Arduino():
    def __init__(self):
        self.port = self.getArduinoPort()
        self.ser = Serial(self.port, 9600)
        
    def getArduinoPort(self):
        ports = list(list_ports.comports())
        for p in ports:
            if 'Arduino' in str(p.manufacturer):
                return p.device
        else:
            return None
        
    def moveCamera(self, direction, cm):
        assert direction in ['u','d']
        while True:
            if (self.ser.inWaiting()>0):  # Check if board available
                self.ser.write("%s %s\n"%(direction,cm))
                break 
    
    def readline(self):
        return self.ser.readline()
    
    def getHeight(self):
        while True:
            line  = self.ser.readline()
            if 'mm' in line:
                return float(line.split('mm')[0])
            print(line)
        
    def cameraUpMm(self):
        self.moveCamera('u','0.1')
    def cameraUpCm(self):
        self.moveCamera('u','1')
    def cameraDownMm(self):
        self.moveCamera('d','0.1')
    def cameraDownCm(self):
        self.moveCamera('d','1')
        
    def close(self):
        self.ser.close()