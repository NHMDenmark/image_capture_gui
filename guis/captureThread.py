#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 10:28:02 2018

@author: robertahunt
"""
import os
import subprocess

from time import sleep
from PyQt5 import QtCore
from settings.local_settings import LOCAL_IMAGE_STORAGE_PATH

#from basicGUI import basicGUI

class capturePreview(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.paused = False

    def run(self):
        while( self.isRunning() ):
            if self.paused == False:
                self.running = True
                try:
                    subprocess.check_output(['gphoto2','--capture-preview',
                                             '--force-overwrite','--filename',
                                             os.path.join(LOCAL_IMAGE_STORAGE_PATH,
                                                          'preview.jpg')]
                                             )
                except Exception as ex:
                    pass
                self.running = False
                #print('Updated Preview')
            sleep(1)
            
    def pause(self):
        #print('Capture Paused')
        self.paused = True
        while self.running == True:
            sleep(1)
        return True
        
    def resume(self):
        #print('Capture Resumed')
        self.paused = False

def init():
    global captureThread
    captureThread = capturePreview()
    captureThread.start()