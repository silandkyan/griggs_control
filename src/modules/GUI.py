#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:08:43 2023

@author: pgross
"""

import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow)
from PyQt5.QtCore import QCoreApplication

from gui.main_window_ui import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Motor Control Panel -- MoCoPa')
        # setup functions:
        self.set_allowed_ranges()
        self.set_default_values()
        self.connectSignalsSlots()
        self.show()
        
    def set_default_values(self):
        '''User input: Specify default values here.'''
        ### User input values (with allowed min-max ranges)
        # rpm for all constant speed modes (single, multi, constant):
        self.rpmBox.setValue(10)    # default rpm
        # amount of single steps in multistep mode:
        self.multistep_numberBox.setValue(10)   # amount of single steps 
        ### Hardware settings values (with allowed min-max ranges)
        # motor steps:
        self.stepsBox.setValue(400)         # number of motor steps
        # motor microsteps:
        self.microstepsBox.setValue(256)    # number of microsteps
        # motor rpm (could also be derived from other params...)
        self.rpm_minBox.setValue(0)         # min rpm value
        self.rpm_maxBox.setValue(300)       # max rpm value
        
        
    def connectSignalsSlots(self):
        '''This function defines the widget behaviour with Qt's 
        signal-and-slot mechanism.'''
        # Close window:
        self.quitButton.clicked.connect(self.close)
        # Single step rotation:
        self.singlelButton.clicked.connect(self.single_step_left)
        self.singlerButton.clicked.connect(self.single_step_right)
        # Multi step rotation with emergency stop:
        self.multilButton.clicked.connect(self.multi_step_left)
        self.multirButton.clicked.connect(self.multi_step_right)
        self.multistopButton.clicked.connect(self.stop_motor)
        # Constant (endless) rotation with emergency stop:
        self.constlButton.clicked.connect(self.const_rot_left)
        self.constrButton.clicked.connect(self.const_rot_right)
        self.conststopButton.clicked.connect(self.stop_motor)
                
    def single_step_left(self):
        # dummy functionality
        print('single step left')
        
    def single_step_right(self):
        # dummy functionality
        print('single step right')
        
    def multi_step_left(self):
        print(str(self.multistep_numberBox.value()), 'steps left with', str(self.rpmBox.value()), 'rpm')
        
    def multi_step_right(self):
        print(str(self.multistep_numberBox.value()), 'steps right with', str(self.rpmBox.value()), 'rpm')
        
    def const_rot_left(self):
        print('Rotating left with', str(self.rpmBox.value()), 'rpm')
        
    def const_rot_right(self):
        print('Rotating right with', str(self.rpmBox.value()), 'rpm')
        
    def stop_motor(self):
        print('Motor stopped!')
        
            
    def set_allowed_ranges(self):
        '''Specify allowed min-max ranges for values that can 
        be changed in the GUI. These should usually be fine...'''
        ### User input values (with allowed min-max ranges)
        # rpm for all constant speed modes (single, multi, constant):
        self.rpmBox.setMinimum(0)
        self.rpmBox.setMaximum(999)
        # amount of single steps in multistep mode:
        self.multistep_numberBox.setMinimum(0)
        self.multistep_numberBox.setMaximum(999)
        ### Hardware settings values
        # motor steps:
        self.stepsBox.setMinimum(0)
        self.stepsBox.setMaximum(999)
        # motor microsteps:
        self.microstepsBox.setMinimum(0)
        self.microstepsBox.setMaximum(9999)
        # motor rpm (could also be derived from other params...)
        self.rpm_minBox.setMinimum(0)
        self.rpm_minBox.setMaximum(999)
        self.rpm_maxBox.setMinimum(0)
        self.rpm_maxBox.setMaximum(999)
        

#-----#   Main Program starts here   #-----#
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    
    # find general solution for the following 2 lines
    #sys.exit(app.exec()) # use this line with normal console
    sys.exit(QCoreApplication.quit()) # use this with IPython console
