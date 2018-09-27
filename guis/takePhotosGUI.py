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
from PyQt5 import QtWidgets, QtCore, QtGui
from basicGUI import basicGUI, ClickableIMG
from settings.local_settings import (SFTP_PUBLIC_KEY, ERDA_USERNAME, 
                                     ERDA_SFTP_PASSWORD, ERDA_HOST,
                                     ERDA_PORT, ERDA_FOLDER, DUMP_FOLDER, CACHE_FOLDER,
                                     ARDUINO_PORT)

global start_time

def start_timer():
    global start_time
    start_time = pd.Timestamp.now()

def tick(msg = ''):
    global start_time
    print(msg + ', Time Taken: %s'%(pd.Timestamp.now()-start_time))
    

class takePhotosGUI(basicGUI):
    def __init__(self):
        super(imageViewGUI, self).__init__()
        
        self.board = serial.Serial(ARDUINO_PORT, 9600)
        self.PREVIEW_WIDTH = 1024//2
        self.PREVIEW_HEIGHT = 680//2
        
        self.newImgName = ''
        self.imgSuffix = '0'
        self.initUI()
        
    
    def initUI(self):
        self.moveCameraUpMm = QtWidgets.QPushButton('Up 0.1 cm')
        self.moveCameraUpCm = QtWidgets.QPushButton('Up 1 cm')
        self.moveCameraDownMm = QtWidgets.QPushButton('Down 0.1 cm')
        self.moveCameraDownCm = QtWidgets.QPushButton('Down 1 cm')
        
        self.moveCameraUpMm.clicked.connect(self.cameraUpMm)
        self.moveCameraUpCm.clicked.connect(self.cameraUpCm)
        self.moveCameraDownMm.clicked.connect(self.cameraDownMm)
        self.moveCameraDownCm.clicked.connect(self.cameraDownCm)
        
        self.takePhotoButton = QtWidgets.QPushButton('Take New Photo')
        self.takePhotoButton.clicked.connect(self.takePhoto)
        self.takePhotoButton.clicked.connect(self.displayLatestImg)
        
        self.takeStackedPhotoButton = QtWidgets.QPushButton('Take New Stacked Photo')
        self.takeStackedPhotoButton.clicked.connect(self.takeStackedPhotos)
        
        self.grid.addWidget(self.moveCameraUpMm, 0, 0)
        self.grid.addWidget(self.moveCameraDownMm, 0, 1)
        self.grid.addWidget(self.moveCameraUpCm, 1, 0)
        self.grid.addWidget(self.moveCameraDownCm, 1, 1)
        self.grid.addWidget(self.takePhotoButton, 2, 0, 1, 2)
        self.grid.addWidget(self.takeStackedPhotoButton, 3, 0, 1, 2)
        
        self.setLayout(self.grid)
        
        
    def sendToERDA(self, tempPath, newImgName):
        if len(str(int(self.QRCode))) != 6:
            try:
                if len(str(int(self.QRCodeManualEdit.text()))) == 6:
                    self.QRCode = len(str(int(self.QRCodeManualEdit.text())))
                else:
                    self.warn('QR Code not recognized in image, and manual catalog number entry invalid')
                    return None
            except:
                self.warn('QR Code not recognized in image, and manual catalog number entry invalid')
        
        key = paramiko.RSAKey(data=b64decode(SFTP_PUBLIC_KEY))
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys.add(ERDA_HOST, 'ssh-rsa', key)
        
        sftp = pysftp.Connection(host=ERDA_HOST, username=ERDA_USERNAME, 
                                 password=ERDA_SFTP_PASSWORD, cnopts=cnopts)

        remote_path = os.path.join(ERDA_FOLDER, newImgName)
        sftp.put(tempPath,remote_path)
        sftp.close()
        
        #        
#        print('Sending to ERDA')
#        if len(QRCode):
#            for i in range(n_photos):
#                start_timer()
#                print('Photo %s'%i)
#                tempRawPath = os.path.join(self.TEMP_FOLDER, 'Stacked_'+str(i)+'.arw')
#                tempTiffPath = os.path.join(self.TEMP_FOLDER, 'Stacked_'+str(i)+'.tiff')
#                
#                rawImgName = 'NHMD' + QRCode + '_' + timestamp + '_' + str(i) + '.arw'
#                tiffImgName = 'NHMD' + QRCode + '_' + timestamp + '_' + str(i) + '.tiff'
#                
#                self.sendToERDA(tempRawPath, rawImgName)
#                tick('Done sending one arw to ERDA')
#                self.sendToERDA(tempTiffPath, tiffImgName)
#                tick('Done sending one tiff to ERDA')
        
    def sendToLocalDir(self):
        #        print('Copying to Local Storage')
