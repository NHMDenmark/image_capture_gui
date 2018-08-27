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
from apscheduler.schedulers.background import BackgroundScheduler

from time import sleep
from PyQt5 import QtGui, QtCore, QtWidgets
from pyzbar import pyzbar


#_fromUtf8 = QtCore.QString.fromUtf8

class Example(QtWidgets.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.IMG_HEIGHT = 700
        self.IMG_WIDTH = 700
        self.IMG_QUALITY = 2
        self.IMG_FOLDER = 'images'
        self.IMG_FILEFOLDER = self.load_latest_image(self.IMG_FOLDER)
        
        self.setImgQuality(self.IMG_QUALITY)
        self.sched = BackgroundScheduler()
        
        self.initUI()
        self.sched.add_job(self.update_preview, 'interval', seconds=1)
        self.sched.start()
        
    def initUI(self):       
        inst_title = QtWidgets.QLabel('Instructions')
        inst_desc = QtWidgets.QLabel('''These are the instructions. 
                                      If you have any questions, 
                                      shoot roberta a mail: ngw861@alumni.ku.dk. 
                                      If it is urgent, call her: 91 93 20 26''')
       
        auto_detect_output = self.auto_detect_camera()
        auto_detect = QtWidgets.QLabel(auto_detect_output)
        
        qr_code_output = self.get_qr_code()
        qr_code = QtWidgets.QLabel('QR Code: %s'%qr_code_output)
        img_title = QtWidgets.QLabel('Latest image in folder: %s'%os.path.join(os.getcwd(),self.IMG_FOLDER))
        

        takePhotoButton = QtWidgets.QPushButton("Take Photo")
        takePhotoButton.clicked.connect(self.take_photo)
        okButton = QtWidgets.QPushButton("Save and Send to Database")
        cancelButton = QtWidgets.QPushButton("Cancel")

        
        

        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(inst_title, 1, 0, 1, 1)
        self.grid.addWidget(inst_desc, 2, 0, 1, 1)
        self.grid.addWidget(auto_detect, 3, 0)
        self.grid.addWidget(takePhotoButton, 5, 0)
        self.grid.addWidget(qr_code, 4, 0)
        self.grid.addWidget(img_title, 1, 1)
        
        self.grid.addWidget(okButton, 12, 0)
        self.grid.addWidget(cancelButton, 12, 1)
        
        self.setLayout(self.grid) 
        
        self.setWindowTitle('Upload Image to Database')    
        self.setWindowIcon(QtGui.QIcon('icon.png')) 
        self.show()
        self.display_latest_img()
        self.update_preview()
        sleep(10)
        self.update_preview()
        
        
        
    def display_latest_img(self):
        self.IMG_FILEFOLDER = self.load_latest_image(self.IMG_FOLDER)
        img = QtWidgets.QLabel(self)
        img_resized = QtGui.QPixmap(self.IMG_FILEFOLDER).scaled(self.IMG_WIDTH, 
                                                       self.IMG_HEIGHT, 
                                                       QtCore.Qt.KeepAspectRatio)
        img.setPixmap(img_resized)
        img.setMinimumSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        img.setStyleSheet("border: 1px solid black")
        self.grid.addWidget(img, 2, 1, 10, 1)
        self.setLayout(self.grid)
        self.show()
        
    def update_preview(self):
        subprocess.check_output(['gphoto2','--capture-preview','--force-overwrite'])
        preview_resized = QtGui.QPixmap('capture_preview.jpg').scaled(300, 
                                                       300, 
                                                       QtCore.Qt.KeepAspectRatio)
        preview = QtWidgets.QLabel(self)
        preview.setPixmap(preview_resized)
        preview.setMinimumSize(300, 300)
        self.grid.addWidget(preview, 6, 0)
        self.setLayout(self.grid)
        self.show()
        
        

    def auto_detect_camera(self):
        auto_detect_output = 'Cameras Detected: \n%s'%subprocess.check_output(['gphoto2','--auto-detect'])
        if len(auto_detect_output) <= 126:
            warning = 'Error xkcd1314: No cameras detected'
            self.warn(warning)
            return auto_detect_output + warning
        return auto_detect_output
    
    def load_latest_image(self, image_folder):
        images = os.listdir(image_folder)
        latest_image = max([os.path.join(image_folder, image) for image in images], key=os.path.getctime)
        return latest_image
    
    def take_photo(self):
        output = subprocess.check_output(['gphoto2','--capture-image-and-download','--filename','images/%y%m%d%H%M%S.jpg'])
        print(output)
        self.display_latest_img()
        return output

    def get_qr_code(self):
        decoded_list = pyzbar.decode(cv2.imread(self.IMG_FILEFOLDER))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            self.warn('Error xkcd1237: Qr code not found in image!')
            return ''

    def setImgQuality(self, ImgQuality):
        output = subprocess.check_output(['gphoto2',
                                        '--set-config-index',
                                        '/main/capturesettings/imagequality=%s'%ImgQuality])
        if len(output) > 0:
            warn('Setting image quality failed, output: %s'%output)

    def closeEvent(self, event):
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        #    event.accept()
        #else:
        #    event.ignore() 
        self.sched.shutdown()
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
    ex = Example()
    sys.exit(app.exec_())