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
        self.module = m # TODO: maybe change back to m in the entire file...
        self.motor = self.module.motor
        self.last_motor_command = None
        # setup functions:
        self.set_allowed_ranges()
        self.set_default_values()
        self.connectSignalsSlots()
        # ADC connection:
        self.chan_s1 = None
        self.chan_s3 = None
        self.adc_sigma1_scaling = 114.2
        self.adc_sigma3_scaling = 99 # TODO: add correct value here
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
        self.module.rpm = self.rpmBox.value()
        self.module.update_pps()
        # amount of single steps in multistep mode:
        self.multistep_numberBox.setValue(90)   # degrees
        # set ADC_box:
        self.initADC_s1.setChecked(False)
        self.initADC_s3.setChecked(False)
        self.invert_checkBox.setChecked(False)
        # set initial stress setpoint value:
        self.sigma1_SP_spinBox.setValue(0)
        self.dsigma_SP_spinBox.setValue(0)
        # set initial maxvel value:
        self.maxvel_spinBox.setValue(120)
        self.module.maxvel = self.maxvel_spinBox.value()

        
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
        # Multi step rotation:
        self.multi_down_Button.clicked.connect(self.multi_step_down)
        self.multi_up_Button.clicked.connect(self.multi_step_up)
        # Continuous rotation:
        self.perm_down_Button.clicked.connect(self.permanent_down)
        self.perm_up_Button.clicked.connect(self.permanent_up)
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
        self.quench_start_pushB.clicked.connect(self.quench_PID)
        self.stopprofile_pushB_2.clicked.connect(self.stop_profile)
        # start ADC connection:
        self.initADC_s1.stateChanged.connect(lambda: self.init_adc(self.initADC_s1, 's1'))
        self.initADC_s3.stateChanged.connect(lambda: self.init_adc(self.initADC_s3, 's3'))
        # refresh maxvel when value is changed:
        self.maxvel_spinBox.valueChanged.connect(self.maxvel_changed)



    ###   DATA MANAGEMENT   ###
    
    def init_data_containers(self):
        self.data_chunk_size = 99
        self.savecounter = 1 # != 0 because of initialization, etc.
        self.time = [0] # time
        self.t0 = time.time()
        self.act_vel = [self.pps_rpm_converter(abs(self.motor.actual_velocity) * -self.module.dir)]
        self.set_vel = [self.pps_rpm_converter(abs(self.module.pps) * -self.module.dir)]
        # self.SP = [self.setpointSlider.value()]
        self.sigma1_SP = [self.sigma1_SP_spinBox.value()]
        self.dsigma_SP = [self.dsigma_SP_spinBox.value()]
        if self.initADC_s1.isChecked() == True:
            self.sigma1_PV = [int(self.chan_s1.voltage/self.adc_sigma1_scaling)]
            # self.sigma3_PV = [int(self.chan_s3.voltage/self.adc_sigma3_scaling)]
            # self.PV = [self.procvarSlider.value()]
            if self.initADC_s3.isChecked() == True:
                self.sigma3_PV = [int(self.chan_s3.voltage/self.adc_sigma3_scaling)]
                self.dsigma_PV = [self.sigma1_PV[0] - self.sigma3_PV[0]]
            else:
                self.sigma3_PV = [0]
                self.dsigma_PV = [0]
        else:
            self.sigma1_PV = [0]
            self.sigma3_PV = [0]
            self.dsigma_PV = [0]
            # self.PV = [self.procvarSlider.value()]
        # self.CV = [0]
        # self.error = [0, 0, 0]
        self.error = [self.sigma1_SP[-1] - self.sigma1_PV[-1]]
        # print(self.time, self.act_vel, self.set_vel)
        self.init_save_files()
        
    def update_data(self):
        # add new values
        self.time.append(time.time()-self.t0)
        self.act_vel.append(self.pps_rpm_converter(abs(self.motor.actual_velocity) * -self.module.dir))
        self.set_vel.append(self.pps_rpm_converter(abs(self.module.pps) * -self.module.dir))
        # self.SP.append(self.setpointSlider.value())
        self.sigma1_SP.append(self.sigma1_SP_spinBox.value())
        self.dsigma_SP.append([]) # TODO
        if self.initADC_s1.isChecked() == True:
            self.sigma1_PV.append(int(self.chan_s1.voltage/self.adc_sigma1_scaling))
            # self.PV.append(self.procvarSlider.value())
        else:
            self.sigma1_PV.append(0)
            # self.PV.append(self.procvarSlider.value())
        # self.CV.append(self.CV[-1])
        self.error.append(self.sigma1_SP[-1] - self.sigma1_PV[-1])
        # print('times:', self.time[-1], time.time()-self.t0)
        # print('t:', round(self.time[-1], 2),
        #       '  CV:', self.set_vel[-1],
        #       '  SP:', self.SP[-1],
        #       '  PV:', self.PV[-1],
        #       '  e:', self.error[-1])
        
        # check counter:
        # print('counter:', self.savecounter)
        if self.savecounter == self.data_chunk_size:
            # self.save_values()
            self.savecounter = 0
        else:
            self.savecounter += 1
        # print('counter:', self.savecounter)
        
        # print('length:', len(self.time))
        if len(self.time) == self.data_chunk_size + 1:
            self.time.pop(0)       # remove the first elements
            self.act_vel.pop(0)
            self.set_vel.pop(0)
            self.sigma1_SP.pop(0)
            self.sigma1_PV.pop(0)
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
    
    def init_adc(self, checkbox, sigma):
        if self.checkbox.isChecked() == True: # TODO: this method might not work to remove the connection...
            import board
            import busio
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn
            # Create the I2C bus:
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Create the ADC object using the I2C bus:
            ads = ADS.ADS1115(i2c)
            
            # Create single-ended input on channel:
            if self.sigma == 's1':
                self.chan_s1 = AnalogIn(ads, ADS.P0)
                
            elif self.sigma == 's1':
                self.chan_s3 = AnalogIn(ads, ADS.P1)
            
            # Create differential input between channel 0 and 1:
            # currently not working since only one pin is connected
            # chan0 = AnalogIn(ads, ADS.P0, ADS.P1)
            
            # print header:
            # print("{:>5}\t{:>5}".format('raw', 'v'))
            
            # print first line of data:
            # print("{:>5}\t{:>5.3f}".format(self.channel.value, self.channel.voltage))
            
            # return self.chan_s1, self.chan_s3


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
        self.line2 = self.plot(self.time, self.set_vel, 'set velocity', 'b')
        self.line3 = self.plot(self.time, self.sigma1_SP, 'SP', 'c')
        self.line4 = self.plot(self.time, self.sigma1_PV, 'PV', 'g')
        self.line5 = self.plot(self.time, self.error, 'error', 'r')
        # LCDs:
        self.lcd_actvel.display(round(self.pps_rpm_converter(abs(self.motor.actual_velocity) * -self.module.dir)))
  
    def update_plot(self):
        # plot lines:
        self.line1.setData(self.time, self.act_vel)
        self.line2.setData(self.time, self.set_vel)
        self.line3.setData(self.time, self.sigma1_SP)
        self.line4.setData(self.time, self.sigma1_PV)
        self.line5.setData(self.time, self.error)
        # LCDs:
        self.lcd_actvel.display(round(self.pps_rpm_converter(abs(self.motor.actual_velocity) * -self.module.dir)))



    ###   CALCULATORS (for unit conversion)   ###
    
    def rpmSlider_changed(self):
        self.module.pps = self.rpmSlider.value()
        self.rpmBox.setValue(self.module.pps / self.module.msteps_per_rev * 60)
        
    def rpmBox_changed(self):
        self.module.rpm = self.rpmBox.value()
        self.module.update_pps()
        self.rpmSlider.setValue(-self.module.pps) # - to get positiv slider values
        
    def maxvel_changed(self):
        self.module.maxvel = self.maxvel_spinBox.value()
        
    def pps_calculator(self, rpm_value):
        self.module.rpm = rpm_value
        self.module.pps = int(round(self.module.rpm * self.module.msteps_per_rev/60))
        # print('pps_calculator', self.module.rpm, self.module.pps)
        
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
        if not self.last_motor_command == None:
            self.module.rpm = self.rpmBox.value()
            self.module.update_pps()
            self.last_motor_command()
        else:
            print('no command given yet...')
    
    def invert_direction(self):
        if self.invert_checkBox.isChecked() == True:
            self.module.dir_inv_mod = -1
        if self.invert_checkBox.isChecked() == False:
            self.module.dir_inv_mod = 1
        self.module.rpm = self.rpmBox.value()
        self.module.update_pps()
        # print(self.module.rpm, self.module.pps)
    
    def stop_motor(self):
        '''Stop signal; can always be sent to the motors.'''
        self.clear_button_colors()
        self.motor.stop()
        self.last_motor_command = self.stop_motor
        # do not use time.sleep here!
        # print status message
        print('Motor', self.module.moduleID, 'stopped!')
    
    def permanent_down(self):
        self.clear_button_colors()
        self.perm_down_Button.setStyleSheet("QPushButton {background-color: rgb(0, 255, 0);}")
        self.module.dir = -1
        self.module.update_pps()
        self.motor.rotate(self.module.pps) # positive pps -> clockwise
        self.last_motor_command = self.permanent_down
        print('Rotating down with', str(self.rpmBox.value()), 'rpm')
    
    def permanent_up(self):
        self.clear_button_colors()
        self.perm_up_Button.setStyleSheet("QPushButton {background-color: rgb(0, 255, 0);}")
        self.module.dir = 1
        self.module.update_pps()
        self.motor.rotate(self.module.pps)
        self.last_motor_command = self.permanent_up
        print('Rotating up with', str(self.rpmBox.value()), 'rpm')
     
    def multi_step_down(self):
        self.module.dir = -1
        self.multi_step()
        print('Coarse step down with Module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
   
    def multi_step_up(self):
        self.module.dir = 1
        self.multi_step()
        print('Coarse step up with Module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        
    def multi_step(self):
        # self.msteps = self.module.msteps_per_fstep * self.multistep_numberBox.value()
        self.msteps = int(round(self.module.msteps_per_rev * self.multistep_numberBox.value()/360))
        self.module.update_pps()
        # dir_inv_mod is needed because move_by does not take negative pps values
        self.motor.move_by(self.module.dir * self.msteps * self.module.dir_inv_mod, self.module.pps)

    
    def drive_profile(self, profile): # TODO: function not used anymore...
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
        interval = 1000
        self.drivetimer = QTimer()
        self.drivetimer.setInterval(interval)
                
        # init controller instance:
        c = Controller(interval/1000, 0.5, 0.1, 0.5, True) # /1000 for ms->s; good?
        # c = Controller(interval/1000, 1, 0.1, 0.0, True)
        
        def on_timeout():
            c.controller_update(self.sigma1_SP_spinBox.value(),
                                        # self.procvarSlider.value(),
                                        self.chan_s1.value/self.adc_sigma1_scaling,
                                        self.pps_rpm_converter(abs(self.motor.actual_velocity)),
                                        self.module.maxvel)
            self.module.rpm = c.output
            self.module.update_pps()
            # self.CV.append(int(c.output))
            self.motor.rotate(self.module.pps)
            
        self.drivetimer.timeout.connect(on_timeout)
        
        self.drivetimer.start()
        self.driveprofile_pushB.setEnabled(False)
        self.stopprofile_pushB.setEnabled(True)
    
    def quench_PID(self):
        interval = 1000
        self.drivetimer = QTimer()
        self.drivetimer.setInterval(interval)
                
        # init controller instance:
        c = Controller(interval/1000, 0.5, 0.1, 0.5, True) # /1000 for ms->s; good?
        # c = Controller(interval/1000, 1, 0.1, 0.0, True)
        
        def on_timeout():
            SP = self.dsigma_SP_spinBox.value()
            PV = self.chan_s1.value/self.adc_sigma1_scaling - self.chan_s3.value/self.adc_sigma3_scaling
            c.controller_update(SP, PV,
                                self.pps_rpm_converter(abs(self.motor.actual_velocity)),
                                self.module.maxvel)
            self.module.rpm = c.output
            self.module.update_pps()
            # self.CV.append(int(c.output))
            self.motor.rotate(- self.module.pps) # TODO: correct to set this negative?
            
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
        # set maxvel spinBox:
        self.maxvel_spinBox.setMinimum(0)
        self.maxvel_spinBox.setMaximum(180)
        
    def clear_button_colors(self):
        self.perm_down_Button.setStyleSheet("")
        self.perm_up_Button.setStyleSheet("")
        
        

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
