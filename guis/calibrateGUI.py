#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 13:28:59 2018

@author: robertahunt
"""
import os
import time
from exifread import process_file
from PyQt5 import QtWidgets
from pprint import pprint

from basicGUI import basicGUI
from settings.local_settings import TEMP_IMAGE_CACHE_PATH

class calibrateGUI(basicGUI):
    def __init__(self):
        super(calibrateGUI, self).__init__()
        self.initUI()
        
    
    def initUI(self):
        self.calibrateButton = QtWidgets.QPushButton('Calibrate camera using grey card')
        self.calibrateButton.clicked.connect(self.calibrate)
        
        self.grid.addWidget(self.calibrateButton)
        self.setLayout(self.grid)
        
    def calibrate(self):
        #Set white balance to auto white balance
        print('Setting white balance to auto white balance')
        self.commandLine(['gphoto2', '--set-config-index', '/main/imgsettings/whitebalance=0'])
        
        #Take photo
        print('Taking photo')
        filePath = os.path.join(TEMP_IMAGE_CACHE_PATH, 'calibration_img.arw')
        self.commandLine(['gphoto2','--capture-image-and-download','--filename',filePath])
        #examine raw photo exif data - get color temp
        print('Examining raw exif data')
        time.sleep(1)
        f = open(filePath,'rb')
        tags = process_file(f)
        print(tags['EXIF WhiteBalance'], type(tags['EXIF WhiteBalance']))
        print(tags['EXIF WhiteBalance'].__dict__)
        print(tags.keys())
        pprint(tags)
        #Set White balance to set color temp
        print('Setting white balance to color temp')
        #set color temp to whatever it was.
        print('Setting color temp')
        
