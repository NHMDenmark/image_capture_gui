#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:40:17 2018

@author: robertahunt
"""
import os
import cv2

from pyzbar import pyzbar
from PyQt5 import QtWidgets, QtCore, QtGui
from basicGUI import basicGUI, ClickableIMG
from settings.local_settings import LOCAL_IMAGE_STORAGE_PATH

class liveViewGUI(basicGUI):
    def __init__(self):
        super(liveViewGUI, self).__init__()
        
        self.preview_path = os.path.join(LOCAL_IMAGE_STORAGE_PATH,'thumb_preview.jpg')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePreview)
        self.timer.start(500)
        self.initUI()
        
    def initUI(self):
        #self.title = self.headerLabel('Camera Preview:')
        self.preview = ClickableIMG(self)
        self.preview.setMinimumSize(1024,680)
        #self.preview.clicked.connect(self.openIMG)
        
        self.QRCode = QtWidgets.QLabel()
        
        #self.grid.addWidget(self.title, 0, 0, 1, 2)
        self.grid.addWidget(self.QRCode, 0, 0, 1, 2)
        self.grid.addWidget(self.preview, 3, 0, 1, 2)
        
        self.setLayout(self.grid)
        
    def openIMG(self):
        self.commandLine(['open',self.preview_path])
    
    def updatePreview(self):
        try:
            preview_img = QtGui.QPixmap(self.preview_path).scaled(1024,680, 
                                                           QtCore.Qt.KeepAspectRatio)
            QRCode_text = self.getQRCode(self.preview_path)
            
            self.preview.setPixmap(preview_img)
            self.QRCode.setText('QR Code / Catalog Number:' + QRCode_text)
        except Exception as ex:
            pass
            #self.warn('Error reading' + self.preview_path + 'file. \n%s'%ex)
    
    def getQRCode(self, img_path):
        decoded_list = pyzbar.decode(cv2.imread(img_path))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            return 'XXXXXX'
        