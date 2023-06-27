#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:08:43 2023

@author: pgross
"""

import sys
import time

from PyQt5.QtWidgets import (QMainWindow, QApplication)
from PyQt5.QtCore import QTimer

from pytrinamic.connections import ConnectionManager

# import time

from modules.gui.main_window_ui import Ui_MainWindow
from .Motor import Motor
from .Controller import Controller 


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
        self.last_motor_command = None
        # setup functions:
        self.set_allowed_ranges()
        self.set_default_values()
        self.connectSignalsSlots()
        # ADC connection:
        self.chan0 = None#self.init_adc()
        # data containers:
        self.init_data_containers()
        # graphing window:
        self.init_graphwindow()
        # timers:
        self.set_timers()

        self.show()
        
    def set_default_values(self):
        '''User input: Specify default values here.'''
        ### User input values (with allowed min-max ranges)
        # rpm for all constant speed modes (single, multi, constant):
        self.rpmBox.setValue(10)    # default rpm
        # adjust slider position to match rpmBox value:
        self.rpmSlider.setValue(int(round(self.rpmBox.value() * self.module.msteps_per_rev/60)))
        # initial calculation of pps:
        self.pps_calculator(self.rpmBox.value())
        # amount of single steps in multistep mode:
        self.multistep_numberBox.setValue(90)   # degrees
        # set ADC_box:
        self.initADC_box.setChecked(False)

        
    def set_timers(self):
        self.basetimer = 100 # in ms
        # data timer:
        self.datatimer = QTimer()
        self.data_timerfactor = 1
        self.datatimer.setInterval(self.basetimer * self.data_timerfactor)
        self.datatimer.timeout.connect(self.update_data)
        self.datatimer.start()
        # graphing timer:
        self.graphtimer = QTimer()
        self.graph_timerfactor = 1
        self.graphtimer.setInterval(self.basetimer * self.graph_timerfactor)
        self.graphtimer.timeout.connect(self.update_plot)
        self.graphtimer.start()
        
        
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
        # direction inversion:
        self.invert_checkBox.stateChanged.connect(self.invert_direction)
        # update velocity button:
        self.update_rpm_button.clicked.connect(self.update_rpm)
        ### PID:
        # self.driveprofile_pushB.clicked.connect(self.drive_profile)
        self.driveprofile_pushB.clicked.connect(self.drive_PID)
        self.stopprofile_pushB.clicked.connect(self.stop_profile)
        # start ADC connection:
        self.initADC_box.stateChanged.connect(self.init_adc)



    ###   DATA MANAGEMENT   ###
    
    def init_data_containers(self):
        self.data_chunk_size = 99
        self.savecounter = 1 # != 0 because of initialization, etc.
        self.time = [0] # time
        self.t0 = time.time()
        self.act_vel = [self.pps_rpm_converter(self.motor.actual_velocity)]
        self.set_vel = [self.pps_rpm_converter(self.module.pps)]
        self.SP = [self.setpointSlider.value()]
        if self.initADC_box.isChecked() == True:
            # self.PV = [int(self.chan0.voltage/3.3 * 240 - 120)]
            self.PV = [self.procvarSlider.value()]
        else:
            # self.PV = [0]
            self.PV = [self.procvarSlider.value()]
        # self.CV = [0]
        # self.error = [0, 0, 0]
        self.error = [self.SP[-1] - self.PV[-1]]
        # print(self.time, self.act_vel, self.set_vel)
        self.init_save_files()
        
    def update_data(self):
        # add new values
        self.time.append(time.time()-self.t0)
        self.act_vel.append(self.pps_rpm_converter(self.motor.actual_velocity))
        self.set_vel.append(self.pps_rpm_converter(self.module.pps))
        self.SP.append(self.setpointSlider.value())
        if self.initADC_box.isChecked() == True:
            # self.PV.append(int(self.chan0.voltage/3.3 * 240 - 120))
            self.PV.append(self.procvarSlider.value())
        else:
            # self.PV.append(0)
            self.PV.append(self.procvarSlider.value())
        # self.CV.append(self.CV[-1])
        self.error.append(self.SP[-1] - self.PV[-1])
        # print('times:', self.time[-1], time.time()-self.t0)
        # print('t:', round(self.time[-1], 2),
        #       '  CV:', self.set_vel[-1],
        #       '  SP:', self.SP[-1],
        #       '  PV:', self.PV[-1],
        #       '  e:', self.error[-1])
        
        # check counter:
        # print('counter:', self.savecounter)
        if self.savecounter == self.data_chunk_size:
            self.save_values()
            self.savecounter = 0
        else:
            self.savecounter += 1
        # print('counter:', self.savecounter)
        
        # print('length:', len(self.time))
        if len(self.time) == self.data_chunk_size + 1:
            self.time.pop(0)       # remove the first elements
            self.act_vel.pop(0)
            self.set_vel.pop(0)
            self.SP.pop(0)
            self.PV.pop(0)
            self.error.pop(0)
            # self.CV.pop(0)
        # print('length:', len(self.time))
            
    def init_save_files(self):
        '''Clears files for next run.'''
        print('overwrite save files')
        with open('act_vel.txt', 'w') as f:
            f.write('')
        with open('time.txt', 'w') as f:
            f.write('')
        
    def save_values(self):
        '''Saves values to external files.'''
        with open('act_vel.txt', 'a') as f:
            for elem in self.act_vel:
                f.write("%s " % int(elem))
                f.write("\n")
        with open('time.txt', 'a') as f:
            for elem in self.time:
                f.write("%s " % round(elem,3))
                f.write("\n")
        print('Saved all positions to file!')
        
    
    
    ###   Breakout board and ADC   ###
    """
    prerequisites: https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/linux
        1. install and configure libusb: 
        2. verify that pyftdi and blinka are installed
        3. in case of a langid error, correct the permission settings: "sudo adduser $USER plugdev"
            see also: https://eblot.github.io/pyftdi/installation.html
        4. re-plug the device and re-login to a new session!
    """
    
    def init_adc(self):
        if self.initADC_box.isChecked() == True:
            import board
            import busio
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn
            # Create the I2C bus:
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Create the ADC object using the I2C bus:
            ads = ADS.ADS1115(i2c)
            
            # Create single-ended input on channel 1:
            chan0 = AnalogIn(ads, ADS.P1)
            
            # Create differential input between channel 0 and 1:
            # currently not working since only one pin is connected
            # chan0 = AnalogIn(ads, ADS.P0, ADS.P1)
            
            # print header:
            print("{:>5}\t{:>5}".format('raw', 'v'))
            
            # print first line of data:
            print("{:>5}\t{:>5.3f}".format(chan0.value, chan0.voltage))
            
            return chan0


    ###   GRAPH WINDOW   ###
    
    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        line = self.graphWidget.plot(x, y, name=plotname, pen=pen)
        return line
    
    def init_graphwindow(self):
        # figure styling:
        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend()
        self.graphWidget.setLabel('left', 'velocity (rpm)')
        self.graphWidget.setLabel('bottom', 'time (s)')
        self.line1 = self.plot(self.time, self.act_vel, 'actual velocity', 'k')
        # self.line2 = self.plot(self.time, self.set_vel, 'set velocity', 'b')
        self.line3 = self.plot(self.time, self.SP, 'SP', 'c')
        self.line4 = self.plot(self.time, self.PV, 'PV', 'g')
        self.line5 = self.plot(self.time, self.error, 'error', 'r')
  
    def update_plot(self):
        self.line1.setData(self.time, self.act_vel)
        # self.line2.setData(self.time, self.set_vel)
        self.line3.setData(self.time, self.SP)
        self.line4.setData(self.time, self.PV)
        self.line5.setData(self.time, self.error)



    ###   CALCULATORS (for unit conversion)   ###
    
    def rpmSlider_changed(self):
        self.module.pps = self.rpmSlider.value()
        self.rpmBox.setValue(self.module.pps / self.module.msteps_per_rev * 60)
        
    def rpmBox_changed(self):
        self.pps_calculator(self.rpmBox.value())
        self.rpmSlider.setValue(self.module.pps)
    
    def pps_calculator(self, rpm_value):
        self.module.rpm = rpm_value
        self.module.pps = int(round(self.module.rpm * self.module.msteps_per_rev/60))
        
    def rpm_pps_converter(self, rpm):
        pps = rpm * self.module.msteps_per_rev / 60
        return pps
        
    def pps_rpm_converter(self, pps):
        rpm = pps / self.module.msteps_per_rev * 60
        return round(rpm, 4)
    
 
    
    ###   MOTOR CONTROL FUNCTIONS   ###
    
    def update_rpm(self):
        '''This function first updates the module pps value from the rpmBox value
        and then executes the last command send to the motor, which is stored
        explicitly in a variable when the respective functions are called.'''
        self.module.update_pps(self.rpmBox.value())
        self.last_motor_command()
    
    def invert_direction(self):
        if self.invert_checkBox.isChecked() == True:
            self.module.dir_inv_mod = -1
        if self.invert_checkBox.isChecked() == False:
            self.module.dir_inv_mod = 1
        self.module.update_pps(self.rpmBox.value())
        # print(self.module.rpm, self.module.pps)
    
    def stop_motor(self):
        '''Stop signal; can always be sent to the motors.'''
        self.clear_button_colors()
        self.motor.stop()
        self.last_motor_command = self.stop_motor
        # do not use time.sleep here!
        # print status message
        print('Motor', self.module.moduleID, 'stopped!')
    
    def permanent_left(self):
        self.clear_button_colors()
        self.contlButton.setStyleSheet("QPushButton {background-color: rgb(0, 255, 0);}")
        self.motor.rotate(-self.module.pps)
        self.last_motor_command = self.permanent_left
        print('Rotating left with', str(self.rpmBox.value()), 'rpm')
    
    def permanent_right(self):
        self.clear_button_colors()
        self.contrButton.setStyleSheet("QPushButton {background-color: rgb(0, 255, 0);}")
        self.motor.rotate(self.module.pps)
        self.last_motor_command = self.permanent_right
        print('Rotating right with', str(self.rpmBox.value()), 'rpm')
            
    def fine_step_left(self):
        self.msteps = self.module.msteps_per_fstep
        # dir_inv_mod is needed because move_by does not take negative pps values
        self.motor.move_by(-self.msteps * self.module.dir_inv_mod, self.module.pps)
        # self.last_motor_command = self.fine_step_left
        print('Fine step left with Module', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        
    def coarse_step_left(self):
        # self.msteps = self.module.msteps_per_fstep * self.multistep_numberBox.value()
        self.msteps = int(round(self.module.msteps_per_rev * self.multistep_numberBox.value()/360))
        # dir_inv_mod is needed because move_by does not take negative pps values
        self.motor.move_by(-self.msteps * self.module.dir_inv_mod, self.module.pps)
        # self.last_motor_command = self.coarse_step_left
        print('Coarse step left with Module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        
    def fine_step_right(self):
        self.msteps = self.module.msteps_per_fstep
        # dir_inv_mod is needed because move_by does not take negative pps values
        self.motor.move_by(self.msteps * self.module.dir_inv_mod, self.module.pps)
        # self.last_motor_command = self.fine_step_right
        print('Fine step right with Module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        
    def coarse_step_right(self):
        # self.msteps = self.module.msteps_per_fstep * self.multistep_numberBox.value()
        self.msteps = int(round(self.module.msteps_per_rev * self.multistep_numberBox.value()/360))
        # dir_inv_mod is needed because move_by does not take negative pps values
        self.motor.move_by(self.msteps * self.module.dir_inv_mod, self.module.pps)
        # self.last_motor_command = self.coarse_step_right
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
        
    def drive_PID(self):
        interval = 500
        self.drivetimer = QTimer()
        self.drivetimer.setInterval(interval)
                
        # c = Controller(interval/1000, 1, 0.0, 0.0, True) # /1000 for ms->s; good?
        c = Controller(interval/1000, 1, 0.3, 0.0, True)
        
        def on_timeout():
            c.controller_update(self.setpointSlider.value(),
                                        self.procvarSlider.value(),
                                        # int(self.chan0.voltage/3.3 * 240 - 120),
                                        self.pps_rpm_converter(self.motor.actual_velocity))
            self.pps_calculator(int(c.output))
            # print('pps:', self.module.pps)
            # self.CV.append(int(c.output))
            self.motor.rotate(self.module.pps)
            
        self.drivetimer.timeout.connect(on_timeout)
        
        self.drivetimer.start()
        self.driveprofile_pushB.setEnabled(False)
        self.stopprofile_pushB.setEnabled(True)
        
    def stop_profile(self):
        if hasattr(self, 'drivetimer'):
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
        self.rpmBox.setMinimum(0)
        self.rpmBox.setMaximum(120)
        # set slider limits and position
        self.rpmSlider.setMinimum(int(round(self.rpmBox.minimum() * self.module.msteps_per_rev / 60)))
        self.rpmSlider.setMaximum(int(round(self.rpmBox.maximum() * self.module.msteps_per_rev / 60)))
        # amount of single steps in multistep mode:
        self.multistep_numberBox.setMinimum(0)
        self.multistep_numberBox.setMaximum(360)
        
    def clear_button_colors(self):
        self.contlButton.setStyleSheet("")
        self.contrButton.setStyleSheet("")
        
        

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
