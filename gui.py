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
import functools
import subprocess

from time import sleep
from PyQt5 import QtGui, QtCore, QtWidgets
from pyzbar import pyzbar


class basicGUI(QtWidgets.QWidget):
    def __init__(self):
        super(basicGUI, self).__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

    def commandLine(self, args):
        assert isinstance(args,list)
        
        if ('captureThread' in globals()) & (args[0] == 'gphoto2'):
            captureThread.pause()

        try:
            output = subprocess.check_output(args)
            if ('captureThread' in globals()) & (args[0] == 'gphoto2'):
                captureThread.resume()
            return output
        except Exception as ex:
            self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))
            if ('captureThread' in globals()) & (args[0] == 'gphoto2'):
                captureThread.resume()
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


class ClickableIMG(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.objectName())
    
class capturePreview(QtCore.QThread, basicGUI):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.paused = False

    def run(self):
        while( self.isRunning() ):
            if self.paused == False:
                self.running = True
                try:
                    subprocess.check_output(['gphoto2','--capture-preview','--force-overwrite'])
                except Exception as ex:
                    pass
                self.running = False
                #print('Updated Preview')
            sleep(2)
            
    def pause(self):
        self.paused = True
        while self.running == True:
            sleep(2)
        return True
        
    def resume(self):
        self.paused = False
        


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
        
        
class openConfigGUI(basicGUI):
    def __init__(self):
        super(openConfigGUI, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.configButton = QtWidgets.QPushButton('Open Config')
        self.configButton.clicked.connect(self.openConfig)
        self.dialog = configGUI()
        
        self.grid.addWidget(self.configButton)
        self.setLayout(self.grid)
        
    def openConfig(self):
        self.dialog.show()
    
    
        
class configGUI(basicGUI):
    def __init__(self):
        super(configGUI, self).__init__()
        self.configOptions = self.getConfigOptions()
        
        self.initUI()

    def initUI(self):
        row = 13
        for option in self.configOptions.keys():
            widget = QtWidgets.QLabel(self.configOptions[option]['Label'])
            widget.name = option
            if option == '/main/capturesettings/shutterspeed':
                widgetEdit = QtWidgets.QLineEdit()
                widgetEdit.name = option
                widgetEdit.setText(self.configOptions[option]['Current'])
                
            elif self.configOptions[option]['Type'] in ['MENU','RADIO']:
                widgetEdit = QtWidgets.QComboBox()
                widgetEdit.name = option
                widgetEdit.addItems(self.configOptions[option]['Choices'])
                widgetEdit.setCurrentIndex(self.getCurrentOptionIndex(option))
                widgetEdit.currentIndexChanged.connect(functools.partial(self.updateConfigOptionByIndex, option))
            
            elif self.configOptions[option]['Type'] in ['RANGE']:
                widgetEdit = QtWidgets.QLineEdit()
                widgetEdit.name = option
                widgetEdit.setText(self.configOptions[option]['Current'])
                
            elif self.configOptions[option]['Type'] in ['TEXT', 'TOGGLE']:
                widgetEdit = QtWidgets.QLabel(self.configOptions[option]['Current'])
                widgetEdit.name = option
            
            self.grid.addWidget(widget, row, 0)
            self.grid.addWidget(widgetEdit, row, 1)
            row += 1
        self.showCurrent()
            
        setDefaultButton = QtWidgets.QPushButton('Reset to Default')
        setDefaultButton.clicked.connect(self.setDefaultOptions)
        self.grid.addWidget(setDefaultButton)
        
        self.setLayout(self.grid)
        
    

    def showCurrent(self):
        widgets = (self.grid.itemAt(i).widget() for i in range(self.grid.count())) 
        for widget in widgets:
            widget_class = widget.__class__.__name__
            if widget_class in ['QComboBox','QLineEdit']:
                option = widget.name
                actual = self.configOptions[option]['Current']
                if option == '/main/capturesettings/shutterspeed':
                    widget.setText(actual)
                elif self.configOptions[option]['Type'] in ['RANGE']:
                    widget.setText(actual)
                elif self.configOptions[option]['Type'] in ['MENU','RADIO']:
                    widget.setCurrentIndex(self.getCurrentOptionIndex(option))

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
        #pprint.pprint([(key, config[key]['Current']) for key in config.keys()])

        return config
    
    def setDefaultOptions(self):
        defaultConfig = {'/main/capturesettings/expprogram':'M',
                         '/main/status/vendorextension':'Sony PTP Extensions',
                         '/main/capturesettings/imagequality':'Extra Fine',
                         '/main/actions/opcode':'0x1001,0xparam1,0xparam2',
                         '/main/capturesettings/flashmode':'Fill flash',
                         '/main/imgsettings/whitebalance':'Choose Color Temperature',
                         '/main/imgsettings/colortemperature':'4200',
                         '/main/capturesettings/exposurecompensation':'0',
                         '/main/capturesettings/exposuremetermode':'Unknown value 8001',
                         '/main/status/cameramodel':'ILCE-7RM3',
                         '/main/status/batterylevel':'98%',
                         '/main/capturesettings/f-number':'11',
                         '/main/imgsettings/imagesize':'Large',
                         '/main/capturesettings/aspectratio':'3:2',
                         '/main/status/deviceversion':'1.0',
                         '/main/actions/capture':'2',
                         '/main/status/serialnumber':'00000000000000003282933003783803',
                         '/main/capturesettings/shutterspeed':'1/10',
                         '/main/actions/movie':'2',
                         '/main/actions/bulb':'2',
                         '/main/capturesettings/focusmode':'Manual',
                         '/main/actions/manualfocus':'0',
                         '/main/status/manufacturer':'Sony Corporation',
                         '/main/imgsettings/iso':'3200',
                         '/main/actions/autofocus':'2',
                         '/main/capturesettings/capturemode':'Single Shot'}
        for option in defaultConfig.keys():
            if defaultConfig[option] != self.configOptions[option]['Current']:
                if option == '/main/capturesettings/shutterspeed':
                    self.updateConfigValue(option, defaultConfig[option], showCurrent=False)
                elif self.configOptions[option]['Type'] in ['RANGE']:
                    self.updateConfigValue(option, defaultConfig[option], showCurrent=False)
                elif self.configOptions[option]['Type'] in ['MENU','RADIO']:
                    self.updateConfigOptionByName(option, defaultConfig[option], showCurrent = False)
        self.showCurrent()

    def updateConfigOptionByIndex(self, option, choice_index, showCurrent = True):
        self.commandLine(['gphoto2','--set-config-index',option+'='+str(choice_index)])
        self.configOptions = self.getConfigOptions()
        
    def updateConfigOptionByName(self, option, choice, showCurrent = True):
        choice_index = self.configOptions[option]['Choices'].index(choice)
        return self.updateConfigOptionByIndex(option, choice_index, showCurrent)
    
    def updateConfigValue(self, option, value, showCurrent = True):
        self.commandLine(['gphoto2','--set-config-value',option+'='+str(value)])
    

    
class liveViewGUI(basicGUI):
    def __init__(self):
        super(liveViewGUI, self).__init__()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePreview)
        self.timer.start(100)
        self.initUI()
        
    def initUI(self):
        self.preview = ClickableIMG(self)
        self.preview.setMinimumSize(1024,680)
        self.preview.clicked.connect(self.openIMG)
        
        self.QRCode = QtWidgets.QLabel('QR Code:')
        
        self.grid.addWidget(self.QRCode, 0, 0)
        self.grid.addWidget(self.preview, 1, 0)
        self.setLayout(self.grid)
        
    def openIMG(self):
        self.commandLine(['open','capture_preview.jpg'])
    
    def updatePreview(self):
        preview_img = QtGui.QPixmap('capture_preview.jpg').scaled(1024,680, 
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
        self.IMG_HEIGHT = 680//2
        self.IMG_WIDTH = 1024//2
        
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
        self.img = ClickableIMG(self)
        self.img.setMinimumSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        self.img.setStyleSheet("border: 1px solid black")
        self.img.clicked.connect(self.openIMG)
        
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
        
    def openIMG(self):
        self.commandLine(['open', self.IMG_FILEFOLDER])

    def takePhoto(self):
        IMG_QUALITY_SETTINGS = self.commandLine(['gphoto2','--get-config','/main/capturesettings/imagequality'])
        IMG_QUALITY = IMG_QUALITY_SETTINGS.split('\n')[3][9:]
        if IMG_QUALITY in ['Standard','Fine','Extra Fine']:
            IMG_FORMAT = 'jpg'
        else:
            IMG_FORMAT = 'arw'
        self.commandLine(['gphoto2', '--capture-image-and-download', '--filename', 
                          'images/%y-%m-%d %H%M%S.' + IMG_FORMAT, '--force-overwrite'])
        self.displayLatestImg()
        
    def getLatestImageName(self, image_folder):
        images = [image for image in os.listdir(image_folder) if image.split('.')[-1] in ['jpg','arw']]
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
        self.config = openConfigGUI()
        self.initUI()
        
    def initUI(self):        
        self.setWindowTitle('Upload Image to Database')  
        self.setWindowIcon(QtGui.QIcon('icon.png')) 
        
        okButton = QtWidgets.QPushButton("Save and Send to Database")
        cancelButton = QtWidgets.QPushButton("Cancel")
        
        self.grid.addWidget(self.instructions, 0, 0)
        self.grid.addWidget(self.auto_detect_camera, 1, 0)
        self.grid.addWidget(self.live_view, 2, 0)
        self.grid.addWidget(self.config, 4, 0)
        self.grid.addWidget(self.image_view, 0, 1, 3, 1)
        self.grid.addWidget(okButton, 5, 0)
        self.grid.addWidget(cancelButton, 5, 1)
        self.setLayout(self.grid)
        
        self.show()
        

if __name__ == '__main__':
    global captureThread
    captureThread = capturePreview()
    captureThread.start()

    QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_())