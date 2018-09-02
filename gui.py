# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:59:05 2018

@author: ngw861
"""
import os
import sys
import pprint
import subprocess

from time import sleep
from PyQt5 import QtGui, QtCore, QtWidgets

from guis.basicGUI import basicGUI
from guis.configGUI import openConfigGUI
from guis.liveViewGUI import liveViewGUI
from guis.imageViewGUI import imageViewGUI
from guis.instructionsGUI import instructionsGUI
from guis.autoDetectCameraGUI import autoDetectCameraGUI

    
class capturePreview(QtCore.QThread, basicGUI):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.paused = False

    def run(self):
        while( self.isRunning() ):
            if self.paused == False:
                self.running = True
                try:
                    subprocess.check_output(['gphoto2','--capture-preview','--force-overwrite'])
                except Exception as ex:
                    pass
                self.running = False
                #print('Updated Preview')
            sleep(2)
            
    def pause(self):
        self.paused = True
        while self.running == True:
            sleep(2)
        return True
        
    def resume(self):
        self.paused = False


class checksGUI(basicGUI):
    def __init__(self):
        super(checksGUI, self).__init__()
        self.initUI()
        
    def initUI(self):
        auto_detect_camera_check = self.checkDetectCamera()
        usb_connection_check = self.checkCameraConnection()
        
        self.grid.addWidget(auto_detect_camera_check)
        self.grid.addWidget(usb_connection_check)
        self.setLayout(self.grid)
        
        
    def checkDetectCamera(self):
        output = self.testDetectCamera()
        label = QtWidgets.QLabel('Auto Detect Camera: ')
        
        if 'Sony' in output:
            label.setText(label.text() + "<font color='green'> OK</font>")
            #headerFont = QtGui.QFont("Times", 20, QtGui.QFont.Bold) 
            #label.setFont()
            return label
        else:
            label.setText(label.text() + "<font color='red'> Error</font>")
            #headerFont = QtGui.QFont("Times", 20, QtGui.QFont.Bold) 
            #label.setFont()
            return label
        
    def checkCameraConnection(self):
        output = self.testCameraConnection()
        label = QtWidgets.QLabel('Camera Connection: ')
        if output is None:
            label.setText(label.text() + "<font color='green'> OK</font>")
            return label
        else:
            label.setText(label.text() + "<font color='red'> Error</font>")
            return label
        
class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        self.testCameraConnection()
        self.instructions = instructionsGUI()
        self.checks = checksGUI()
        self.auto_detect_camera = autoDetectCameraGUI()
        self.live_view = liveViewGUI()
        self.image_view = imageViewGUI()
        self.config = openConfigGUI()
        self.initUI()
        
    def initUI(self):        
        self.setWindowTitle('Upload Image to Database')  
        self.setWindowIcon(QtGui.QIcon('icon.png')) 
        
        okButton = QtWidgets.QPushButton("Save and Send to Database")
        cancelButton = QtWidgets.QPushButton("Cancel")
        
        self.grid.addWidget(self.instructions, 0, 0)
        self.grid.addWidget(self.auto_detect_camera, 1, 0)
        self.grid.addWidget(self.checks, 2, 0)
        self.grid.addWidget(self.image_view, 3, 0)
        self.grid.addWidget(self.config, 4, 0)
        self.grid.addWidget(self.live_view, 0, 1, 4, 1)
        self.grid.addWidget(okButton, 7, 0)
        self.grid.addWidget(cancelButton, 7, 1)
        self.setLayout(self.grid)
        
        self.show()
        

if __name__ == '__main__':
    global captureThread
    captureThread = capturePreview()
    captureThread.start()

    QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_())