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

import pandas as pd 


# import time

from modules.gui.main_window_Test import Ui_MainWindow #TODO
from .Motor import Motor
from .Controller import Controller 


'''
The following must be installed! 
Also, QWidget must be promoted to plotWidget in QtDesigner! See here:
https://www.pythonguis.com/tutorials/embed-pyqtgraph-custom-widgets-qt-app/'''
import pyqtgraph as pg

# from random import randint
port_list = ConnectionManager().list_connections()
for port in port_list:
    Motor(port)

ID_list = [23, 14]
module_list = Motor.sort_module_list(ID_list) 

s1 = module_list[0]
s3 = module_list[1]

# print out Id to find out if module instances got mapped to right ID
print('motor_s1:',s1.moduleID)
print('motor_s3:',s3.moduleID)


class Window(QMainWindow, Ui_MainWindow):
    '''This custom class inherits from QMainWindow class and the custom 
    Ui_MainWindow class from main_window_ui.py file. That file is created 
    from main_window.ui using the pyuic5 command line program, e.g.:
    pyuic5 -x main_window.ui -o main_window_ui.py
    '''
    
    @staticmethod
    def first(bool1, bool2):
        if bool1 and not bool2:
            return True 
        else: 
            return False 
        
    @staticmethod
    def second(bool1, bool2):
        if bool2 and not bool1:
            return True 
        else:
            return False 
        
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('motor_s1 Control Panel -- MoCoPa')
        # implement motors in correct syntax:
        self.module_s1 = s1
        self.module_s3 = s3
        self.motor_s1 = self.module_s1.motor
        self.motor_s3 = self.module_s3.motor  #TODO adapted to s3 compatibility!!
        # choose active motor for initialisation:
        self.active_modules = [self.module_s1]
        # self.active_modules = [self.module_s3]
        # self.active_modules = []
        # for motor s1:
        self.last_motor_command = None
        # PID
        self.PID_max_vel_scale = 1  # TODO: what is this?
        # setup functions:
        self.set_allowed_ranges()
        self.set_default_values()
        self.connectSignalsSlots()
        # ADC connection:
        self.chan_s1 = None
        self.chan_s3 = None
        self.adc_sigma1_scaling = 3.578 # TODO: note: scaling-factor to MPa!
        self.adc_sigma3_scaling = 12.364 
        # data containers:
        self.init_data_containers()
        # graphing window:
        self.init_graphwindow()
        # timers:
        self.set_timers()
        # show window 
        self.show()
        # error threshold for closed valve
        self.threshold_valve = 0
        # error threshold for oilp-change
        self.threshold_oilp = 0.5
        # import positions for quenching 
        self.positions = pd.read_csv(
        'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/position_quenched.csv')
        # self.positions = pd.read_csv(
        # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv') 
        self.positions.columns = self.positions.columns.str.strip()
        if self.motor_s3.actual_position != int(self.positions.loc[0, 'current']):
            self.positions['opened'] = self.positions['opened']-self.positions['current']
            self.positions['closed'] = self.positions['closed']-self.positions['current']
            self.positions.to_csv(
            'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/position_quenched.csv', index=False)
            # self.positions.to_csv(
            # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index=False) 
        self.motor_s3.max_pos_up = int(self.positions.loc[0, 'opened'])
        self.motor_s3.max_pos_down = int(self.positions.loc[0, 'closed'])
        # print('current', int(self.positions['current'][0]),'actual',self.motor_s3.actual_position, 
        #       'up',self.motor_s3.max_pos_up, 'down', self.motor_s3.max_pos_down)
        # print info if valve is not closed at experiment start 
        self.close_valve()
        
        
    def set_default_values(self):
        '''User input: Specify default values here.'''
        ### User input values (with allowed min-max ranges)
        # rpm for all constant speed modes (single, multi, constant):
        self.rpmBox.setValue(10)    # default rpm
        # adjust slider position to match rpmBox value:
        self.rpmSlider.setValue(int(round(self.rpmBox.value() * self.module_s1.msteps_per_rev/60)))
        # initial calculation of pps:
        self.module_s1.rpm = self.rpmBox.value()
        self.module_s3.rpm = self.rpmBox.value()
        self.module_s1.update_pps()
        self.module_s3.update_pps()
        # set ADC_box:
        self.initADC_s1.setChecked(False)
        self.initADC_s3.setChecked(False)
        self.invert_checkBox.setChecked(False)
        # set initial stress setpoint value:
        self.sigma1_SP_spinBox.setValue(0)
        self.dsigma_SP_spinBox.setValue(0)
        # set initial maxvel value:
        self.maxvel_spinBox.setValue(120)
        self.module_s1.maxvel = self.maxvel_spinBox.value()
        self.module_s3.maxvel = self.maxvel_spinBox.value()
        
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
        self.quitButton.clicked.connect(self.close_app)
        # check which motors are active:
        self.checkB_motor_s1.stateChanged.connect(lambda: self.refresh_module_list(self.module_s1))
        self.checkB_motor_s3.stateChanged.connect(lambda: self.refresh_module_list(self.module_s3))
        # Multi step rotation:
        self.multi_down_Button.clicked.connect(lambda: self.multi_module_control(self.multi_step_down))
        self.multi_up_Button.clicked.connect(lambda: self.multi_module_control(self.multi_step_up))
        # Continuous rotation:
        self.perm_down_Button.clicked.connect(lambda: self.multi_module_control(self.permanent_down))
        self.perm_up_Button.clicked.connect(lambda: self.multi_module_control(self.permanent_up))
        # Stop button:
        self.stopButton.clicked.connect(lambda: self.multi_module_control(self.stop_motor))
        # refresh rpm when value is changed:
        self.rpmBox.valueChanged.connect(lambda: self.multi_module_control(self.rpmBox_changed))
        # update rpm by slider movement:
        self.rpmSlider.valueChanged.connect(lambda: self.multi_module_control(self.rpmSlider_changed))
        # direction inversion:
        self.invert_checkBox.stateChanged.connect(lambda: self.multi_module_control(self.invert_direction))
        # update velocity button:
        self.update_rpm_button.clicked.connect(lambda: self.multi_module_control(self.update_rpm))
        ### PID:
        self.driveprofile_pushB.clicked.connect(self.drive_PID)
        self.stopprofile_pushB.clicked.connect(self.stop_profile)
        self.pushB_update_const.clicked.connect(lambda: self.update_PID('const'))
        
        self.quench_start_pushB.clicked.connect(self.quench_PID)
        self.stopprofile_pushB_2.clicked.connect(self.stop_profile)
        self.pushB_update_quench.clicked.connect(lambda: self.update_PID('quench'))
        # start ADC connection:
        self.initADC_s1.stateChanged.connect(lambda: self.init_adc(self.initADC_s1, 's1'))
        self.initADC_s3.stateChanged.connect(lambda: self.init_adc(self.initADC_s3, 's3'))
        # refresh maxvel when value is changed:
        # self.maxvel_spinBox.valueChanged.connect(self.maxvel_changed)
        # close oil-valve at beginning 
        self.pushB_close_valve.clicked.connect(lambda: self.goto_s3(self.motor_s3.max_pos_down, 
                                                                    self.rpmBox_prequench.value()))
        
    def close_valve(self):
        if abs(self.motor_s3.max_pos_down - self.motor_s3.actual_position) > self.threshold_valve:
            self.pushB_close_valve.setStyleSheet('color: red')
            print('Warning: oil valve is not closed all the way!',
                  f'Motor is off by = {abs(self.motor_s3.max_pos_down - self.motor_s3.actual_position)} steps',  
                  ' press "close oil valve"-button to close it!')
        else: 
            self.pushB_close_valve.setStyleSheet('color: green')
            print('s3 motor valve closed. Motor is off by',
                  f' = {abs(self.motor_s3.max_pos_down - self.motor_s3.actual_position)} steps')

    ###   DATA MANAGEMENT   ###
    
    def init_data_containers(self):
        self.data_chunk_size = 99
        self.savecounter = 1 # != 0 because of initialization, etc.
        self.time = [0] # time
        self.t0 = time.time()
        self.act_vel_s3 = [self.pps_rpm_converter(self.module_s3, abs(self.motor_s3.actual_velocity))]
        self.act_vel_s1 = [self.pps_rpm_converter(self.module_s1, abs(self.motor_s1.actual_velocity))]
        self.set_vel = [self.pps_rpm_converter(self.module_s1, self.module_s1.pps)]
        # self.SP = [self.setpointSlider.value()]
        self.sigma1_SP = [self.sigma1_SP_spinBox.value()]
        self.dsigma_SP = [self.dsigma_SP_spinBox.value()]
        if self.initADC_s1.isChecked() == True:
            self.sigma1_PV = [int(self.chan_s1.value/self.adc_sigma1_scaling)]
            # self.PV = [self.procvarSlider.value()]
            if self.initADC_s3.isChecked() == True:
                self.sigma3_PV = [int(self.chan_s3.value/self.adc_sigma3_scaling)]
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
        self.act_vel_s3.append(self.pps_rpm_converter(self.module_s3, abs(self.motor_s3.actual_velocity)))
        self.act_vel_s1.append(self.pps_rpm_converter(self.module_s1, abs(self.motor_s1.actual_velocity)))
        self.set_vel.append(self.pps_rpm_converter(self.module_s1, abs(self.module_s1.pps)))
        # self.SP.append(self.setpointSlider.value())
        self.sigma1_SP.append(self.sigma1_SP_spinBox.value())
        self.dsigma_SP.append(self.dsigma_SP_spinBox.value())
        if self.initADC_s1.isChecked() == True:
            self.sigma1_PV.append(int(self.chan_s1.voltage/self.adc_sigma1_scaling))
            # self.PV.append(self.procvarSlider.value())
            if self.initADC_s3.isChecked() == True:
                self.dsigma_PV.append(self.chan_s1.value/self.adc_sigma1_scaling - self.chan_s3.value/self.adc_sigma3_scaling)
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
            # self.save_values() # uncomment this function if you want to save values continuously to a file
            self.savecounter = 0
        else:
            self.savecounter += 1
        # print('counter:', self.savecounter)
        
        # print('length:', len(self.time))
        if len(self.time) == self.data_chunk_size + 1:
            self.time.pop(0)       # remove the first elements
            self.act_vel_s3.pop(0)
            self.act_vel_s1.pop(0)
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
        if checkbox.isChecked() == True: # TODO: this method might not work to remove the connection...
            import board
            import busio
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn
            # Create the I2C bus:
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Create the ADC object using the I2C bus:
            ads = ADS.ADS1115(i2c)
            print(ads)
            
            # Create single-ended input on channel:
            if sigma == 's1':
                self.chan_s1 = AnalogIn(ads, ADS.P0)
                channel = self.chan_s1
                
            elif sigma == 's3':
                self.chan_s3 = AnalogIn(ads, ADS.P1)
                channel = self.chan_s3
            
            # Create differential input between channel 0 and 1:
            # currently not working since only one pin is connected
            # chan0 = AnalogIn(ads, ADS.P0, ADS.P1)
            
            # print header:
            # print("{:>5}\t{:>5}".format('raw', 'v'))
            
            # print first line of data:
            print("{:>5}\t{:>5.3f}".format(channel.value, channel.voltage))
            
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
        # s1/PID
        self.line1 = self.plot(self.time, self.act_vel_s1, 'actual velocity s1', 'k')
        self.line2 = self.plot(self.time, self.set_vel, 'set velocity', 'b')
        self.line3 = self.plot(self.time, self.sigma1_SP, 'SP', 'c')
        self.line4 = self.plot(self.time, self.sigma1_PV, 'PV', 'g')
        self.line5 = self.plot(self.time, self.error, 'error', 'r')
        # s3
        self.line6 = self.plot(self.time, self.act_vel_s3, 'actual velocity s3', 'y') 
        # LCDs:
        self.lcd_actvel_s1.display(round(self.pps_rpm_converter(self.module_s1, abs(self.motor_s1.actual_velocity))))
        self.lcd_actvel_s3.display(round(self.pps_rpm_converter(self.module_s3, abs(self.motor_s3.actual_velocity))))

        
    def update_plot(self):
        # plot lines:
        self.line1.setData(self.time, self.act_vel_s1)
        self.line2.setData(self.time, self.set_vel)
        self.line3.setData(self.time, self.sigma1_SP)
        self.line4.setData(self.time, self.sigma1_PV)
        self.line5.setData(self.time, self.error)
        self.line6.setData(self.time, self.act_vel_s3)
        # LCDs:
        self.lcd_actvel_s1.display(round(self.pps_rpm_converter(self.module_s1, abs(self.motor_s1.actual_velocity))))
        self.lcd_actvel_s3.display(round(self.pps_rpm_converter(self.module_s3, abs(self.motor_s3.actual_velocity))))

        
    ###   CALCULATORS (for unit conversion)   ###
    
    def rpmSlider_changed(self):
        self.module.pps = self.rpmSlider.value()
        self.rpmBox.setValue(self.module.pps / self.module.msteps_per_rev * 60)
        
    def rpmBox_changed(self):
        self.module.rpm = self.rpmBox.value()
        self.module.update_pps()
        self.rpmSlider.setValue(abs(self.module.pps)) # - to get positiv slider values
        
    # def update_maxvel(self):
    #     self.module_s1.maxvel = self.maxvel_spinBox.value()
    
    def pps_rpm_converter(self, module, pps):
        rpm = pps / module.msteps_per_rev * 60 
        return round(rpm, 4)
        
    # def pps_calculator(self, rpm_value):
    #     self.module_s1.rpm = rpm_value
    #     self.module_s1.pps = int(round(self.module_s1.rpm * self.module_s1.msteps_per_rev/60))
    #     # print('pps_calculator', self.module_s1.rpm, self.module_s1.pps)
        
    # def rpm_pps_converter(self, rpm):
    #     pps = rpm * self.module_s1.msteps_per_rev / 60
    #     return pps
    
      
    def crash_safety(self, module, steps): 
    # check if there are position bounds for this motor and prevent going to far 
        # check if there is no bounds 
        self.motor = self.module.motor
        if (self.motor.max_pos_down is None and self.motor.max_pos_up is None):
            self.motor.up_enabled = True 
            self.motor.down_enabled = True
        # check if there is lower bound, no upper bound 
        # elif Window.first(self.motor.max_pos_up is not None, self.motor.max_pos_down is not None):
        #     if (self.motor.actual_position + steps*self.module.dir) < self.motor.max_pos_up:
        #         self.motor.up_enabled = True 
        #     else: 
        #         self.motor.up_enabled = False
        # # check if there is upper bound, no lower bound
        # elif Window.second(self.motor.max_pos_up is not None, self.motor.max_pos_down is not None):
        #     if (self.motor.actual_position + steps*self.module.dir) > self.motor.max_pos_down:
        #         self.motor.down_enabled = True 
        #     else: 
        #         self.motor.down_enabled = False
        # check if there is upper and lower bound
        elif (self.motor.max_pos_up is not None and self.motor.max_pos_down is not None):
            if (self.motor.actual_position + steps*self.module.dir) < self.motor.max_pos_up:
                self.motor.up_enabled = True 
            else: 
                self.motor.up_enabled = False
            if (self.motor.actual_position + steps*self.module.dir) > self.motor.max_pos_down:
                self.motor.down_enabled = True 
            else: 
                self.motor.down_enabled = False  
        
    def refresh_module_list(self, module):
        self.active_modules = []
        if Window.first(self.checkB_motor_s1.isChecked(), self.checkB_motor_s3.isChecked()):
            self.active_modules.append(self.module_s1)
        elif Window.second(self.checkB_motor_s1.isChecked(), self.checkB_motor_s3.isChecked()):
            self.active_modules.append(self.module_s3)
        elif self.checkB_motor_s1.isChecked() and self.checkB_motor_s3.isChecked():
            self.active_modules = [self.module_s1, self.module_s3]
        else:
            print('no motor is active!')
        for module in self.active_modules:
            print('module:', module.moduleID, 'selected.')
        
        
    def multi_module_control(self, action):
        '''Add multi motor control capability. Argument "action" is one of
        the motor control functions below (e.g., single_step).'''
        # iterate over all active modules and apply the action function:
        for module in self.active_modules:
            # Prevent blocking of the application by the while loop:
            QApplication.processEvents()
            # set module and motor: IS THIS NEEDED?
            self.module = module
            self.motor = module.motor
            action()
            if self.motor == self.motor_s3:
                while module.motor.get_actual_velocity() != 0:
                    # Prevent blocking of the application by the while loop:
                    QApplication.processEvents()
                    print('acutal position:', module.motor.actual_position)
                    if abs(module.motor.actual_position - self.motor_s3.max_pos_down) > self.threshold_valve:
                        self.pushB_close_valve.setStyleSheet('color: red')
                    else:
                        self.pushB_close_valve.setStyleSheet('color: green')
                self.positions.loc[0, 'current'] = module.motor.actual_position 
                self.positions.to_csv(
                'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/position_quenched.csv', index = False)
                # self.positions.to_csv(
                # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index = False) 
         
    
    ###   MOTOR CONTROL FUNCTIONS   ###
    
    def update_rpm(self):
        '''This function first updates the module_s1 pps value from the rpmBox value
        and then executes the last command send to the motor_s1, which is stored
        explicitly in a variable when the respective functions are called.'''
        if self.module == self.module_s1:
            if not self.last_motor_command == None:
                self.module_s1.rpm = self.rpmBox.value()
                self.module_s1.update_pps()
                self.last_motor_command()
            else:
                print('no command given yet...')
        elif self.module == self.module_s3:
            self.module_s3.rpm = self.rpmBox.value()
            self.module_s3.update_pps()
            
    def update_PID(self, params):  ###TODO: update for PID arguments 
        if params == 'const':
            self.SP = self.sigma1_SP_spinBox.value()
            self.module_s1.maxvel = self.maxvel_spinBox.value()
            print('updated parameters for constant stress mode')
        elif params == 'quench':
            self.prequench_rpm = self.rpmBox_prequench.value()
            self.quench_rpm = self.rpmBox_quench.value()
            self.SP = self.dsigma_SP_spinBox.value()
            # self.SP_correction = 0
            print('updated parameters for quenching mode')

            
    def invert_direction(self):
        if self.invert_checkBox.isChecked() == True:
            self.module.dir_inv_mod = -1
        if self.invert_checkBox.isChecked() == False:
            self.module.dir_inv_mod = 1
        self.module.rpm = self.rpmBox.value()
        self.module.update_pps()
        print('dir for module:', self.module.moduleID, 'inverted!')
        # print(self.module_s1.rpm, self.module_s1.pps)
    
    def stop_motor(self):
        '''Stop signal to all motors; can always be sent to the motors.'''
        self.module.motor.stop()
        # ensure that the motors actually have time to slow down and stop:
        time.sleep(0.2)
        # # set target_position to actual_position for the multi_control loop:
        act_pos = self.module.motor.get_axis_parameter(self.module.motor.AP.ActualPosition)
        self.module.motor.set_axis_parameter(self.module.motor.AP.TargetPosition, act_pos)
        # # targ_pos = self.module.motor.get_axis_parameter(self.module.motor.AP.TargetPosition)
        # # print('debug: stop', self.module.moduleID, act_pos, targ_pos) # debug message
        print('Motor', self.module.moduleID, 'stopped!')

    
    def permanent_down(self):
        self.module.dir = -1
        self.module.update_pps()
        # check if with this velocity, motor will hit lower bound of motor within <= 3s 
        # if so set enabled down to False to prevent crash
        self.crash_safety(self.module, self.module.pps*3)
        if self.module.motor.down_enabled:
            self.clear_button_colors()
            self.perm_down_Button.setStyleSheet("QPushButton {background-color: rgb(0, 255, 0);}")
            self.motor.rotate(self.module.pps) # positive pps -> clockwise
            self.last_motor_command = self.permanent_down
            print('Rotating down with', str(self.rpmBox.value()), 'rpm')
        else: 
            print(f'Error: module {self.module.moduleID} will exceed max. down position!')
    
    def permanent_up(self):
        self.module.dir = 1
        self.module.update_pps()
        # check if with this velocity, motor will hit upper bound of motor within <= 3s 
        # if so set enabled up to False to prevent crash
        self.crash_safety(self.module, self.module.pps*3)
        if self.module.motor.up_enabled:
            self.clear_button_colors()
            self.perm_up_Button.setStyleSheet("QPushButton {background-color: rgb(0, 255, 0);}")
            self.motor.rotate(self.module.pps)
            self.last_motor_s1_command = self.permanent_up
            print('Rotating up with', str(self.rpmBox.value()), 'rpm')
        else: 
            print(f'Error: module {self.module.moduleID} will exceed max. up position!')
     
    def multi_step_down(self):
        self.module.dir = -1
        self.msteps = int(round(self.module.msteps_per_rev * self.multistep_numberBox.value()/360))
        self.module.update_pps()
        # check if actual_pos + steps < lower bound  
        # if so set enabled down to False to prevent crash
        self.crash_safety(self.module, self.msteps)
        if self.module.motor.down_enabled:
            self.motor.move_by(self.module.dir * self.msteps * self.module.dir_inv_mod, self.module.pps)
            print('Coarse step down with module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        else: 
            print(f'Error: module {self.module.moduleID} will exceed max. down position!')
   
    def multi_step_up(self):
        self.module.dir = 1
        self.msteps = int(round(self.module.msteps_per_rev * self.multistep_numberBox.value()/360))
        self.module.update_pps()
        # check if actual_pos + steps > upper bound  
        # if so set enabled up to False to prevent crash
        self.crash_safety(self.module, self.msteps)
        if self.module.motor.up_enabled:
            self.motor.move_by(self.module.dir * self.msteps * self.module.dir_inv_mod, self.module.pps)
            print('Coarse step up with module:', str(self.module.moduleID), 'at', str(self.rpmBox.value()), 'RPM')
        else: 
            print(f'Error: module {self.module.moduleID} will exceed max. up position!')


    
    def goto_s3(self, pos, rpm):
        # update current position to csv every on_timeout-cycle 
        self.positions.loc[0, 'current'] = self.motor_s3.actual_position
        self.positions.to_csv(
        'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/position_quenched.csv', index = False)
        # self.positions.to_csv(
        # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index = False) 
        # go to position (pos arg): - opened valve: self.motor_s3.max_pos_up
        #                           - closed valve: self.motor_s3.max_pos_down
        # with velocity (rpm arg):  - prequench v.: self.rpmBox_prequench.value()
        #                           - quench v.   : self.rpmBox_quench.value()
        pps = round(rpm * self.module_s3.msteps_per_rev/60)
        self.motor_s3.move_to(pos, pps)
        print('s3 moves to', pos, 'with', rpm, 'RPM')
        # keep record of position with get_position_reached
        if pos == self.motor_s3.max_pos_up:
            # check if quench succeeded: gets called repeatedly from drivetimer.timeout 
            # so if is fine. drivetimer.stop() ends the quench process
            if abs(self.motor_s3.actual_position - self.motor_s3.max_pos_up) <= self.threshold_valve:
                print('oil valve opened, quench completed!')
                self.pushB_close_valve.setStyleSheet('color:red')
                self.drivetimer.stop()
        elif pos == self.motor_s3.max_pos_down:
            # as long as valve not closed 
            while abs(self.motor_s3.actual_position - self.motor_s3.max_pos_down) > self.threshold_valve:
                QApplication.processEvents()
                self.pushB_close_valve.setStyleSheet('color: red')
            # when closed
            self.pushB_close_valve.setStyleSheet('color: green')
        else: 
            # no designated pos reached: show position and how much is left [steps]
            print('motor s3 is at:',self.motor_s3.actual_position, ',', 
                  abs(self.motor_s3.actual_position - pos), 'steps are left')
            
            
    def drive_PID(self):
        interval = 1000
        self.drivetimer = QTimer()
        self.drivetimer.setInterval(interval)
        self.module_s1.dir = -1 # ensures correct motor_s1 rotation direction
                
        # init controller instance:
        # c = Controller(interval/1000, 50, 10, 50, True) # /1000 for ms->s; good?
        c = Controller(interval/1000, 10, 2, 1, True)
        self.SP = self.sigma1_SP_spinBox.value()
        
        def on_timeout():
            c.controller_update(self.SP,
                                self.chan_s1.value/self.adc_sigma1_scaling,
                                self.pps_rpm_converter(self.module_s1, abs(self.motor_s1.actual_velocity)),
                                self.module_s1.maxvel/self.PID_max_vel_scale)
            self.module_s1.rpm = c.output
            self.module_s1.update_pps()   ###TODO: dir inversion factor gets used here
            # self.CV.append(int(c.output))
            self.motor_s1.rotate(self.module_s1.pps)
            
        self.drivetimer.timeout.connect(on_timeout)
        
        self.drivetimer.start()
        self.driveprofile_pushB.setEnabled(False)
        self.stopprofile_pushB.setEnabled(True)
    
    def quench_PID(self):
        interval = 1000
        self.drivetimer = QTimer()
        self.drivetimer.setInterval(interval)
        self.module_s1.dir = 1 # ensures correct motor_s1 rotation direction
                
        print("sig3:",self.chan_s3.value/self.adc_sigma3_scaling)
        print("sig1:",self.chan_s1.value/self.adc_sigma1_scaling)
        # init controller instance:
        # c = Controller(interval/1000, 50, 10, 50, True) # /1000 for ms->s; good?
        c = Controller(interval/1000, 1, 0.1, 0, False)
        self.current_oilp = self.chan_s3.value/self.adc_sigma3_scaling
        self.old_oilp = self.current_oilp  
        self.enable_slow = False
        
        self.prequench_rpm = self.rpmBox_prequench.value() ###TODO: initial param update (only refreshed if update button pressed)
        self.quench_rpm = self.rpmBox_quench.value()
        
        self.SP = self.dsigma_SP_spinBox.value()
        # self.SP_correction = 0
        
        def on_timeout():
            
            self.current_oilp = self.chan_s3.value/self.adc_sigma3_scaling
            # print("current ",self.current_oilp, "diff", self.old_oilp - self.current_oilp)
            # see if oilp changed by the amout threshold [MPa?] 
            if (self.old_oilp - self.current_oilp) < self.threshold_oilp and self.enable_slow == False:
                # no: open valve fast (prequench velocity)
                self.goto_s3(self.motor_s3.max_pos_up, self.prequench_rpm)
            elif (self.old_oilp - self.current_oilp) >= self.threshold_oilp or self.enable_slow == True:
                # yes: open valve slow (quench velocity)
                self.enable_slow = True
                self.goto_s3(self.motor_s3.max_pos_up, self.quench_rpm)
            # compare old oilp with new measured value #TODO: test this!!
            self.old_oilp = self.current_oilp
            
            # decreasing setpoint for s1 below 200 MPa -> s1 converges to 0
            if self.chan_s3.value/self.adc_sigma3_scaling <= 200 and self.SP > 0: ###TODO: below 200 MPa let s1 converge to 0
                self.SP -= self.quench_rpm * 7#TODO: check

            PV = self.chan_s1.value/self.adc_sigma1_scaling - self.chan_s3.value/self.adc_sigma3_scaling
            print("diff stress ",PV, "setpoint", self.SP)
            c.controller_update(self.SP, PV,
                                self.pps_rpm_converter(self.module_s1, abs(self.motor_s1.actual_velocity)),#TODO: removed abs : abs(self.motor_s1.actual_velocity)
                                self.module_s1.maxvel/self.PID_max_vel_scale)
            print("pid output rpm", c.output)
            self.module_s1.rpm = c.output
            self.module_s1.update_pps()
            # self.CV.append(int(c.output))
            self.motor_s1.rotate(- self.module_s1.pps) # TODO: correct to set this negative?
            
        self.drivetimer.timeout.connect(on_timeout)
        
        self.drivetimer.start()
        self.driveprofile_pushB.setEnabled(False)
        self.stopprofile_pushB.setEnabled(True)
        
    def stop_profile(self):
        if hasattr(self, 'drivetimer'):
            self.drivetimer.stop()
        for module in module_list:   ###TODO: all modules stop not only active ones (independant from checkboxes)\
            self.module = module
            self.stop_motor()
            print(f"module: {self.module.moduleID} stopped at pos: ", self.module.motor.actual_position)
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
        self.rpmSlider.setMinimum(int(round(self.rpmBox.minimum() * self.module_s1.msteps_per_rev / 60)))
        self.rpmSlider.setMaximum(int(round(self.rpmBox.maximum() * self.module_s1.msteps_per_rev / 60)))
        # amount of single steps in multistep mode:
        self.multistep_numberBox.setMinimum(0)
        self.multistep_numberBox.setMaximum(360)
        # set maxvel spinBox:
        self.maxvel_spinBox.setMinimum(0)
        self.maxvel_spinBox.setMaximum(120)
        
    def clear_button_colors(self):
        self.perm_down_Button.setStyleSheet("")
        self.perm_up_Button.setStyleSheet("")
        
        
    def close_app(self):
        # stop motors and set actpos to targetpos to prevent motors from diving to targetpos instantly when reconnected?
        for module in module_list:
            self.module = module
            self.stop_motor()
        # save current position of s3 module one last time 
        self.positions.loc[0, 'current'] = self.motor_s3.actual_position
        self.positions.to_csv(
        'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/position_quenched.csv', index = False)
        # self.positions.to_csv(
        # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index = False) 
        print('saved current position!')
        self.close()
        

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
