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
#from guis.plotsGUI import plotsGUI
from guis.basicGUI import basicGUI
from guis.checksGUI import checksGUI
#from guis.configGUI import openConfigGUI, configGUI
#from guis.liveViewGUI import liveViewGUI
#from guis.imageViewGUI import imageViewGUI, takePhotoGUI
#from guis.calibrateGUI import calibrateGUI
from guis.progressDialog import progressDialog
from guis.instructionsGUI import instructionsGUI
#from guis.autoDetectCameraGUI import autoDetectCameraGUI



class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        self.progress = progressDialog()
        self.progress._open()

        self.progress.update(20,'Getting Coffee..')
        self.instructions = instructionsGUI()
       
        self.progress.update(30,'Checking Appendages..')
        self.checks = checksGUI()
      
        self.progress.update(50,'Getting Dressed..')
        #self.live_view = liveViewGUI()
        #self.plots = plotsGUI()
        #self.takePhoto = takePhotoGUI()
        #self.config = configGUI()
        #self.calibrate = calibrateGUI()
        self.progress.update(100)
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
        self.progress.close()

        

if __name__ == '__main__':
    global captureThread
    captureThread.init()

    QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_()) 