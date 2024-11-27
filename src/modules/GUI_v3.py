# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:08:43 2023

@author: pgross
"""

import sys
import time

from PyQt5.QtWidgets import (QMainWindow, QApplication)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor

from pytrinamic.connections import ConnectionManager

import pandas as pd 


# import time

from modules.gui.main_window_v1 import Ui_MainWindow #TODO
from modules.set_init_gui_settings_v1 import init_gui
from .Motor import Motor
from .Controller import Controller


'''TODO:
        - close valve function: get posititons and colors right #DONE (probably)
        - go over new names for widgets #DONE
        - care about goto s3 function #DONE
        - scaling for multistep for s3 (to Mpa) #DONE
        - current position update in multistep up for s3 (not given w.o. multimodulecontrol) #DONE
        - connect signal slots: prequench velocity pushB is missing #DONE
        - check position imports and operations #DONE
        - check if init_gui functions works
        - implement clickwarning for dir inversion when starting program !!!
        - check if get_position_reached flag works
        - test prequench hold  
        - add in readme: use %reload_ext autoreload and %autoreload 0 to disable reloading from cache mem
    NOTE:
        - manual stopbuttons only affect single motors, PID-mode stopbuttons stop both motors as well as quit app
        - maxvel for s3 hardcoded to 60RPM
        - close oil valve button takes rpm from prequench spinB on tab3
        - permanent mode for s3 works as long as button is pressed down
        - position of s3 in permanent mode only gets updated when pressing stop button not while driving
        - stress lcd's are only enabled if both ADC checkboxes are checked
        - hold prequench function works with press and release: adjust oilp threshold to get either in prequench 
        or quench velocitys for s3 in callback function of quench pid'''

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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('motor_s1 Control Panel -- MoCoPa')
        # implement motors in correct syntax:
        self.module_s1 = s1
        self.module_s3 = s3
        self.motor_s1 = self.module_s1.motor
        self.motor_s3 = self.module_s3.motor  #TODO adapted to s3 compatibility!!
        # choose s3 motor for starting tab:
        self.module = self.module_s3
        self.motor = self.motor_s3
        # for motor s1:
        self.last_motor_command_s1 = None
        # PID
        self.PID_max_vel_scale = 1  # TODO: what is this?
        # ADC connection:
        self.chan_s1 = None
        self.chan_s3 = None
        self.adc_sigma1_scaling = 3.578 # TODO: note: scaling-factor to MPa!
        self.adc_sigma3_scaling = 12.364 
        # connect signals with actions: 
        self.connectSignalsSlots()
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
        'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/positions_valve.txt', sep='\t')
        # self.positions = pd.read_csv(
        # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/positions_valve.txt', sep='\t') 
        if self.motor_s3.actual_position != int(self.positions.loc[0, 'current']):
            self.positions['opened'] = self.positions['opened']-self.positions['current']
            self.positions['closed'] = self.positions['closed']-self.positions['current']
            self.positions.to_csv(
            'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/positions_valve.txt', index=False)
        self.valve_closed = self.positions.loc[0, 'closed']
        self.valve_distance = self.positions.loc[0, 'distance']
        self.valve_current = self.positions.loc[0, 'current']
        self.valve_opened = self.valve_closed + self.valve_distance
        self.is_valve_closed()
        
        
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
        # if tab0 active chosen module is s1, if tab2 is active, chosen module is s3
        self.tabWidget.currentChanged.connect(lambda: self.refresh_module_list(
            (lambda i, arg: arg if i % 2 == 0 else None)(
                self.tabWidget.currentIndex(), 
                (lambda arg1, arg2: arg1 if self.tabWidget.currentIndex() < 2 else arg2)(self.module_s1, self.module_s3)
            )
        ))
        # Multi step rotation:
            # s1
        self.multi_up_s1.clicked.connect(self.multi_step_up)
        self.pushB_multi_down_s1.clicked.connect(self.multi_step_down)
            #s3
        self.multi_up_s3.clicked.connect(self.multi_step_up)
        # Continuous rotation:
            #s1
        self.pushB_perm_down_s1.clicked.connect(self.permanent_down)
        self.pushB_perm_up_s1.clicked.connect(self.permanent_up)
            #s3
        self.pushB_perm_up_s3.clicked.connect(self.permanent_up)
        self.pushB_perm_down_s3.pressed.connect(self.permanent_down)
        self.pushB_perm_down_s3.released.connect(self.stop_motor)
        # Stop buttons:
            #s1
        self.pushB_stop_s1.clicked.connect(self.stop_motor)
            #s3
        self.pushB_stop_s3.clicked.connect(self.stop_motor)
        # refresh rpm when value is changed:
            #s1
        self.rpmBox_s1.valueChanged.connect(self.rpmBox_changed)
        self.rpmSlider_s1.valueChanged.connect(self.rpmSlider_changed)
            #s3
        self.rpmBox_s3.valueChanged.connect(self.rpmBox_changed)
        self.rpmSlider_s3.valueChanged.connect(self.rpmSlider_changed)
        # direction inversion (only for s1):
        self.invert_checkBox.stateChanged.connect(self.invert_direction)
        # update velocity button:
            #s1
        self.pushB_update_rpm_s1.clicked.connect(self.update_rpm)
            #s3
        self.pushB_update_rpm_s3.clicked.connect(self.update_rpm)  
        
        # PID:
        self.pushB_start_const.clicked.connect(self.drive_PID)
        self.pushB_stop_const.clicked.connect(self.stop_profile)
        self.pushB_update_const.clicked.connect(lambda: self.update_PID('const'))
        # Quenching 
        self.pushB_quench_start.clicked.connect(self.quench_PID)
        self.pushB_quench_stop.clicked.connect(self.stop_profile)
        self.pushB_goto_prequench.pressed.connect(lambda: self.prequench_hold(self.old_oilp))
        self.pushB_goto_prequench.released.connect(lambda: self.prequench_hold(0.5))
        self.pushB_update_quench.clicked.connect(lambda: self.update_PID('quench'))
        # start ADC connection:
        self.initADC_s1.stateChanged.connect(lambda: self.init_adc(self.initADC_s1, 's1'))
        self.initADC_s3.stateChanged.connect(lambda: self.init_adc(self.initADC_s3, 's3'))
        # close oilvalve as long as button pressed in gui
        self.pushB_close_valve.pressed.connect(lambda: self.goto_s3(self.valve_closed, 
                                                                    self.rpmBox_prequench.value()))
        self.pushB_close_valve.released.connect(self.stop_motor)
        # set closed position of valve 
        self.pushB_set_closed.clicked.connect(self.set_closed)
        
    def is_valve_closed(self):
        if abs(self.valve_closed - self.valve_current) > self.threshold_valve:
            self.pushB_close_valve.setStyleSheet('color: rgb(100, 200, 0)')
            print('Warning: oil valve is not closed all the way!',
                  f'Motor is off by = {abs(self.valve_closed - self.valve_current)} steps',  
                  ' press "close oil valve"-button to close it!')
        else: 
            self.pushB_multi_up_s3.setEnabled(True)
            self.pushB_perm_up_s3.setEnabled(True)
            self.pushB_close_valve.setStyleSheet('color: rgb(0, 200, 100)')
            print('s3 motor valve closed. Motor is off by',
                  f' = {abs(self.valve_closed - self.valve_current)} steps')

    ###   DATA MANAGEMENT   ###
        
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
            
        if (self.initADC_s1.isChecked == True) and (self.initADC_s3.isChecked == True):
            self.enable_display_stress = True 
            
            # return self.chan_s1, self.chan_s3


    ###   GRAPH WINDOW   ###
    
    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        line = self.graphWidget.plot(x, y, name=plotname, pen=pen)
        return line

        
    def update_plot(self):
        # plot lines:
        self.line1.setData(self.time, self.act_vel_s1)
        self.line2.setData(self.time, self.set_vel)
        self.line3.setData(self.time, self.sigma1_SP)
        self.line4.setData(self.time, self.sigma1_PV)
        self.line5.setData(self.time, self.error)
        self.line6.setData(self.time, self.act_vel_s3)
        # LCDs:
        self.lcd_actvel_s1.display(self.pps_rpm_converter(self.module_s1, abs(self.motor_s1.actual_velocity)))
        self.lcd_actvel_s3.display(self.pps_rpm_converter(self.module_s3, abs(self.motor_s3.actual_velocity)))
        if self.enable_display_stress == True:
            self.lcd_stress_s1.display(self.chan_s1.value/self.adc_sigma1_scaling)
            self.lcd_stress_s3.display(self.chan_s3.value/self.adc_sigma3_scaling)
            self.lcd_dstress.display(self.chan_s1.value/self.adc_sigma1_scaling - self.chan_s3.value/self.adc_sigma3_scaling)

        
    ###   CALCULATORS (for unit conversion)   ###
    
    def rpmSlider_changed(self):
        if self.module == self.module_s1:
            self.module.rpm = self.rpmSlider_s1.value()
            self.rpmBox_s1.setValue(self.module.pps / self.module.msteps_per_rev * 60)
        else:
            self.module.rpm = self.rpmSlider_s3.value()
            self.rpm_box_s3.setValue(self.module.pps / self.module.msteps_per_rev * 60)
        
    def rpmBox_changed(self):
        if self.module == self.module_s1:
            self.module.rpm = self.rpmBox_s1.value()
            self.rpmSlider_s1.setValue(self.module.pps / self.module.msteps_per_rev * 60)
        else:
            self.module.rpm = self.rpmBox_s3.value()
            self.rpmSlider_s3.setValue(self.module.pps / self.module.msteps_per_rev * 60)
            
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
    

        
    def refresh_module_list(self, module):
        # set instance var to selected motor (works for manual modes)
        self.module = module
        self.motor = module.motor
    
    ###   MOTOR CONTROL FUNCTIONS   ###
    
    def update_rpm(self):
        '''This function first updates the module_s1 pps value from the rpmBox value
        and then executes the last command send to the motor_s1, which is stored
        explicitly in a variable when the respective functions are called.'''
        if self.module == self.module_s1:
            if not self.last_motor_command_s1 == None:
                self.module_s1.rpm = self.rpmBox_s1.value()
                self.module_s1.update_pps()
                self.last_motor_command_s1()
            else:
                print('no command given yet...')
        elif self.module == self.module_s3:
            self.module_s3.rpm = self.rpmBox_s3.value()
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
            
    def update_position(self):
        self.positions.loc[0, 'current'] = self.motor_s3.actual_position
        self.positions.to_csv(
        'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/positions_valve.txt', index = False)
            
    def invert_direction(self):
        if self.invert_checkBox.isChecked() == True:
            self.module_s1.dir_inv_mod = -1
        if self.invert_checkBox.isChecked() == False:
            self.module_s1.dir_inv_mod = 1
        self.module_s1.rpm = self.rpmBox_s1.value()
        self.module_s1.update_pps()
        print('dir for module s1 inverted!')
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
        if self.module == self.module_s3:
            self.update_position()
        self.clear_button_colors()
        print('Motor', self.module.moduleID, 'stopped!')

    def permanent_down(self):
        self.module.dir = -1
        self.module.update_pps()
        self.motor.rotate(self.module.pps) # positive pps -> clockwise
        if self.module == self.module_s1:
            self.last_motor_command_s1 = self.permanent_down()
            self.pushB_perm_down_s1.setStyleSheet("QPushButton {background-color: rgb(0, 200, 100);}")
            print('Rotating down with', str(self.rpmBox_s1.value()), 'rpm')
        else:
            self.pushB_perm_down_s3.setStyleSheet("QPushButton {background-color: rgb(0, 200, 100);}")
            print('Rotating down with', str(self.rpmBox_s3.value()), 'rpm')
    
    def permanent_up(self):
        self.module.dir = 1
        self.module.update_pps()
        self.motor.rotate(self.module.pps)
        if self.module == self.module_s1:
            self.last_motor_command_s1 = self.permanent_down()
            self.pushB_perm_up_s1.setStyleSheet("QPushButton {background-color: rgb(0, 200, 100);}")
            print('Rotating up with', str(self.rpmBox_s1.value()), 'rpm')
        else:
            self.pushB_perm_up_s3.setStyleSheet("QPushButton {background-color: rgb(0, 200, 100);}")
            print('Rotating up with', str(self.rpmBox_s3.value()), 'rpm')

    def multi_step_down(self):
        self.module.dir = -1
        self.msteps = int(round(self.module.msteps_per_rev * self.spinB_multistep_s1.value()/360))
        self.module.update_pps()
        self.motor.move_by(self.module.dir * self.msteps * self.module.dir_inv_mod, self.module.pps)
        print('Coarse step down with module:', str(self.module.moduleID), 'at', str(self.rpmBox_s1.value()), 'RPM')
   
    def multi_step_up(self):
        self.module.dir = 1
        if self.module == self.module_s1:
            # degrees to msteps 
            self.msteps = int(round(self.module_s1.msteps_per_rev * self.spinB_multistep_s1.value()/360))
            self.module.update_pps()
            self.motor.move_by(self.module.dir * self.msteps * self.module.dir_inv_mod, self.module.pps)
            print('Coarse step up with module:', str(self.module.moduleID), 'at', str(self.rpmBox_s1.value()), 'RPM')
        elif self.module == self.module_s3:
            # MPa to msteps 
            self.msteps = int(round(self.module_s3.msteps_per_rev * self.spinB_multistep_s3.value()/320))
            self.module.update_pps()
            self.motor.move_by(self.module.dir * self.msteps * self.module.dir_inv_mod, self.module.pps)
            print('Coarse step up with module:', str(self.module.moduleID), 'at', str(self.rpmBox_s3.value()), 'RPM')
        # at this hirarchy, update_pos makes sure motor updates position when reached, not while driving there?
        self.update_position()
    
    
    def goto_s3(self, pos, rpm):
        # update current position to csv every on_timeout-cycle 
        self.update_position()
        # self.positions.to_csv(
        # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index = False) 
        pps = round(rpm * self.module_s3.msteps_per_rev/60)
        self.motor_s3.move_to(pos, pps)
        # keep record of position with get_position_reached
        self.pushB_multi_up_s3.setEnabled(False)
        self.pushB_perm_up_s3.setEnabled(False)
        self.pushB_close_valve.setStyleSheet('color: color: rgb(200, 100, 0)')
        while not self.motor_s3.get_position_reached() == 1:
            QApplication.processEvents()
            print('s3 is at:',self.motor_s3.actual_position, ',', 
                  abs(self.motor_s3.actual_position - pos), 'steps to go')
        # when closed
        if abs(self.motor_s3.actual_position - pos) <= self.threshold_valve:
            self.update_position()
            self.pushB_multi_up_s3.setEnabled(True)
            self.pushB_perm_up_s3.setEnabled(True)
            self.pushB_close_valve.setStyleSheet('color: color: rgb(0, 200, 100)')
            
    def prequench_hold(self, threshold):
        if self.drivetimer.isActive():
            self.threshold_oilp = threshold
        else:
            print('this function is only enabled if quench PID is operating!')
            
    def set_closed(self):
        self.valve_closed = self.module_s3.motor.actual_position
        self.valve_opened = self.valve_closed + self.valve_distance #TODO: does this work?
        self.positions.loc[0, 'closed'] = self.valve_closed
        self.positions.to_csv(
        'C:/Users/GriggsLab_Y/Documents/software/griggs_control/src/positions_valve.txt', index = False)
        self.pushB_multi_up_s3.setEnabled(True)
        self.pushB_perm_up_s3.setEnabled(True)
        self.pushB_close_valve.setStyleSheet('color: color: rgb(0, 200, 100)')
        
        
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
                self.goto_s3(self.valve_opened, self.prequench_rpm)
            elif (self.old_oilp - self.current_oilp) >= self.threshold_oilp or self.enable_slow == True:
                # yes: open valve slow (quench velocity)
                self.enable_slow = True
                self.goto_s3(self.valve_opened, self.quench_rpm)
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
        self.update_position()
        self.driveprofile_pushB.setEnabled(True)
        self.stopprofile_pushB.setEnabled(False)
    

    ###   GENERAL GUI SETTINGS   ###
    def clear_button_colors(self):
        self.pushB_perm_up_s1.setStyleSheet("")
        self.pushB_perm_down_s1.setStyleSheet("")
        self.pushB_perm_up_s3.setStyleSheet("")
        self.pushB_perm_down_s3.setStyleSheet("")
        
    def close_app(self):
        # all motors stop before closing app and update position of s3
        for module in module_list:
            self.module = module
            self.stop_motor()
        # update positon of s3 one last time 
        # self.update_position()
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
    # init standart settings for gui:
    init_gui(main_win)
    # Open GUI window on screen:
    main_win.show()
    # Return an instance of a running QApplication = starts event handling
    return app.exec()