#        if len(QRCode):
#            for i in range(n_photos):
#                start_timer()
#                tempRawPath = os.path.join(self.TEMP_FOLDER, 'Stacked_'+str(i)+'.arw')
#                tempTiffPath = os.path.join(self.TEMP_FOLDER, 'Stacked_'+str(i)+'.tiff')
#                
#                rawImgName = 'NHMD' + QRCode + '_' + timestamp + '_' + str(i) + '.arw'
#                tiffImgName = 'NHMD' + QRCode + '_' + timestamp + '_' + str(i) + '.tiff'
#                
#                rawImgPath = os.path.join(LOCAL_IMAGE_STORAGE_PATH, rawImgName)
#                tiffImgPath = os.path.join(LOCAL_IMAGE_STORAGE_PATH, tiffImgName)
#                
#                self.commandLine(['cp',tempRawPath,rawImgPath])
#                tick('Done copying one arw locally')
#                start_timer()
#                self.commandLine(['cp',tempTiffPath,tiffImgPath])
#                tick('Done copying one tiff locally')

        #start_timer()
        #self.tempPath, self.tempName = self.getLatestImageName(self.TEMP_FOLDER)
        #name, fileformat = self.tempName.split('.')
        #if len(name):
        #    new_name = os.path.join(TEMP_IMAGE_CACHE_PATH, name + '.tiff')
        #    self.commandLine(['sips', '-s','format','tiff',self.tempPath, '--out',new_name])
        #tick('Done Converting Photo to tiff')
        pass
    
    def readQRCode(self, imgPath):
        _format = imgPath.split('.')[-1]
        if _format == 'arw':
            with rawpy.imread(path) as raw:
                img =  raw.postprocess()
        else:
            self.warn('Image format at %s not understood. Got %s, should be arw.'%(path,_format))
    
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
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
        imgName = 'singlePhoto.arw'
        
        self.takePhoto(imgName)
        dumpPath = os.path.join(DUMP_FOLDER, imgName)
        QRCode = self.readQRCode(dumpPath)
        QRCode = self.checkQRCode(QRCode)
        
        newImgName = 'NHMD' + QRCode + '_' + timestamp + '.arw'
        cachePath = os.path.join(CACHE_FOLDER, newImgName)
        
        self.commandLine(['cp',dumpPath,cachePath])

    def checkQRCode(self, QRCode):
        try:
            _len = len(str(int(QRCode)))
        except:
            _len = 0
        if _len != 6:
            QRCode, okPressed = QtWidgets.QInputDialog.getInt(self, "QR Code not found","QR Code not found in image, please manually input 6-digit Catalog Number:")
            if okPressed:
                try:
                    _len = len(str(int(QRCode)))
                    if _len == 6:
                        return QRCode
                    else:
                        self.checkQRCode(QRCode)
            
       
        
    def takeStackedPhotos(self):
        n_photos = 6
        QRCode = ''
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
        
        print('Taking pics')
        for i in range(n_photos):
            start_timer()
            tempName = 'Stacked_'+str(i)+'.arw'
            self.takePhoto(imgName=tempName)
            time.sleep(0.1)
            self.moveCamera('d','0.2')
            tempPath = os.path.join(DUMP_FOLDER, tempName)
           
            _QRCode = self.readQRCode(tempPath)
            try:
                _len = len(str(int(_QRCode)))
            except:
                _len = 0
            if _len == 6:
                QRCode = _QRCode
            print(QRCode)
            
            QRCode = self.checkQRCode(QRCode)
            tick('Done taking one photo for stack')
#               
        print('Moving camera back to place')
        #Move camera back to place
        start_timer()
        self.moveCamera('u',str(n_photos*0.2))
        tick('Done Moving Camera Back') 
    
    def moveCamera(self, direction, cm):
        assert direction in ['u','d']
        while True:
            if (self.board.inWaiting()>0):  # Check if board available
                self.board.write("%s %s\n"%(direction,cm))
                break 
    
    def cameraUpMm(self):
        self.moveCamera('u','0.1')
    def cameraUpCm(self):
        self.moveCamera('u','1')
    def cameraDownMm(self):
        self.moveCamera('d','0.1')
    def cameraDownCm(self):
        self.moveCamera('d','1')
   