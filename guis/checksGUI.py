#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 17:28:17 2018

@author: robertahunt
"""
import time

from serial import Serial
from PyQt5 import QtCore, QtWidgets

from guis.basicGUI import basicGUI, Arduino
from guis.progressDialog import progressDialog


class checksGUI(basicGUI):
    def __init__(self):
        super(checksGUI, self).__init__()
        
        self.progress = progressDialog()
        self.progress._open()
        
        self.progress.update(0,'Trying to Detect Camera.')
        self.testDetectCamera()
        
        self.progress.update(20,'Testing Camera Connection')
        self.testCameraConnection()
        
        self.progress.update(40,'Testing Arduino Connection')
        self.testArduinoConnection()
        
        #self.progress.update(60,'Testing Sonar Data Collection')
        #self.testGetSonarData()
        
        #self.progress.update(80,'Testing Camera Movement')
        #self.testMoveCamera()
        
        self.progress.update(100,'Done')
        self.arduino.close()
        self.progress.close()
       
            
    def testDetectCamera(self):
        try:
            auto_detect_output = 'Cameras Detected: \n%s'%self.commandLine(['gphoto2','--auto-detect'])
            if len(auto_detect_output) <= 126:
                warning = 'Error xkcd1314: No cameras detected. Please make sure camera is on and connected to the computer.'
                self.warn(warning, _exit=True)
        except Exception as ex:
            print(str(ex))

    def testCameraConnection(self):
        try:
            output = self.commandLine(['gphoto2','--list-all-config'])
            if 'Error' in str(output):
                self.warn('''Error xkcd806: There is a problem sending commands to camera. Please check usb cable, unplug and replug and try again.''', _exit=True)
        except Exception as ex:
            print(str(ex))
                
                
    def testArduinoConnection(self):
        try:
            self.arduino = Arduino()
        except Exception as ex:
            print(str(ex))
            self.warn('Error xkcd730: Unable to connect to Arduino. Please make sure arduino has power and is connected to the computer.',_exit=True)
            

    def testGetSonarData(self):
        try:
            height = self.arduino.getHeight()
        except Exception as ex:
            print(str(ex))
            self.warn('Error xkcd1590: Unable to read data from sonar sensor. Please make sure it is connected to the big black box.',_exit=True)
            
    def testMoveCamera(self):
        try:
            height_1 = self.arduino.getHeight()
            print(height_1)
            time.sleep(4)
            self.arduino.moveCamera('u','3')
            time.sleep(5)
            height_2 = self.arduino.getHeight()
            print(height_2)
            if height_2 - height_1 < 0.9:
                print(height_1, height_2)    
                self.arduino.moveCamera('d','3')
                self.warn('Error xkcd1428: It seems we cannot move the camera using the arduino.... That is not good.', _exit=True)
            self.arduino.moveCamera('d','4')
        except Exception as ex:
            print(str(ex))
            self.arduino.moveCamera('d','3')
            self.warn('Error xkcd510: Something went horribly wrong. Goodbye', _exit=True)
        

    