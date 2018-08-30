# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:59:05 2018

@author: ngw861
"""
import os
import cv2
import sys
import warnings
import subprocess
import threading

from time import sleep
from PyQt5 import QtGui, QtCore, QtWidgets
from pyzbar import pyzbar
from apscheduler.schedulers.background import BackgroundScheduler
import logging
logging.basicConfig()

instructions = '''
1. Make sure camera is on, usb cable is connected, 
and camera is set to auto-focus.

If you have any questions, 
shoot roberta a mail: ngw861@alumni.ku.dk. 
If it is urgent, call her: 91 93 20 26
'''

class basicGUI(QtWidgets.QWidget):
    
    def __init__(self):
        super(basicGUI, self).__init__()
        self.timer = QtCore.QTimer()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

    def commandLine(self, args):
        assert isinstance(args,list)
        try:
            output = subprocess.check_output(args)
            return output
        except Exception as ex:
            self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))
        
    def warn(self, msg):
        warnings.warn(msg)
        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle('Warning Encountered')
        warning.setText(msg)
        warning.exec_()
        
    #def closeEvent(self, event):
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        #    event.accept()
        #else:
        #    event.ignore() 
        #event.accept()
    
class otherGUI(basicGUI):
    def __init__(self):
        super(otherGUI, self).__init__()
        test = QtWidgets.QLabel('BlahBlahBlah')
        self.grid.addWidget(test)
        self.setLayout(self.grid)
        

class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        self.initUI()
        
    def initUI(self):
        test = QtWidgets.QLabel('Instructions')
        self.grid.addWidget(test)
        blah = otherGUI()
        self.grid.addWidget(blah)
        self.setLayout(self.grid)
        self.show()

class Example(QtWidgets.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.IMG_HEIGHT = 700
        self.IMG_WIDTH = 700
        self.IMG_QUALITY = 2
        assert (self.IMG_QUALITY >= 0) & (self.IMG_QUALITY <= 7)
        self.IMG_SUFFIX = 'jpg' if self.IMG_QUALITY <= 2 else 'arw'
        self.IMG_FOLDER = 'images'
        self.IMG_FILEFOLDER = self.getLatestImageName(self.IMG_FOLDER)
        
        self.setImgQuality(self.IMG_QUALITY)
        self.timer = QtCore.QTimer()
        self.initUI()
        self.configOptions = self.getConfigOptions()

        
    def initUI(self):
        inst_title = QtWidgets.QLabel('Instructions')
        inst_desc = QtWidgets.QLabel(instructions)
       
        auto_detect_output = self.autoDetectCamera()
        auto_detect = QtWidgets.QLabel(auto_detect_output)
        
        qr_code_output = self.getQRCode()
        qr_code = QtWidgets.QLabel('QR Code: %s'%qr_code_output)
        img_title = QtWidgets.QLabel('Latest image in folder: %s'%os.path.join(os.getcwd(),self.IMG_FOLDER))
        
        takePhotoButton = QtWidgets.QPushButton("Take Photo")
        takePhotoButton.clicked.connect(self.takePhoto)
        okButton = QtWidgets.QPushButton("Save and Send to Database")
        cancelButton = QtWidgets.QPushButton("Cancel")

        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(inst_title, 1, 0, 1, 1)
        self.grid.addWidget(inst_desc, 2, 0, 2, 1)
        self.grid.addWidget(auto_detect, 3, 0, 3, 1)
        self.grid.addWidget(takePhotoButton, 5, 0, 5, 1)
        self.grid.addWidget(qr_code, 4, 0, 4, 1)
        self.grid.addWidget(img_title, 1, 2)
        
        self.grid.addWidget(okButton, 12, 1)
        self.grid.addWidget(cancelButton, 12, 2)
        
        self.setLayout(self.grid) 
        
        self.setWindowTitle('Upload Image to Database')    
        self.setWindowIcon(QtGui.QIcon('icon.png')) 
        self.show()
        self.updatePreview()
        self.displayLatestImg()
        self.timer.timeout.connect(self.updatePreview)
        self.timer.start(500)
        
    def getConfigOptions(self):
        raw_config = self.commandLine(['gphoto2','--list-all-config'])
        config = {}
        for line in raw_config.split('\n'):
            if 'other' in line:
                break
            
            if line.startswith('/'):
                name = line
                config[name] = {}
                config[name]['Choices'] = []
            elif line.startswith('Label:'):
                config[name]['Label'] = line[6:]
            elif line.startswith('Readonly:'):
                config[name]['Readonly'] = line[10:]
            elif line.startswith('Type:'):
                config[name]['Type'] = line[6:]
            elif line.startswith('Current:'):
                config[name]['Current'] = line[7:]
            elif line.startswith('Choice:'):
                choice = line[7:]#.split(' ')
                config[name]['Choices'] += [choice]
                #config[name]['Choices'][choice[0]] = ' '.join(choice[1:])
            elif line.startswith('Bottom:'):
                config[name]['Bottom'] = line[8:]
            elif line.startswith('Top:'):
                config[name]['Top'] = line[4:]
            elif line.startswith('Step:'):
                config[name]['Step'] = line[4:]
        
        row = 13
        for option in config.keys():
            if config[option]['Type'] in ['MENU','RADIO']:
                widget = QtWidgets.QLabel(config[option]['Label'])
                widgetEdit = QtWidgets.QComboBox()
                widgetEdit.addItems(config[option]['Choices'])
                widgetEdit.currentIndexChanged.connect(lambda x: self.updateConfigIndex(config, choice))
                self.grid.addWidget(widget, row, 0)
                self.grid.addWidget(widgetEdit, row, 1)
                row += 1
        self.setLayout(self.grid)
        self.show()
        return config

    def updateConfigIndex(self, config, choice):
        print(config, choice)
        
        
    def displayLatestImg(self):
        self.IMG_FILEFOLDER = self.getLatestImageName(self.IMG_FOLDER)
        first = 0
        if 'img' in self.__dict__:
            self.grid.removeWidget(self.img)
        self.img = QtWidgets.QLabel(self)
        img_resized = QtGui.QPixmap(self.IMG_FILEFOLDER).scaled(self.IMG_WIDTH, 
                                                       self.IMG_HEIGHT, 
                                                       QtCore.Qt.KeepAspectRatio)
        self.img.setPixmap(img_resized)
        self.img.setMinimumSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        self.img.setStyleSheet("border: 1px solid black")
        self.grid.addWidget(self.img, 2, 2, 10, 2)
        self.setLayout(self.grid)
        self.show()
        
    def updatePreview(self):
        self.commandLine(['gphoto2','--capture-preview','--force-overwrite'])
        if 'preview' in self.__dict__:
            self.grid.removeWidget(self.preview)
        self.preview = QtWidgets.QLabel(self)
        preview_resized = QtGui.QPixmap('capture_preview.jpg').scaled(300, 
                                                       300, 
                                                       QtCore.Qt.KeepAspectRatio)
        self.preview.setPixmap(preview_resized)
        self.preview.setMinimumSize(300, 300)
        self.grid.addWidget(self.preview, 6, 0, 6, 1)
        self.setLayout(self.grid)
        self.show()
        self.preview.update()
        self.preview.repaint()
        
    def autoDetectCamera(self):
        auto_detect_output = 'Cameras Detected: \n%s'%self.commandLine(['gphoto2','--auto-detect'])
        if len(auto_detect_output) <= 126:
            warning = 'Error xkcd1314: No cameras detected'
            self.warn(warning)
            return auto_detect_output + warning
        return auto_detect_output

    def setImgQuality(self, ImgQuality):
        self.commandLine(['gphoto2', '--set-config-index',
                            '/main/capturesettings/imagequality=%s'%ImgQuality])
    
    def takePhoto(self):
        self.commandLine(['gphoto2', '--capture-image-and-download',
                           '--filename', 'images/%y%m%d%H%M%S.jpg'])
        self.displayLatestImg()

    def getLatestImageName(self, image_folder):
        images = [image for image in os.listdir(image_folder) if image.split('.')[1] in ['jpg','arw']]
        latest_image = max([os.path.join(image_folder, image) for image in images], key=os.path.getctime)
        return latest_image

    def getQRCode(self):
        decoded_list = pyzbar.decode(cv2.imread(self.IMG_FILEFOLDER))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            self.warn('Error xkcd1237: Qr code not found in image!')
            return ''

    def commandLine(self, args):
        assert isinstance(args,list)
        try:
            output = subprocess.check_output(args)
            return output
        except Exception as ex:
            self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))

    def closeEvent(self, event):
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        #    event.accept()
        #else:
        #    event.ignore() 
        event.accept()
        
    def warn(self, msg):
        warnings.warn(msg)
        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle('Warning Encountered')
        warning.setText(msg)
        warning.exec_()
        

if __name__ == '__main__':
    QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_())