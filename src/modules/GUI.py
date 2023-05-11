#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:08:43 2023

@author: pgross
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication)
from modules.gui.main_window_ui import Ui_MainWindow

from .Motor import Motor 
from pytrinamic.connections import ConnectionManager


### Module connection ###
port_list = ConnectionManager().list_connections()
m = Motor(port_list[0])



class Window(QMainWindow, Ui_MainWindow):
    '''This custom class inherits from QMainWindow class and the custom 
    Ui_MainWindow class from main_window_ui.py file. That file is created 
    from main_window.ui using the pyuic5 command line program, e.g.:
    pyuic5 -x main_window.ui -o main_window_ui.py
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Motor Control Panel -- MoCoPa')
        # motor interface
        self.module = m
        self.motor = self.module.motor
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
        # initial calculation of pps:
        self.pps_calculator()
        # amount of single steps in multistep mode:
        self.multistep_numberBox.setValue(10)   # amount of single steps
        # set default button values:
        self.manual_radB.setChecked(True) # manual mode is default
        self.auto_radB.setChecked(False)
        
        
    def connectSignalsSlots(self):
        '''This function defines the widget behaviour with Qt's 
        signal-and-slot mechanism.'''
        # Close window and end program:
        self.quitButton.clicked.connect(self.close)
        # Single step rotation:
        self.singlelButton.clicked.connect(self.fine_step_left)
        self.singlerButton.clicked.connect(self.fine_step_right)
        # Multi step rotation:
        self.multilButton.clicked.connect(self.coarse_step_left)
        self.multirButton.clicked.connect(self.coarse_step_right)
        # Continuous rotation:
        self.contlButton.clicked.connect(self.permanent_left)
        self.contrButton.clicked.connect(self.permanent_right)
        # Stop button:
        self.stopButton.clicked.connect(self.stop_motor)
        # refresh rpm when value is changed:
        self.rpmBox.valueChanged.connect(self.pps_calculator)



    ###   CALCULATORS (for unit conversion to pps)   ###
    
    def pps_calculator(self):
        self.module.rpm = self.rpmBox.value()
        self.module.pps = round(self.module.rpm * self.module.msteps_per_rev/60)
            
        
    
    ###   MOTOR CONTROL FUNCTIONS   ###
    
    def stop_motor(self):
        '''Stop signal; can always be sent to the motors.'''
        self.motor.stop()
        # do not use time.sleep here!
        # set target_position to actual_position for the multi_control loop:
        act_pos = self.motor.get_axis_parameter(self.motor.AP.ActualPosition)
        self.motor.set_axis_parameter(self.motor.AP.TargetPosition, act_pos)
        # print status message
        print('Motor', self.module.moduleID, 'stopped!')
    
    def permanent_left(self):
        self.motor.rotate(-self.module.pps)
        print('Rotating left with', str(self.rpmBox.value()), 'rpm')
    
    def permanent_right(self):
        self.motor.rotate(self.module.pps)
        print('Rotating right with', str(self.rpmBox.value()), 'rpm')
            
    def fine_step_left(self):
        self.msteps = self.module.msteps_per_fstep #* self.spinB_fine.value()
        # self.motor.move_by(-self.msteps, self.pps)
        self.motor.move_by(-self.msteps, self.module.pps)
        print('Fine step left with Module', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        
    def coarse_step_left(self):
        self.msteps = self.module.msteps_per_fstep * self.multistep_numberBox.value()
        # self.motor.move_by(-self.msteps, self.pps)
        self.motor.move_by(-self.msteps, self.module.pps)
        print('Coarse step left with Module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        
    def fine_step_right(self):
        self.msteps = self.module.msteps_per_fstep #* self.spinB_fine.value()
        self.motor.move_by(self.msteps, self.module.pps)
        print('Fine step right with Module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        
    def coarse_step_right(self):
        self.msteps = self.module.msteps_per_fstep * self.multistep_numberBox.value()
        self.motor.move_by(self.msteps, self.module.pps)
        print('Coarse step right with Module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')

    

    ###   GENERAL GUI SETTINGS   ###
    
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
        
    

def run_app():
    app = 0
    '''Initialize GUI control flow management. Requires passing argument 
    vector (sys.argv) or empty list [] as arg; the former allows to pass 
    configuration commands on startup to the program from the command 
    line, if such commands were implemented. If app is already open, 
    use that one, otherwise open new app:'''
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    # Create main window (= instance of custom Window Class):
    main_win = Window()
    # Open GUI window on screen:
    main_win.show()
    # Return an instance of a running QApplication = starts event handling
    return app.exec()
