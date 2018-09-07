#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:03:22 2018

@author: robertahunt
"""
import functools
import subprocess

from PyQt5 import QtWidgets
from basicGUI import basicGUI

defaultConfig = {'/main/capturesettings/expprogram':'M', #not controllable
                 '/main/status/vendorextension':'Sony PTP Extensions', #not controllable
                 '/main/capturesettings/imagequality':'Extra Fine', #Controllable
                 '/main/actions/opcode':'0x1001,0xparam1,0xparam2', #not controllable
                 '/main/capturesettings/flashmode':'Fill flash', #Somewhat controllable
                 '/main/imgsettings/whitebalance':'Choose Color Temperature', #
                 '/main/imgsettings/colortemperature':'4200', #controllable if whitebalance set to 'Choose Color Temperature'
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
                 '/main/capturesettings/shutterspeed':'1/10', #Controllable
                 '/main/actions/movie':'2', #not controllable
                 '/main/actions/bulb':'2', #not controllable
                 '/main/capturesettings/focusmode':'Manual', #not controllable
                 '/main/actions/manualfocus':'0', #not controllable
                 '/main/status/manufacturer':'Sony Corporation', #not controllable
                 '/main/imgsettings/iso':'3200', #Controllable
                 '/main/actions/autofocus':'2', #not controllable
                 '/main/capturesettings/capturemode':'Single Shot'} #Controllable

    
class MyQSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self):
        super(MyQSpinBox, self).__init__()
        #self.valueChanged.connect(self.__handleValueChanged)
        #self.editingFinished.connect(self.__handleEditingFinished)
        #self._before = self.value()
        
    def __handleValueChanged(self, value):
        pass
        #self._before = value
        
    def __handleEditingFinished(self):
        pass
        #before,after = self._before, self.value()
        #if before != after:
        #    self._before = after
        #    self.textModified.emit(before, after)
        #print('Editing Finished, Value: %s'%self.value())
        #return self.value()

class configGUI(basicGUI, QtWidgets.QMainWindow):
    def __init__(self):
        super(configGUI, self).__init__()
        self.configOptions = self.getConfigOptions()
        self.widgets = {}
        self.initUI()

    def initUI(self):
        row = 13
        for option in self.configOptions.keys():
            widget = QtWidgets.QLabel(self.configOptions[option]['Label'])
            widget.name = option
            if option == '/main/capturesettings/shutterspeed':
                widgetEdit = QtWidgets.QLineEdit()
                widgetEdit.setText(self.configOptions[option]['Current'])
                widgetEdit.textEdited.connect(functools.partial(self.updateConfigValue, option))
                
            elif self.configOptions[option]['Type'] in ['MENU','RADIO']:
                widgetEdit = QtWidgets.QComboBox()
                widgetEdit.addItems(self.configOptions[option]['Choices'])
                widgetEdit.setCurrentIndex(self.getCurrentOptionIndex(option))
                widgetEdit.activated.connect(functools.partial(self.updateConfigOptionByIndex, option))
                
            
            elif self.configOptions[option]['Type'] in ['RANGE']:
                widgetEdit = QtWidgets.QLineEdit()
                widgetEdit.setText(self.configOptions[option]['Current'])
                widgetEdit.editingFinished.connect(functools.partial(self.updateTextConfigValue, option))
                
            elif self.configOptions[option]['Type'] in ['TEXT', 'TOGGLE']:
                widgetEdit = QtWidgets.QLabel(self.configOptions[option]['Current'])
            
            widgetEdit.name = option
            self.grid.addWidget(widget, row, 0)
            self.grid.addWidget(widgetEdit, row, 1)
            
            self.widgets[option] = {}
            self.widgets[option]['Label'] = widget
            self.widgets[option]['Edit'] = widgetEdit
            row += 1
        self.showCurrent()
            
        setDefaultButton = QtWidgets.QPushButton('Reset to Default')
        setDefaultButton.clicked.connect(self.setDefaultOptions)
        self.grid.addWidget(setDefaultButton)
        
        self.setLayout(self.grid)
        
        self._widgets = (self.grid.itemAt(i).widget() for i in range(self.grid.count()))
        self.widgets = {}
        for widget in self._widgets:
            if hasattr(widget, 'name'):
                self.widgets[widget.name] = widget
    

    def showCurrent(self):
        self.configOptions = self.getConfigOptions()
        
        
        for widget in self.widgets:
            widget_class = widget.__class__.__name__
            if widget_class in ['QComboBox', 'QLineEdit', 'QDoubleSpinBox','QSpinBox', 'MyQSpinBox']:
                option = widget.name
                actual = self.configOptions[option]['Current']
                if widget_class in ['QComboBox']:
                    if self.configOptions[option]['Type'] in ['RANGE']:
                        widget.setText(actual)
                    elif self.configOptions[option]['Type'] in ['MENU','RADIO']:
                        widget.setCurrentIndex(self.getCurrentOptionIndex(option))
                        
                elif widget_class in ['QLineEdit']:
                    widget.setText(actual)
                        
                elif widget_class in ['QDoubleSpinBox','QSpinBox']:
                    widget.setValue(float(actual))
                elif widget_class in ['MyQSpinBox']:
                    widget.valueChanged.disconnect()
                    widget.setValue(float(actual))
                    widget.valueChanged.connect(functools.partial(self.updateConfigValue, option))
                

    def getCurrentOptionIndex(self, option):
        return self.configOptions[option]['Choices'].index(
                        self.configOptions[option]['Current'])

    def setDefaultOptions(self):   
        self.configOptions = self.getConfigOptions()
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
        print('Updating Config Option by Index')
        self.commandLine(['gphoto2','--set-config-index',option+'='+str(choice_index)])
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
    
    def updateTextConfigValue(self, option, showCurrent = True):
        value = self.widgets[option].text()
        self.commandLine(['gphoto2','--set-config-value',option+'='+str(value)])
        if showCurrent == True:
            self.showCurrent()
        self.widgets[option].clearFocus()
            
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
                config[name]['Bottom'] = float(line[8:])
            elif line.startswith('Top:'):
                config[name]['Top'] = float(line[5:])
            elif line.startswith('Step:'):
                config[name]['Step'] = float(line[6:])
        return config
    
            
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