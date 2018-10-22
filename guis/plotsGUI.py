#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 09:18:50 2018

@author: robertahunt
"""
import os
import gc
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtCore
from matplotlib.figure import Figure
#from matplotlib.backends.qt_compat import QtCore#, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import FigureCanvas

from guis.settings.local_settings import DUMP_FOLDER


from guis.basicGUI import basicGUI

class plotsGUI(basicGUI):
    def __init__(self):
        super(plotsGUI, self).__init__()
        
        self.width = 400
        self.height = 150
        self.path = os.path.join(DUMP_FOLDER, 'thumb_preview.jpg')
        self.n_contrast_history = 100
        self.contrast_history = np.zeros(self.n_contrast_history)
        self.contrast_x_axis = np.linspace(1,self.n_contrast_history,
                                           self.n_contrast_history)
        
        self._img_timer = QtCore.QTimer()
        self._img_timer.timeout.connect(self._update_img)
        self._img_timer.start(500)
        
        self.hist_timer = QtCore.QTimer()
        self.hist_timer.timeout.connect(self._update_hist)
        self.hist_timer.start(600)

        self.initUI()
        
    def initUI(self):
        self.hist_fig = Figure(figsize=(5,3))
        #self.hist_fig, self.hist_ax = plt.subplots(figsize=(5,3))
        self.hist_canvas = FigureCanvas(self.hist_fig)
        self.hist_canvas.setMinimumSize(self.width, self.height)
        self.hist_ax = self.hist_canvas.figure.subplots()
        #contrast_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        
        #contrast_canvas.setMinimumSize(self.width, self.height)
        
        #self.histTimer = hist_canvas.new_timer(
        #    500, [(self._update_hist, (), {})])
        #self.histTimer.start()
        
        #self._contrast_ax = contrast_canvas.figure.subplots()
        #self.contrastTimer = contrast_canvas.new_timer(
        #    500, [(self._update_contrast, (), {})])
        #self.contrastTimer.start()

        #self.grid.addWidget(contrast_canvas, 1, 0)
        self.grid.addWidget(self.hist_canvas, 0, 0)
        self.setLayout(self.grid)
   
    def _update_img(self):
        try:
            self.img = cv2.imread(self.path)
        except:
            pass
    
    def _update_hist(self):
        try:
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY).ravel()
            
            #self.rmhist()
            self.hist_ax.clear()
            #self.hist_ax.figure.canvas.clear()
            #self.hist_ax = self.hist_canvas.figure.subplots()
            
            self.hist_ax.hist(gray, 256, [0,256])
            self.hist_ax.set_title('Histogram')
            self.hist_ax.figure.canvas.draw()     
        except:
            pass
   
    def _update_contrast(self):
        try:
            self._contrast_ax.clear()
            
            contrast = cv2.Laplacian(self.img, cv2.CV_64F).var()
            
            self.contrast_history = np.append(self.contrast_history[1:], [contrast])
            
            self._contrast_ax.plot(self.contrast_x_axis, self.contrast_history)
            self._contrast_ax.set_title('Contrast')
            self._contrast_ax.figure.canvas.draw()
        except:
            pass
        
    def rmhist(self):
        self._hist_ax.close()
        self._hist_ax.deleteLater()
        gc.collect()
        