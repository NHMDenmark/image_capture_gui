#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:03:22 2018

@author: robertahunt
"""
import functools

from PyQt5 import QtWidgets
from basicGUI import basicGUI

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


class configGUI(basicGUI, QtWidgets.QMainWindow):
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
        if showCurrent == True:
            self.showCurrent()
        
    def updateConfigOptionByName(self, option, choice, showCurrent = True):
        choice_index = self.configOptions[option]['Choices'].index(choice)
        return self.updateConfigOptionByIndex(option, choice_index, showCurrent)
        if showCurrent == True:
            self.showCurrent()
    
    def updateConfigValue(self, option, value, showCurrent = True):
        self.commandLine(['gphoto2','--set-config-value',option+'='+str(value)])
        if showCurrent == True:
            self.showCurrent()
            
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
        self.dialog.raise_()
        self.dialog.show()