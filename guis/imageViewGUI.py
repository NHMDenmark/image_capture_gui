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
                                     ERDA_PORT, ERDA_FOLDER, TEMP_IMAGE_CACHE_PATH,
                                     LOCAL_IMAGE_STORAGE_PATH, ARDUINO_PORT)

global start_time

def start_timer():
    global start_time
    start_time = pd.Timestamp.now()

def tick(msg = ''):
    global start_time
    print(msg + ', Time Taken: %s'%(pd.Timestamp.now()-start_time))

class imageViewGUI(basicGUI, QtWidgets.QMainWindow):
    def __init__(self):
        super(imageViewGUI, self).__init__()
        self.board = serial.Serial(ARDUINO_PORT, 9600)
        self.PREVIEW_WIDTH = 1024//2
        self.PREVIEW_HEIGHT = 680//2
        
        self.TEMP_FOLDER = TEMP_IMAGE_CACHE_PATH
        self.tempPath, self.tempName = self.getLatestImageName(self.TEMP_FOLDER)
        self.newImgName = ''
        self.imgSuffix = '0'
        self.initUI()
        
    
    def initUI(self):
        self.imgView = ClickableIMG(self)
        self.imgView.setMinimumSize(self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT)
        self.imgView.clicked.connect(self.openIMG)
        
        header = self.headerLabel('Latest image')
        self.imgDesc = QtWidgets.QLabel('Latest image in folder: %s'% self.tempPath)
        self.newImgNameLabel = QtWidgets.QLabel('New image name: %s'% self.newImgName)
        sendButton = QtWidgets.QPushButton("Send to Datastorage")
        sendButton.clicked.connect(self.sendToERDA)
        sendButton.clicked.connect(self.sendToLocalDir)
        
        self.QRCodeLabel = QtWidgets.QLabel()
        
        label = 'Manual Catalog Number Entry (used only if QR Code not found): '
        QRCodeManualLabel = QtWidgets.QLabel(label)
        self.QRCodeManualEdit = QtWidgets.QLineEdit()
        
        self.grid.addWidget(header, 0, 0, 1, 2)
        self.grid.addWidget(self.imgDesc, 1, 0, 1, 2)
        self.grid.addWidget(self.QRCodeLabel, 2, 0, 1, 2)
        self.grid.addWidget(QRCodeManualLabel, 3, 0, 1, 1)
        self.grid.addWidget(self.QRCodeManualEdit, 3, 1, 1, 1)
        self.grid.addWidget(self.imgView, 4, 0, 1, 2)
        self.grid.addWidget(self.newImgNameLabel, 5, 0, 1, 2)
        self.grid.addWidget(sendButton, 6, 0, 1, 2)
        self.setLayout(self.grid)
        
    def getIMG(self):
        _format = self.tempPath.split('.')[-1]
        #if _format == 'jpg':
        #    return cv2.imread(self.tempPath)
        if _format == 'arw':
            with rawpy.imread(self.tempPath) as raw:
                return raw.postprocess()
        else:
            self.warn('Image format in folder not understood.%s'%_format)
        
    def sendToERDA(self, tempPath=None, imgName=None):  
        if not len(tempPath):
            tempPath = self.tempPath
        if not len(imgName):
            imgName = self.newImgName
    
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

        remote_path = os.path.join(ERDA_FOLDER, imgName)
        sftp.put(tempPath,remote_path)
        sftp.close()
        self.close()
        
    def sendToLocalDir(self):
        pass
        
    
    def getQRCode(self):

        decoded_list = pyzbar.decode(cv2.resize(self.img,(1024,680)))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            return ''
        
    def openIMG(self):
        self.commandLine(['open', self.tempPath])
        
    def getLatestImageName(self, image_folder):
        images = [image for image in os.listdir(image_folder) if image.split('.')[-1] in ['arw']]
        if len(images):
            latest_image_path = max([os.path.join(image_folder, image) for image in images], key=os.path.getctime)
            return latest_image_path, latest_image_path.split('/')[-1]
        else:
            return '', ''
    
    def displayLatestImg(self):
        self.tempPath, self.tempName = self.getLatestImageName(self.TEMP_FOLDER)
        self.imgDesc.setText('Latest image in folder: %s'% self.tempPath)
        self.img = self.getIMG()
        
        _format = self.tempPath.split('.')[-1]
        #if _format == 'arw':
        imgResized = QtGui.QImage(self.img.data, self.img.shape[1], self.img.shape[0],
                               self.img.shape[1]*3, QtGui.QImage.Format_RGB888)
        imgResized = QtGui.QPixmap.fromImage(imgResized).scaled(self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT, 
                                                   QtCore.Qt.KeepAspectRatio)
        #elif _format == 'jpg':
        #    imgResized = QtGui.QPixmap(self.tempPath).scaled(self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT, 
        #                                               QtCore.Qt.KeepAspectRatio)
        self.imgView.setPixmap(imgResized)
        
        self.QRCode = str(self.getQRCode())
        self.QRCodeLabel.setText('QR Code / Catalog Number: ' + self.QRCode)
        self.newImgName = self.QRCode + '_'  + self.tempName
        self.newImgNameLabel.setText('New image name: %s'% self.newImgName)
        
    def takePhoto(self, imgName=None):   
        start_timer()
        print(imgName)
        if (imgName is None) | (imgName == False):
            imgName = 'capture.arw'
        
        os.chdir(self.TEMP_FOLDER)
        print(imgName)
        self.commandLine(['gphoto2', '--capture-image-and-download',
                          '--force-overwrite', '--filename', imgName])
        tick('Done Taking Photo')
        
        #start_timer()
        #self.tempPath, self.tempName = self.getLatestImageName(self.TEMP_FOLDER)
        #name, fileformat = self.tempName.split('.')
        #if len(name):
        #    new_name = os.path.join(TEMP_IMAGE_CACHE_PATH, name + '.tiff')
        #    self.commandLine(['sips', '-s','format','tiff',self.tempPath, '--out',new_name])
        #tick('Done Converting Photo to tiff')
    
    
        
    def takeStackedPhotos(self):
        n_photos = 10
        QRCode = ''
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
        
        while True:
            if (self.board.inWaiting()>0):  # Check if board available
                #Start taking photos
                print('Taking pics')
                for i in range(n_photos):
                    start_timer()
                    tempImgName = 'Stacked_'+str(i)+'.arw'
                    self.takePhoto(imgName=tempImgName)
                    time.sleep(0.1)
                    self.board.write("d 0.2\n")
                    time.sleep(0.5)
                    
                    self.img = self.getIMG()
                    self.QRCode = self.getQRCode()
                    if len(self.QRCode):
                        QRCode = self.QRCode
                    print(self.QRCode)
                    tick('Done taking one photo for stack')
                break
