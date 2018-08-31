# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:59:05 2018

@author: ngw861
"""
import os
import cv2
import sys
import rawpy
import pprint
import warnings
import subprocess

from time import sleep
from PyQt5 import QtGui, QtCore, QtWidgets
from pyzbar import pyzbar
from multiprocessing import Pool


class basicGUI(QtWidgets.QWidget):
    def __init__(self):
        super(basicGUI, self).__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

    def commandLine(self, args):
        assert isinstance(args,list)
        try:
            output = subprocess.check_output(args)
            return output
        except Exception as ex:
            self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))
            return ex
        
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
    
    
class capturePreview(QtCore.QThread, basicGUI):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        while( self.isRunning() ):
            try:
                pass
                #self.commandLine(['gphoto2','--capture-preview','--force-overwrite'])
            except Exception as ex:
                pass
            
            sleep(1)
            #print('Updated Preview')


class instructionsGUI(basicGUI):
    def __init__(self):
        super(instructionsGUI, self).__init__()
        
        self.inst_title = QtWidgets.QLabel('Instructions')
        self.inst_desc = QtWidgets.QLabel('''1. Make sure camera is on, usb cable is connected, 
        and camera is set to auto-focus.
        
        If you have any questions, 
        shoot roberta a mail: ngw861@alumni.ku.dk. 
        If it is urgent, call her: 91 93 20 26
        ''')
        self.initUI()
        
    def initUI(self):
        self.grid.addWidget(self.inst_title)
        self.grid.addWidget(self.inst_desc)
        self.setLayout(self.grid)
        
        
class configGUI(basicGUI):
    def __init__(self):
        super(configGUI, self).__init__()
        self.configOptions = self.getConfigOptions()
        
        self.initUI()
    
    def initUI(self):
        row = 13
        for option in self.configOptions.keys():
            widget = QtWidgets.QLabel(self.configOptions[option]['Label'])
            if option == '/main/capturesettings/shutterspeed':
                widgetEdit = QtWidgets.QLineEdit()
                widgetEdit.setText(self.configOptions[option]['Current'])
                
            elif self.configOptions[option]['Type'] in ['MENU','RADIO']:
                widgetEdit = QtWidgets.QComboBox()
                widgetEdit.addItems(self.configOptions[option]['Choices'])
                widgetEdit.setCurrentIndex(self.getCurrentOptionIndex(option))
                widgetEdit.currentIndexChanged.connect(lambda x: self.updateConfigIndex(config, choice))
                
            self.grid.addWidget(widget, row, 0)
            self.grid.addWidget(widgetEdit, row, 1)
            row += 1
        self.setLayout(self.grid)

    def setCurrent(self):
        

    def getCurrentOptionIndex(self, option):
        return self.configOptions[option]['Choices'].index(
                        self.configOptions[option]['Current'])
    
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
                config[name]['Choice Indices'] = []
            elif line.startswith('Label:'):
                config[name]['Label'] = line[7:]
            elif line.startswith('Readonly:'):
                config[name]['Readonly'] = line[10:]
            elif line.startswith('Type:'):
                config[name]['Type'] = line[6:]
            elif line.startswith('Current:'):
                config[name]['Current'] = line[9:]
            elif line.startswith('Choice:'):
                choice = ' '.join(line[8:].split(' ')[1:])
                choice_index = line[8:].split(' ')[0]
                config[name]['Choices'] += [choice]
                config[name]['Choice Indices'] += [choice_index]
            elif line.startswith('Bottom:'):
                config[name]['Bottom'] = line[8:]
            elif line.startswith('Top:'):
                config[name]['Top'] = line[4:]
            elif line.startswith('Step:'):
                config[name]['Step'] = line[4:]
        pprint.pprint(config)

        return config

    def updateConfigIndex(self, option, choice):
        choice_index = self.configOptions[option]['Choices'].index(choice)
        self.commandLine(['gphoto2','--set-config-index',option+'='+str(choice_index)])
        self.configOptions = self.getConfigOptions()
        self.setCurrent()
    


    
class liveViewGUI(basicGUI):
    def __init__(self):
        super(liveViewGUI, self).__init__()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePreview)
        self.timer.start(500)
        self.thread = capturePreview()
        self.thread.start()
        self.initUI()
        
    def initUI(self):
        self.preview = QtWidgets.QLabel(self)
        self.QRCode = QtWidgets.QLabel('QR Code:')
        
        self.preview.setMinimumSize(350, 250)
        
        self.grid.addWidget(self.QRCode, 0, 0)
        self.grid.addWidget(self.preview, 1, 0)
        self.setLayout(self.grid)

    
    def updatePreview(self):
        #if 'thread' in self.__dict__:
        #    self.thread.terminate()
        
        #self.thread = capturePreview()
        #self.thread.start()
        preview_img = QtGui.QPixmap('capture_preview.jpg').scaled(350, 250, 
                                                       QtCore.Qt.KeepAspectRatio)
        QRCode_text = self.getQRCode('capture_preview.jpg')
        
        self.preview.setPixmap(preview_img)
        self.QRCode.setText('QR Code:' + QRCode_text)
        
    def getNewPreview(self):
        self.commandLine(['gphoto2','--capture-preview','--force-overwrite'])
    
    def getQRCode(self, img_path):
        decoded_list = pyzbar.decode(cv2.imread(img_path))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            return 'QR Code not found'


class imageViewGUI(basicGUI):
    def __init__(self):
        super(imageViewGUI, self).__init__()
        self.IMG_HEIGHT = 500
        self.IMG_WIDTH = 700
        self.IMG_QUALITY = 4
        
        self.setImgQuality(self.IMG_QUALITY)
        self.IMG_FOLDER = 'images'
        self.IMG_FILEFOLDER = self.getLatestImageName(self.IMG_FOLDER)
        self.IMG = self.getIMG()
        self.initUI()
    

    def getIMG(self):
        IMG_FORMAT = self.IMG_FILEFOLDER.split('.')[-1]
        if IMG_FORMAT == 'jpg':
            return cv2.imread(self.IMG_FILEFOLDER)
        elif IMG_FORMAT == 'arw':
            with rawpy.imread(self.IMG_FILEFOLDER) as raw:
                return raw.postprocess()
        else:
            self.warn('Image format in folder not understood.%s'%self.IMG_FORMAT)
    
    def initUI(self):
        self.img = QtWidgets.QLabel(self)
        self.img.setMinimumSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        self.img.setStyleSheet("border: 1px solid black")
        img_title = QtWidgets.QLabel('Latest image in folder: %s'%os.path.join(os.getcwd(),self.IMG_FOLDER))
        takePhotoButton = QtWidgets.QPushButton("Take Photo")
        takePhotoButton.clicked.connect(self.takePhoto)
        QRCode_text = self.getQRCode(self.IMG_FILEFOLDER)
        QRCode = QtWidgets.QLabel('QR Code: ' + QRCode_text)
        
        self.grid.addWidget(img_title, 0, 0)
        self.grid.addWidget(QRCode, 1, 0)
        self.grid.addWidget(self.img, 2, 0)
        self.displayLatestImg()
        self.grid.addWidget(takePhotoButton, 3, 0)
        self.setLayout(self.grid)
    
    def setImgQuality(self, ImgQuality):
        self.commandLine(['gphoto2', '--set-config-index',
                            '/main/capturesettings/imagequality=%s'%ImgQuality])

    def takePhoto(self):
        #self.IMG_QUALITY = self.commandLine(['gphoto2','--get-config','/main/capturesettings/imagequality'])
        if int(self.IMG_QUALITY) in [0,1,2]:
            IMG_FORMAT = 'jpg'
        else:
            IMG_FORMAT = 'arw'
        output = self.commandLine(['gphoto2', '--capture-image-and-download',
                           '--filename', 'images/%y-%m-%d %H%M%S.' + IMG_FORMAT])
        
        if 'ERROR' in output:
            self.warn('Error taking image. Try again. Maybe check focus')
        else:
            self.displayLatestImg()
        
    def getLatestImageName(self, image_folder):
        images = [image for image in os.listdir(image_folder) if image.split('.')[1] in ['jpg','arw']]
        latest_image_name = max([os.path.join(image_folder, image) for image in images], key=os.path.getctime)
        return latest_image_name
    
    def displayLatestImg(self):
        self.IMG_FILEFOLDER = self.getLatestImageName(self.IMG_FOLDER)
        IMG_FORMAT = self.IMG_FILEFOLDER.split('.')[-1]
        self.IMG = self.getIMG()
        if IMG_FORMAT == 'arw':
            img_resized = QtGui.QImage(self.IMG.data, self.IMG.shape[1], self.IMG.shape[0],
                                   self.IMG.shape[1]*3, QtGui.QImage.Format_RGB888)
            img_resized = QtGui.QPixmap.fromImage(img_resized).scaled(self.IMG_WIDTH, self.IMG_HEIGHT, 
                                                       QtCore.Qt.KeepAspectRatio)
        elif IMG_FORMAT == 'jpg':
            img_resized = QtGui.QPixmap(self.IMG_FILEFOLDER).scaled(self.IMG_WIDTH, self.IMG_HEIGHT, 
                                                       QtCore.Qt.KeepAspectRatio)
        self.img.setPixmap(img_resized)
                
    def getQRCode(self, img_path):
        decoded_list = pyzbar.decode(cv2.resize(self.IMG,(1024,680)))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            self.warn('Error xkcd1237: Qr code not found in image!')
            return ''
    
    
class autoDetectCameraGUI(basicGUI):
    def __init__(self):
        super(autoDetectCameraGUI, self).__init__()
        self.initUI()
    
    def initUI(self):
        auto_detect_output = self.autoDetectCamera()
        auto_detect = QtWidgets.QLabel(auto_detect_output)
        self.grid.addWidget(auto_detect)
        self.setLayout(self.grid) 
        
    def autoDetectCamera(self):
        auto_detect_output = 'Cameras Detected: \n%s'%self.commandLine(['gphoto2','--auto-detect'])
        if len(auto_detect_output) <= 126:
            warning = 'Error xkcd1314: No cameras detected'
            self.warn(warning)
            sys.exit()
            return auto_detect_output + warning
        return auto_detect_output


class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        self.instructions = instructionsGUI()
        self.auto_detect_camera = autoDetectCameraGUI()
        self.live_view = liveViewGUI()
        self.image_view = imageViewGUI()
        self.config = configGUI()
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Upload Image to Database')  
        self.setWindowIcon(QtGui.QIcon('icon.png')) 
        
        okButton = QtWidgets.QPushButton("Save and Send to Database")
        cancelButton = QtWidgets.QPushButton("Cancel")
        
        self.grid.addWidget(self.instructions, 0, 0)
        self.grid.addWidget(self.auto_detect_camera, 1, 0)
        self.grid.addWidget(self.live_view, 2, 0)
        self.grid.addWidget(self.image_view, 0, 1, 3, 1)
        self.grid.addWidget(self.config, 3, 0, 4, 1)
        self.grid.addWidget(okButton, 4, 0)
        self.grid.addWidget(cancelButton, 4, 1)
        self.setLayout(self.grid)
        
        self.show()
        

if __name__ == '__main__':
    QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_())