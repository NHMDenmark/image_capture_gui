# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:59:05 2018

@author: ngw861
"""
import os
import sys
import cv2
import time
import pprint
import numpy as np

from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT)

from guis import captureThread
from guis.basicGUI import basicGUI
from guis.checksGUI import checksGUI
from guis.configGUI import openConfigGUI
from guis.liveViewGUI import liveViewGUI
from guis.imageViewGUI import imageViewGUI
from guis.instructionsGUI import instructionsGUI
from guis.autoDetectCameraGUI import autoDetectCameraGUI


class histogramGUI(basicGUI):
    def __init__(self):
        super(histogramGUI, self).__init__()
        
        self.width = 400
        self.height = 150
        self.path = 'capture_preview.jpg'

        self.initUI()
        
    def initUI(self):
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        dynamic_canvas.setMinimumSize(self.width, self.height)

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(
            1000, [(self._update_canvas, (), {})])
        self._timer.start()

        self.grid.addWidget(dynamic_canvas)
        self.setLayout(self.grid)
   
    def _update_canvas(self):
        self._dynamic_ax.clear()
        try:
            self.img = cv2.imread(self.path, 0)
        except:
            pass
        self._dynamic_ax.hist(self.img.ravel(), 256, [0,256])
        self._dynamic_ax.set_title('Histogram')
        self._dynamic_ax.figure.canvas.draw()
        
class contrastGUI(basicGUI):
    def __init__(self):
        super(contrastGUI, self).__init__()
        
        self.width = 400
        self.height = 150
        self.path = 'capture_preview.jpg'
        self.n_history = 100
        self.history = np.zeros(self.n_history)
        self.x_axis = np.linspace(1,self.n_history,self.n_history)

        self.initUI()
        
    def initUI(self):
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        dynamic_canvas.setMinimumSize(self.width, self.height)

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(
            1000, [(self._update_canvas, (), {})])
        self._timer.start()

        self.grid.addWidget(dynamic_canvas)
        self.setLayout(self.grid)
        
   
    def _update_canvas(self):
        self._dynamic_ax.clear()
        
        try:
            self.img = cv2.imread(self.path)
        except:
            pass
        contrast = cv2.Laplacian(self.img, cv2.CV_64F).var()
        
        self.history = np.roll(self.history, -1)
        self.history[-1] = contrast
        
        self._dynamic_ax.plot(self.x_axis, self.history)
        self._dynamic_ax.set_title('Contrast')
        self._dynamic_ax.figure.canvas.draw()



class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        #self.checks = checksGUI()
        print('Checks Done')
        self.instructions = instructionsGUI()
        print('Instructions Done')
        #self.auto_detect_camera = autoDetectCameraGUI()
        print('autoDetect Done')
        self.live_view = liveViewGUI()
        print('liveView Done')
        self.histogram = histogramGUI()
        print('histogram Done')
        self.contrast = contrastGUI()
        print('contrast Done')
        self.image_view = imageViewGUI()
        print('imageView Done')
        self.config = openConfigGUI()
        print('Config Done')
        self.initUI()
        
        
    def initUI(self):        
        self.setWindowTitle('Upload Image to Database')  
        self.setWindowIcon(QtGui.QIcon('icon.png')) 
        cancelButton = QtWidgets.QPushButton("Cancel")
        self.takePhotoButton = QtWidgets.QPushButton("Take New Photo")
        self.takePhotoButton.clicked.connect(self.image_view.takePhoto)
        
        self.grid.addWidget(self.instructions, 0, 0)
        #self.grid.addWidget(self.auto_detect_camera, 1, 0)
        #self.grid.addWidget(self.checks, 2, 0)
        self.grid.addWidget(self.image_view, 3, 0)
        self.grid.addWidget(self.config, 4, 0)
        self.grid.addWidget(self.live_view, 0, 1, 4, 2)
        self.grid.addWidget(self.takePhotoButton, 4, 1, 1, 2)
        self.grid.addWidget(self.histogram, 5, 1, 1, 1)
        self.grid.addWidget(self.contrast, 5, 2, 1, 1)
        #self.grid.addWidget(cancelButton, 6, 1)
        self.setLayout(self.grid)
        
        self.show()
        

if __name__ == '__main__':
    global captureThread
    captureThread.init()

    QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_())