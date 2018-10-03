#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:43:32 2018

@author: robertahunt
"""
import os
import cv2
import time
import Queue
import rawpy
import serial
import pysftp
import paramiko
import threading
import numpy as np
import pandas as pd


from pyzbar import pyzbar
from base64 import b64decode
from functools import partial
from PyQt5 import QtWidgets, QtCore, QtGui
from basicGUI import basicGUI, ClickableIMG, Arduino
from settings.local_settings import (SFTP_PUBLIC_KEY, ERDA_USERNAME, 
                                     ERDA_SFTP_PASSWORD, ERDA_HOST,
                                     ERDA_PORT, ERDA_FOLDER, DUMP_FOLDER, CACHE_FOLDER)
from guis.progressDialog import progressDialog


global start_time

def start_timer():
    global start_time
    start_time = pd.Timestamp.now()

def tick(msg = ''):
    global start_time
    print(msg + ', Time Taken: %s'%(pd.Timestamp.now()-start_time))
    

class takePhotosGUI(basicGUI):
    def __init__(self):
        super(takePhotosGUI, self).__init__()
        
        self.arduino = Arduino()
        self.PREVIEW_WIDTH = 1024//2
        self.PREVIEW_HEIGHT = 680//2
        
        self.newImgName = ''
        self.imgSuffix = '0'
        
        self.previewPath = os.path.join(DUMP_FOLDER,'thumb_preview.jpg')
        self.initUI()
        
    
    def initUI(self):
        self.moveCameraUpMm = QtWidgets.QPushButton('Up 0.1 cm')
        self.moveCameraUpCm = QtWidgets.QPushButton('Up 1 cm')
        self.moveCameraDownMm = QtWidgets.QPushButton('Down 0.1 cm')
        self.moveCameraDownCm = QtWidgets.QPushButton('Down 1 cm')
        
        self.moveCameraUpMm.clicked.connect(self.arduino.cameraUpMm)
        self.moveCameraUpCm.clicked.connect(self.arduino.cameraUpCm)
        self.moveCameraDownMm.clicked.connect(self.arduino.cameraDownMm)
        self.moveCameraDownCm.clicked.connect(self.arduino.cameraDownCm)
        
        self.takePhotoButton = QtWidgets.QPushButton('Take New Photo')
        self.takePhotoButton.clicked.connect(self.takeSinglePhoto)
        
        self.takeStackedPhotoButton = QtWidgets.QPushButton('Take New Stacked Photo')
        self.takeStackedPhotoButton.clicked.connect(self.takeStackedPhotos)
        
        self.grid.addWidget(self.moveCameraUpMm, 0, 0)
        self.grid.addWidget(self.moveCameraDownMm, 0, 1)
        self.grid.addWidget(self.moveCameraUpCm, 1, 0)
        self.grid.addWidget(self.moveCameraDownCm, 1, 1)
        self.grid.addWidget(self.takePhotoButton, 2, 0, 1, 2)
        self.grid.addWidget(self.takeStackedPhotoButton, 3, 0, 1, 2)
        
        self.setLayout(self.grid)
    
    def readQRCode(self, imgPath):
        _format = imgPath.split('.')[-1]
        if _format == 'arw':
            with rawpy.imread(imgPath) as raw:
                img =  raw.postprocess()
        elif _format == 'jpg':
            img = cv2.imread(imgPath)
        else:
            self.warn('Image format at %s not understood. Got %s, should be arw or jpg.'%(imgPath,_format))
    
        decoded_list = pyzbar.decode(cv2.resize(img,(1024,680)))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            return ''
        
    def takePhoto(self, imgName):   
        os.chdir(DUMP_FOLDER)

        self.commandLine(['gphoto2', '--capture-image-and-download',
                          '--force-overwrite', '--filename', imgName])
        
    def takeSinglePhoto(self):
        progress = progressDialog('Taking Single Photo')
        progress._open()
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
        imgName = 'singlePhoto.arw'
        
        progress.update(20, 'Taking Single Photo..')
        self.takePhoto(imgName)
        
        dumpPath = os.path.join(DUMP_FOLDER, imgName)
        QRCode = self.readQRCode(self.previewPath)
        QRCode = self.checkQRCode(QRCode)
        
        if len(QRCode):
            newImgName = 'NHMD-' + QRCode + '_' + timestamp + '.arw'
            progress.update(90, 'Copying file to cache as %s '%newImgName)
            cachePath = os.path.join(CACHE_FOLDER, newImgName)
            
            self.commandLine(['cp',dumpPath,cachePath])
            self.warn('Done Taking Photo')
        progress._close()

    def checkQRCode(self, QRCode):
        try:
            _len = len(str(int(QRCode)))
        except:
            _len = 0
        
        if _len == 6:
            return str(QRCode)
            
        else:
            QRCode, okPressed = QtWidgets.QInputDialog.getInt(self, "QR Code not found","QR Code not found in image, please manually input 6-digit Catalog Number:")
            if okPressed:
                try:
                    _len = len(str(int(QRCode)))
                    if _len == 6:
                        return str(QRCode)
                except:
                    pass
                return self.checkQRCode(QRCode)
            else:
                self.warn('No Photo Taken')
                return ''
            
    def takeStackedPhotos(self):
        n_photos = 6
        progress = progressDialog('Taking %s Stacked Photos'%n_photos)
        progress._open()
        
        
        progress.update(5,'Checking QR Code..')
        QRCode = self.readQRCode(self.previewPath)
        QRCode = self.checkQRCode(QRCode)
        
        if len(QRCode):    
            timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
        
            for i in range(0,n_photos):
                progress.update(80*i/n_photos, 'Taking Photo %s of %s'%(i+1,n_photos))
                start_timer()
                tempName = 'Stacked_'+str(i)+'.arw'
                self.takePhoto(imgName=tempName)
                time.sleep(0.1)
                self.arduino.moveCamera('d','0.2')
                time.sleep(1)
                
                newImgName = 'NHMD-' + QRCode + '_' + timestamp + '_Stacked_' + str(i) + '.arw'
                progress.update(80*i/n_photos + 5)
                
                dumpPath = os.path.join(DUMP_FOLDER, tempName)
                cachePath = os.path.join(CACHE_FOLDER, newImgName)
            
                self.commandLine(['cp',dumpPath,cachePath]) 
                
            progress.update(99, 'Moving Camera Back Into Place')

            self.arduino.moveCamera('u',str(n_photos*0.2))
            self.warn('Done Taking Photos')

        progress._close()
    
