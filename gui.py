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

from pyzbar import pyzbar
from PyQt5 import QtGui, QtCore, QtWidgets

#_fromUtf8 = QtCore.QString.fromUtf8

class Example(QtWidgets.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.IMG_HEIGHT = 700
        self.IMG_WIDTH = 700
        self.IMG_QUALITY = 3
        self.IMG_FILENAME = 'qr_code6.jpg'
        self.IMG_FOLDER = 'images'
        
        self.initUI()
        
    def initUI(self):       
        inst_title = QtWidgets.QLabel('Instructions')
        inst_desc = QtWidgets.QLabel('''These are the instructions. 
                                      If you have any questions, 
                                      shoot roberta a mail: ngw861@alumni.ku.dk. 
                                      If it is urgent, call her: 91 93 20 26''')
       
        auto_detect_output = self.auto_detect_camera()
        auto_detect = QtWidgets.QLabel(auto_detect_output)
        
        latest_image = self.load_latest_image(self.IMG_FOLDER)
        
        qr_code_output = self.get_qr_code()
        qr_code = QtWidgets.QLabel('QR Code: %s'%qr_code_output)
        img = QtWidgets.QLabel(self)
        img_resized = QtGui.QPixmap(os.path.join(self.IMG_FOLDER,self.IMG_FILENAME)).scaled(self.IMG_WIDTH, 
                                                       self.IMG_HEIGHT, 
                                                       QtCore.Qt.KeepAspectRatio)
        img.setPixmap(img_resized)
        img.setMinimumSize(self.IMG_WIDTH, self.IMG_HEIGHT)

        takePhotoButton = QtWidgets.QPushButton("Take Photo")
        takePhotoButton.clicked.connect(self.take_photo)
        okButton = QtWidgets.QPushButton("Save and Send to Database")
        cancelButton = QtWidgets.QPushButton("Cancel")

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(inst_title, 1, 0, 1, 1)
        grid.addWidget(inst_desc, 2, 0, 1, 1)
        grid.addWidget(auto_detect, 3, 0)
        grid.addWidget(takePhotoButton, 5, 0)
        grid.addWidget(qr_code, 4, 0)
        grid.addWidget(img, 1, 1, 5, 1)
        
        grid.addWidget(okButton, 6, 0)
        grid.addWidget(cancelButton, 6, 1)
        
        self.setLayout(grid) 
        
        self.setGeometry(300, 300, 350, 300)
        self.center()
        self.setWindowTitle('Upload Image to Database')    
        self.setWindowIcon(QtGui.QIcon('icon2.png')) 
        self.show()

    def auto_detect_camera(self):
        auto_detect_output = 'Cameras Detected: \n%s'%subprocess.check_output(['gphoto2','--auto-detect'])
        if len(auto_detect_output) <= 126:
            warning = 'Error xkcd1314: No cameras detected'
            self.warn(warning)
        return auto_detect_output + warning
    
    def load_latest_image(self, image_folder):
        images = os.listdir(image_folder)
        latest_image = max([os.path.join(image_folder, image) for image in images], key=os.path.getctime)
        print(latest_image)
        return 0
        
    
    def take_photo(self):
        print('Photo taken')
        return 0

    def get_qr_code(self):
        decoded_list = pyzbar.decode(cv2.imread(os.path.join(self.IMG_FOLDER,self.IMG_FILENAME)))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            self.warn('Error xkcd1237: Qr code not found in image!')
            return ''

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

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
    ex = Example()
    sys.exit(app.exec_())