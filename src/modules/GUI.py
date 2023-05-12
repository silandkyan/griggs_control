#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:08:43 2023

@author: pgross
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication)
from PyQt5.QtCore import QTimer
from modules.gui.main_window_ui import Ui_MainWindow

from .Motor import Motor 
from pytrinamic.connections import ConnectionManager

'''
The following must be installed! 
Also, QWidget must be promoted to plotWidget in QtDesigner! See here:
https://www.pythonguis.com/tutorials/embed-pyqtgraph-custom-widgets-qt-app/'''
import pyqtgraph as pg

# from random import randint

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
        # graphing window:
        self.graphwindow()

        self.show()
        
    def set_default_values(self):
        '''User input: Specify default values here.'''
        ### User input values (with allowed min-max ranges)
        # rpm for all constant speed modes (single, multi, constant):
        self.rpmBox.setValue(10)    # default rpm
        # adjust slider position to match rpmBox value:
        self.rpmSlider.setValue(self.rpmBox.value())
        # initial calculation of pps:
        self.pps_calculator(self.rpmBox.value())
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
        self.rpmBox.valueChanged.connect(self.rpmBox_changed)
        # update rpm by slider movement:
        self.rpmSlider.valueChanged.connect(self.rpmSlider_changed)
        # Drive profile:
        self.driveprofile_pushB.clicked.connect(self.drive_profile)
        self.stopprofile_pushB.clicked.connect(self.stop_profile)



    ###   GRAPH WINDOW   ###
    
    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        line = self.graphWidget.plot(x, y, name=plotname, pen=pen)
        return line
    
    def graphwindow(self):
        # setup window and timer:
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        # setup data containers:
        self.x = [0] # time
        self.y1 = [self.pps_rpm_converter(self.motor.actual_velocity)]
        self.y2 = [self.pps_rpm_converter(self.module.pps)]
  
        # figure styling:
        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend()
        self.graphWidget.setLabel('left', 'velocity (rpm)')
        self.graphWidget.setLabel('bottom', 'time (s)')
        
        self.line1 = self.plot(self.x, self.y1, 'actual velocity', 'r')
        self.line2 = self.plot(self.x, self.y2, 'set velocity', 'b')
  
    def update_plot_data(self):
        # self.x = self.x[1:]  # Remove the first x element
        self.x.append(self.x[-1] + self.timer.interval() / 1000)  # add new value according to timer interval

        # self.y = self.y[1:]  # Remove the first
        self.y1.append(self.pps_rpm_converter(self.motor.actual_velocity))
        self.y2.append(self.pps_rpm_converter(self.module.pps))

        self.line1.setData(self.x, self.y1)  # Update the data.
        self.line2.setData(self.x, self.y2)  # Update the data.



    ###   CALCULATORS (for unit conversion)   ###
    
    def rpmSlider_changed(self):
        rpm = self.rpmSlider.value()
        self.rpmBox.setValue(rpm)
        self.pps_calculator(rpm)
        
    def rpmBox_changed(self):
        rpm = self.rpmBox.value()
        self.rpmSlider.setValue(rpm)
        self.pps_calculator(rpm)
    
    def pps_calculator(self, rpm_value):
        self.module.rpm = rpm_value
        self.module.pps = round(self.module.rpm * self.module.msteps_per_rev/60)
        
    def pps_rpm_converter(self, pps):
        rpm = pps / self.module.msteps_per_rev * 60
        return round(rpm)
            
        
    
    ###   MOTOR CONTROL FUNCTIONS   ###
    
    def stop_motor(self):
        '''Stop signal; can always be sent to the motors.'''
        self.motor.stop()
        # do not use time.sleep here!
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
        
    def drive_profile(self, profile):
        print('Driving profile...')
        self.drivetimer = QTimer()
        self.drivetimer.setInterval(100)
        self.motor.rotate(self.module.pps)
        self.drivetimer.timeout.connect(lambda: self.motor.rotate(self.module.pps))
        self.drivetimer.start()
        self.driveprofile_pushB.setEnabled(False)
        self.stopprofile_pushB.setEnabled(True)
        # print('Done!')
        
    def stop_profile(self):
        self.drivetimer.stop()
        self.stop_motor()
        self.driveprofile_pushB.setEnabled(True)
        self.stopprofile_pushB.setEnabled(False)

    

    ###   GENERAL GUI SETTINGS   ###
    
    def set_allowed_ranges(self):
        '''Specify allowed min-max ranges for values that can 
        be changed in the GUI. These should usually be fine...'''
        ### User input values (with allowed min-max ranges)
        # rpm for all constant speed modes (single, multi, constant):
        self.rpmBox.setMinimum(-120)
        self.rpmBox.setMaximum(120)
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
