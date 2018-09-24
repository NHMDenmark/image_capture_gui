# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:59:05 2018

@author: ngw861
"""
import os
import sys
import time

from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtCore#, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT)

from guis import captureThread
from guis.plotsGUI import plotsGUI
from guis.basicGUI import basicGUI
from guis.checksGUI import checksGUI
from guis.configGUI import openConfigGUI, configGUI
from guis.liveViewGUI import liveViewGUI
from guis.imageViewGUI import imageViewGUI, takePhotoGUI
from guis.calibrateGUI import calibrateGUI
from guis.instructionsGUI import instructionsGUI
from guis.autoDetectCameraGUI import autoDetectCameraGUI

class progressDialog(basicGUI, QtWidgets.QMainWindow):
    def __init__(self):
        super(progressDialog, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.text = QtWidgets.QLabel('Text Here')
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0,100)
        self.grid.addWidget(self.text)
        self.grid.addWidget(self.progressBar)
        self.setLayout(self.grid)
        
    def _open(self):
        QtWidgets.QApplication.processEvents()
        self.raise_()
        self.show()
        QtWidgets.QApplication.processEvents()
        
    def update(self, value, text = None):
        if text is not None:
            self.text.setText(text)
        self.progressBar.setValue(value)
        
    

class progressThread(QtCore.QThread):
    progress_update = QtCore.Signal(int)
    
    def __init__(self, parent=None):
        super(progressThread, self).__init__(parent)

        
    def __del__(self):
        self.wait()
        
    def run(self):
        while True:
            maxVal = 1
            self.progress_update.emit(maxVal)
            time.sleep(1)

class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        self.dialog = progressDialog()
        
        self.dialog._open()
        #self.checks = checksGUI()
        print('Checks Done')
        self.instructions = instructionsGUI()
        self.dialog.update(10,'New Text')
        print('Instructions Done')
        #self.auto_detect_camera = autoDetectCameraGUI()
        print('autoDetect Done')
        self.live_view = liveViewGUI()
        print('liveView Done')
        self.plots = plotsGUI()
        print('contrast Done')
        self.takePhoto = takePhotoGUI()
        print('imageView Done')
        self.config = configGUI()#openConfigGUI()
        print('Config Done')
        #self.calibrate = calibrateGUI()
        print('Calibrate Loaded')
        self.initUI()
        
        
    def initUI(self):        
        self.setWindowTitle('Upload Image to Database')  
        
        self.setWindowIcon(QtGui.QIcon('icon.png')) 
  
        self.grid.addWidget(self.instructions, 0, 0)
        #self.grid.addWidget(self.image_view, 3, 0)
        #self.grid.addWidget(self.calibrate, 0, 0, 1, 1)
        #self.grid.addWidget(self.config, 1, 0, 2, 1)
        #self.grid.addWidget(self.plots, 3, 0, 5, 1)
        #self.grid.addWidget(self.live_view, 0, 1, 8, 1)
        #self.grid.addWidget(self.takePhoto, 8, 1, 1, 1)
        
        self.setLayout(self.grid)
        self.show()
        self.dialog.close()

        

if __name__ == '__main__':
    global captureThread
    captureThread.init()

    QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_()) 