#                
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
        
        print('Moving camera back to place')
        #Move camera back to place
        start_timer()
        for i in range(n_photos):
            self.moveCamera('u',str(n_photos*0.2))
            time.sleep(0.25)
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
            
class takePhotoGUI(basicGUI):
    def __init__(self):
        super(takePhotoGUI, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.dialog = imageViewGUI()
        self.moveCameraUpMm = QtWidgets.QPushButton('Up 0.1 cm')
        self.moveCameraUpCm = QtWidgets.QPushButton('Up 1 cm')
        self.moveCameraDownMm = QtWidgets.QPushButton('Down 0.1 cm')
        self.moveCameraDownCm = QtWidgets.QPushButton('Down 1 cm')
        
        self.moveCameraUpMm.clicked.connect(self.dialog.cameraUpMm)
        self.moveCameraUpCm.clicked.connect(self.dialog.cameraUpCm)
        self.moveCameraDownMm.clicked.connect(self.dialog.cameraDownMm)
        self.moveCameraDownCm.clicked.connect(self.dialog.cameraDownCm)
        
        self.takePhotoButton = QtWidgets.QPushButton('Take New Photo')
        self.takePhotoButton.clicked.connect(self.dialog.takePhoto)
        self.takePhotoButton.clicked.connect(self.dialog.displayLatestImg)
        self.takePhotoButton.clicked.connect(self._open)
        
        self.takeStackedPhotoButton = QtWidgets.QPushButton('Take New Stacked Photo')
        self.takeStackedPhotoButton.clicked.connect(self.dialog.takeStackedPhotos)
        
        self.grid.addWidget(self.moveCameraUpMm, 0, 0)
        self.grid.addWidget(self.moveCameraDownMm, 0, 1)
        self.grid.addWidget(self.moveCameraUpCm, 1, 0)
        self.grid.addWidget(self.moveCameraDownCm, 1, 1)
        self.grid.addWidget(self.takePhotoButton, 2, 0, 1, 2)
        self.grid.addWidget(self.takeStackedPhotoButton, 3, 0, 1, 2)
        
        self.setLayout(self.grid)
        
    def _open(self):
        self.dialog.raise_()
        self.dialog.show()
        
                