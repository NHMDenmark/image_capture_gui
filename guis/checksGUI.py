#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 17:28:17 2018

@author: robertahunt
"""
import time
import serial

from PyQt5 import QtCore, QtWidgets

from guis.basicGUI import basicGUI
from guis.progressDialog import progressDialog

from guis.settings.local_settings import ARDUINO_PORT


class checksGUI(basicGUI):
    def __init__(self):
        super(checksGUI, self).__init__()
        
        self.progress = progressDialog()
        self.progress._open()
        
        
        self.progress.update(0,'Trying to Detect Camera.')
        #self.testDetectCamera()
        
        self.progress.update(20,'Testing Camera Connection')
        #self.testCameraConnection()
        
        self.progress.update(40,'Testing Arduino Connection')
        self.testArduinoConnection()
        
        self.progress.update(60,'Testing Sonar Data Collection')
        self.testGetSonarData()
        
        self.progress.update(80,'Testing Camera Movement')
        self.testMoveCamera()
        
        self.progress.update(100,'Done')
        self.progress.close()
       
            
    def testDetectCamera(self):
        auto_detect_output = 'Cameras Detected: \n%s'%self.commandLine(['gphoto2','--auto-detect'])
        if len(auto_detect_output) <= 126:
            warning = 'Error xkcd1314: No cameras detected'
            self.warn(warning, _exit=True)
            return auto_detect_output + warning
        return auto_detect_output
        
    def testCameraConnection(self):
        output = self.commandLine(['gphoto2','--list-config'])
        if 'Error' in str(output):
            self.warn('''There is a problem sending commands to camera. Please check usb cable, unplug and replug and try again''', _exit=True)
                      
    def testArduinoConnection(self):
        try:
            self.board = serial.Serial(ARDUINO_PORT, 9600)
        except:
            self.warn('Unable to connect to Arduino on Port: ' + ARDUINO_PORT + '. Please make sure arduino has power and is connected to the computer.',_exit=True)
            

    def testGetSonarData(self):
        pass
            
    def testMoveCamera(self):
    
        self.board.close()
        pass
        