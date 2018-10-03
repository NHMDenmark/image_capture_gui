#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:03:22 2018

@author: robertahunt
"""
import functools
import subprocess

from time import sleep
from PyQt5 import QtWidgets
from basicGUI import basicGUI

defaultConfig = {'/main/capturesettings/expprogram':'M', #not controllable
                 '/main/status/vendorextension':'Sony PTP Extensions', #not controllable
                 '/main/capturesettings/imagequality':'RAW', #Controllable
                 '/main/actions/opcode':'0x1001,0xparam1,0xparam2', #not controllable
                 '/main/capturesettings/flashmode':'Flash off', #Somewhat controllable
                 '/main/imgsettings/whitebalance':'Preset 1', #
                 '/main/imgsettings/colortemperature':'5200', #controllable if whitebalance set to 'Choose Color Temperature'
                 '/main/capturesettings/exposurecompensation':'0', #not controllable
                 '/main/capturesettings/exposuremetermode':'Unknown value 8001', #Seems controllable
                 '/main/status/cameramodel':'ILCE-7RM3', #not controllable
                 '/main/status/batterylevel':'98%', #not controllable
                 '/main/capturesettings/f-number':'11', #Controllable
                 '/main/imgsettings/imagesize':'Large', #Controllable
                 '/main/capturesettings/aspectratio':'3:2', #Controllable
                 '/main/status/deviceversion':'1.0', #not controllable
                 '/main/actions/capture':'2', #not controllable
                 '/main/status/serialnumber':'00000000000000003282933003783803', #not controllable
                 '/main/capturesettings/shutterspeed':'1/15', #Controllable
                 '/main/actions/movie':'2', #not controllable
                 '/main/actions/bulb':'2', #not controllable
                 '/main/capturesettings/focusmode':'Manual', #not controllable
                 '/main/actions/manualfocus':'0', #not controllable
                 '/main/status/manufacturer':'Sony Corporation', #not controllable
                 '/main/imgsettings/iso':'200', #Controllable
                 '/main/actions/autofocus':'2', #not controllable
                 '/main/capturesettings/capturemode':'Single Shot'} #Controllable

fNumbers = ['2.8', '3.2', '3.5', '4.0', '4.5', '5.0', '5.6', '6.3', '7.1', 
            '9.8', '10', '11', '13', '14', '16', '18', '20', '22']

shutterSpeeds = ['1/8000','1/6400','1/5000','1/4000','1/3200','1/2500',
                 '1/2000','1/1600','1/1250','1/1000','1/800','1/640',
                 '1/500','1/400','1/320','1/250','1/200','1/160','1/125',
                 '1/100','1/80','1/60','1/50','1/40','1/30','1/25','1/20',
                 '1/15','1/13','1/10','1/8','1/6','1/5','1/4','1/3','0.4',
                 '0.5','0.6','0.8','1','1.3','1.6','2','2.5','3.2','4','5',
                 '6','8','10','13','15','20','25','30']

colorTemperatures = ['0'] + [str(x) for x in list(range(3000,8000,100))]

class configGUI(basicGUI, QtWidgets.QMainWindow):
    def __init__(self):
        super(configGUI, self).__init__()
        self.configOptions = self.getConfigOptions()
        self.widgets = {}
        self.initUI()
        
    
    #def colorTempWidgets(self):
    #    path = '/main/imgsettings/colortemperature'
    #    config = self.configOptions[path]
    #    labelWidget = QtWidgets.QLabel(config['Label'])
    #    
    #    editWidget = QtWidgets.QLineEdit()
    #    editWidget.setText(config['Current'])
    #    editWidget.editingFinished.connect(functools.partial(self.updateValue, path))
    #    
    #    editWidget.name = path
    #    self.widgets[path] = editWidget
    #    return labelWidget, editWidget
    def colorTempWidgets(self):
        path = '/main/imgsettings/colortemperature'
        return self.makeWidgetsFromPath(path)
        
        
    def fNumberWidgets(self):
        path = '/main/capturesettings/f-number'
        return self.makeWidgetsFromPath(path)
    
    def imageSizeWidgets(self):
        path = '/main/imgsettings/imagesize'
        return self.makeWidgetsFromPath(path)
        
    def shutterSpeedWidgets(self):
        path = '/main/capturesettings/shutterspeed'
        return self.makeWidgetsFromPath(path) 
    
    def isoWidgets(self):
        path = '/main/imgsettings/iso'
        return self.makeWidgetsFromPath(path) 
    
    def captureModeWidgets(self):
        path = '/main/capturesettings/capturemode'
        return self.makeWidgetsFromPath(path)

    def imgQualityWidgets(self):
        path = '/main/capturesettings/imagequality'
        return self.makeWidgetsFromPath(path)
    
    def whiteBalanceWidgets(self):
        path = '/main/imgsettings/whitebalance'
        return self.makeWidgetsFromPath(path)  
    
    def flashModeWidgets(self):
        path = '/main/capturesettings/flashmode'
        return self.makeWidgetsFromPath(path)
    
    def makeWidgetsFromPath(self, path):
        config = self.configOptions[path]
        labelWidget = QtWidgets.QLabel(config['Label'])
        
        editWidget = QtWidgets.QComboBox()
        editWidget.addItems(config['Choices'])
            
        currentIndex = self.getCurrentOptionIndex(path)
            
        editWidget.setCurrentIndex(currentIndex)
        if path in ['/main/capturesettings/f-number',
                    '/main/capturesettings/shutterspeed',
                    '/main/imgsettings/colortemperature']:
            editWidget.activated.connect(functools.partial(
                    self.updateValueByIndex, path))
        else:
            editWidget.activated.connect(functools.partial(
                    self.updateConfigOptionByIndex, path))
        editWidget.name = path
        self.widgets[path] = editWidget
        return labelWidget, editWidget


    def initUI(self):
        iso, self.isoEdit = self.isoWidgets()
        fNumber, self.fNumberEdit = self.fNumberWidgets()
        flashMode, self.flashModeEdit = self.flashModeWidgets()
        colorTemp, self.colorTempEdit = self.colorTempWidgets()
        #imageSize, self.imageSizeEdit = self.imageSizeWidgets()
        #imgQuality, self.imgQualityEdit = self.imgQualityWidgets()
        captureMode, self.captureModeEdit = self.captureModeWidgets()
        whiteBalance, self.whiteBalanceEdit = self.whiteBalanceWidgets()
        shutterSpeed, self.shutterSpeedEdit = self.shutterSpeedWidgets()
        
        setDefaultButton = QtWidgets.QPushButton('Reset to Default')
        setDefaultButton.clicked.connect(self.setDefaultOptions)
        showCurrentButton = QtWidgets.QPushButton('Show Current')
        showCurrentButton.clicked.connect(self.showCurrent)
    
        #self.grid.addWidget(imgQuality, 0, 0)
        #self.grid.addWidget(self.imgQualityEdit, 0, 1)
        #self.grid.addWidget(imageSize, 1, 0)
        #self.grid.addWidget(self.imageSizeEdit, 1, 1)
        self.grid.addWidget(fNumber, 2, 0)
        self.grid.addWidget(self.fNumberEdit, 2, 1)
        self.grid.addWidget(shutterSpeed, 3, 0)
        self.grid.addWidget(self.shutterSpeedEdit, 3, 1)
        self.grid.addWidget(iso, 4, 0)
        self.grid.addWidget(self.isoEdit, 4, 1)
        self.grid.addWidget(whiteBalance, 5, 0)
        self.grid.addWidget(self.whiteBalanceEdit, 5, 1)
        self.grid.addWidget(colorTemp, 6, 0)
        self.grid.addWidget(self.colorTempEdit, 6, 1)
        self.grid.addWidget(captureMode, 7, 0)
        self.grid.addWidget(self.captureModeEdit, 7, 1)
        self.grid.addWidget(flashMode, 8, 0)
        self.grid.addWidget(self.flashModeEdit, 8, 1)
        self.grid.addWidget(setDefaultButton, 9, 1)
        #self.grid.addWidget(showCurrentButton, 10, 0)
        
        self.showCurrent()
            
        self.setLayout(self.grid)
                
        #self.widgets['/main/imgsettings/colortemperature'].clearFocus()
    

    def showCurrent(self):
        sleep(0.5)
        
        self.configOptions = self.getConfigOptions()

        for path in self.widgets.keys():
            widget = self.widgets[path]
            widget_class = widget.__class__.__name__
            if widget_class in ['QComboBox', 'QLineEdit']:
                path = widget.name
                actual = self.configOptions[path]['Current']
                if False:#path == '/main/imgsettings/colortemperature':
                    widget.setText(actual)
                else:
                    widget.setCurrentIndex(self.getCurrentOptionIndex(path))

    def getCurrentOptionIndex(self, path):
        return self.configOptions[path]['Choices'].index(
                        self.configOptions[path]['Current'])

    def setDefaultOptions(self):   
        self.configOptions = self.getConfigOptions()
        path = '/main/imgsettings/whitebalance'
        if defaultConfig[path] != self.configOptions[path]['Current']:
            index = self.widgets[path].findText(defaultConfig[path])
            self.updateValueByIndex(path, index, showCurrent=False)
            
        for path in self.widgets.keys():
            if defaultConfig[path] != self.configOptions[path]['Current']:
                if False:#path in ['/main/imgsettings/colortemperature']:
                    self.updateValue(path, defaultConfig[path], showCurrent=False)
                elif path in ['/main/capturesettings/f-number',
                            '/main/capturesettings/shutterspeed',
                            '/main/imgsettings/colortemperature']:
                    index = self.widgets[path].findText(defaultConfig[path])
                    self.updateValueByIndex(path, index, showCurrent=False)
                else:
                    self.updateConfigOptionByName(path, defaultConfig[path], showCurrent = False)
        self.showCurrent()

    def updateConfigOptionByIndex(self, path, choice_index, showCurrent = True):
        self.commandLine(['gphoto2','--set-config-index',path+'='+str(choice_index)])
        
        if path == '/main/imgsettings/whitebalance':
            if self.widgets[path].itemText(choice_index) != 'Choose Color Temperature':
                pass
                #self.updateValue('/main/imgsettings/colortemperature', '0')
        if showCurrent == True:
            self.showCurrent()
        
    def updateConfigOptionByName(self, path, choice, showCurrent = True):
        choice_index = self.configOptions[path]['Choices'].index(choice)
        return self.updateConfigOptionByIndex(path, choice_index, showCurrent)
    
    def updateValueByIndex(self, path, index, showCurrent = True):
        value = self.widgets[path].itemText(index)
        self.commandLine(['gphoto2','--set-config-value',path+'='+str(value)])
        if showCurrent == True:
            self.showCurrent()
    
    def updateValue(self, path, value = None, showCurrent = True):
        if value is None:
            value = self.widgets[path].text()
        if path == '/main/imgsettings/colortemperature':
            if self.widgets['/main/imgsettings/whitebalance'].itemText(self.widgets['/main/imgsettings/whitebalance'].currentIndex()) != 'Choose Color Temperature':
                value = 0
        self.commandLine(['gphoto2','--set-config-value',path+'='+str(value)])
        if showCurrent == True:
            self.showCurrent()
        self.widgets[path].clearFocus()
            
    def getConfigOptions(self):
        raw_config = self.commandLine(['gphoto2','--list-all-config'])
        config = {}
        if isinstance(raw_config, subprocess.CalledProcessError):
            self.warn('Could not get config params from camera. Restart camera and try again', _exit=True)
        
        for line in raw_config.split('\n'):
            if 'other' in line:
                break
            
            if line.startswith('/'):
                name = line
                config[name] = {}
                config[name]['Choices'] = []
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
                config[name]['Choices'] += [choice]
            elif line.startswith('Bottom:'):
                config[name]['Bottom'] = float(line[8:])
            elif line.startswith('Top:'):
                config[name]['Top'] = float(line[5:])
            elif line.startswith('Step:'):
                config[name]['Step'] = float(line[6:])
        
        config['/main/capturesettings/f-number']['Choices'] = fNumbers
        config['/main/capturesettings/shutterspeed']['Choices'] = shutterSpeeds 
        config['/main/imgsettings/colortemperature']['Choices'] = colorTemperatures
        return config

    
            