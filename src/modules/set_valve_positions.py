#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 16:37:43 2023

@author: pgross
"""

### TO DO
# clean up all the mess!
# improve module assignment by using a module_list?
# add multi_module_control capability to goto and store_pos?
# find good values for max_current parameter for both motor types...

import sys
import time
from PyQt5.QtWidgets import (QMainWindow, QApplication)
from pytrinamic.connections import ConnectionManager
# LAPTOP DIR
from modules.gui.set_valve_positions_window import Ui_MainWindow
# LAB PC DIR
# from gui.set_valve_positions_window import Ui_MainWindow
# LAPTOP DIR
from modules.Motor import Motor
# LAB PC DIR
# from ..Motor import Motor

import pandas as pd



### Module setup and assignment ###
port_list = ConnectionManager().list_connections()
for port in port_list:
    Motor(port)

# define list of all moduleIDs and sort connected modules accordingly:
ID_list = [14, 28, 13, 11, 15, 21, 22, 23, 24]
module_list = Motor.sort_module_list(ID_list)

'''Choose names for the modules. Make sure to correctly match the correct 
module with its descriptive variable name (e.g. motor_L) below; 
adjust if needed.'''
module_L = module_list[0]
# module_R = module_list[1]
# module_C = Motor.instances[2]
# expand list as needed...

# for module in module_list:
#     print(module.status_message())


### Class definition ###
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
        # setup functions:
        self.set_allowed_ranges()
        self.set_default_values()
        self.refresh_lcd_displays()
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
        self.stepsBox.setValue(200)         # number of motor steps
        # motor microsteps:
        self.microstepsBox.setValue(256)    # number of microsteps
        # motor rpm (could also be derived from other params...)
        self.rpm_minBox.setValue(0)         # min rpm value
        self.rpm_maxBox.setValue(300)       # max rpm value
        # Motor selection radio buttons:
        self.motor1_radioButton.setChecked(True) # Motor 1 is default
        # Motor selection checkBoxes:
        self.motor1_checkBox.setChecked(True)
        # Mode selection checkBoxes and mode:
        self.mode_single.setChecked(True)
        self.mode = 1
        # Set default motor and module that is active initially:
        self.reset_active_modules()
        # list of store_positions LCDs:
        self.store_lcds = [[self.lcd_stored_1A, self.lcd_stored_1B],
                           [self.lcd_stored_2A, self.lcd_stored_2B]] # expand list if needed...
        
    def connectSignalsSlots(self):
        '''This function defines the widget behaviour with Qt's 
        signal-and-slot mechanism.'''
        ### general ###
        # Close window and end program:
        self.quitButton.clicked.connect(self.close_app)
        self.mode_single.pressed.connect(lambda: self.set_mode(1))
        self.mode_multi.pressed.connect(lambda: self.set_mode(2))
        self.mode_perm.pressed.connect(lambda: self.set_mode(3))
        # reset active modules when mode tab is Changed:
        self.tabWidget.currentChanged.connect(self.reset_active_modules)
        # Status LCDs:
        # self.lcd_current_1.display(module_L.motor.actual_position)
        # Store current position:
        self.storeButtonA.clicked.connect(lambda: self.store_pos(0))
        self.storeButtonB.clicked.connect(lambda: self.store_pos(1))
        # Go to stored position:
        self.goto_buttonA.clicked.connect(lambda: self.multi_module_control(lambda: self.goto(0)))
        self.goto_buttonB.clicked.connect(lambda: self.multi_module_control(lambda: self.goto(1)))
        
        ### single ###
        # Motor selection radioButtons:
        self.motor1_radioButton.pressed.connect(lambda: self.select_module(module_L))
        # self.motor2_radioButton.pressed.connect(lambda: self.select_module(module_R))
        # Rotation Buttons:
        self.s_left.clicked.connect(lambda: self.multi_module_control(self.left))
        self.s_right.clicked.connect(lambda: self.multi_module_control(self.right))
        self.s_stop.clicked.connect(lambda: self.multi_module_control(self.stop_motor))

        ### multi ###
        # Motor selection checkBoxes:
        self.motor1_checkBox.toggled.connect(self.refresh_active_modules)
        self.motor2_checkBox.toggled.connect(self.refresh_active_modules)
        # Rotation Buttons:
        self.m_left.clicked.connect(lambda: self.multi_module_control(self.left))
        self.m_right.clicked.connect(lambda: self.multi_module_control(self.right))
        self.m_stop.clicked.connect(lambda: self.multi_module_control(self.stop_motor))
        
        
        
        ### overwrite opened and closed positions in positions file ###
        self.positions = pd.read_csv('C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv')
        self.positions.columns = self.positions.columns.str.strip()
        self.pushB_set_opened.clicked.connect(lambda: self.overwrite_pos('opened'))
        self.pushB_set_closed.clicked.connect(lambda: self.overwrite_pos('closed'))
        
        
        # print(self.positions.loc[0, 'opened'], self.positions.loc[0, 'closed'])
        self.store_lcds[0][0].display(self.positions.loc[0, 'opened'])
        self.store_lcds[0][1].display(self.positions.loc[0, 'closed'])
        
        
    def overwrite_pos(self, pos):
        self.positions.loc[0, pos] = self.motor.actual_position
        self.positions.to_csv('C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index = False)
        print('overwritten pos', pos)
        
        
    def select_module(self, m):
        '''Module selection for single module control.'''
        self.module = m
        self.motor = self.module.motor
        # overwrite list of active modules:
        self.active_modules = [self.module]
        print('Selected motor: Motor', self.module.moduleID)
        #print(self.module.status_message())
        
    def reset_active_modules(self):
        '''Set default motor and module that is active initially:'''
        self.module = module_L
        self.motor = module_L.motor
        # clear list of active modules:
        self.active_modules = [self.module]
        # set buttons correctly:
        self.motor1_radioButton.setChecked(True)
        self.motor1_checkBox.setChecked(True)
        self.motor2_checkBox.setChecked(False)
        # expand list if needed...
        
    def refresh_active_modules(self):
        '''Module selection for multi module use.'''
        # clear list of active modules:
        self.active_modules = []
        # write all possible module checkboxes to a list:
        boxlist = [self.motor1_checkBox, self.motor2_checkBox]
        # iterate over all checked boxes:
        for box in boxlist:
            if box.isChecked() == True:
                # add all selected modules to the active list:
                if box == self.motor1_checkBox:
                    self.active_modules.append(module_L)
                # elif box == self.motor2_checkBox:
                #     self.active_modules.append(module_R)
                # elif box == self.motor3_checkBox:
                #     self.active_modules.append(module_C)
                # ...
        # update single active module and motor:
        if len(self.active_modules) == 1:
            self.module = self.active_modules[0]
            self.motor = self.module.motor
        # Status message:
        print('Selected motor(s):')
        for module in self.active_modules:
            print('Motor', module.moduleID)
            
    def set_mode(self, mode):
        self.mode = mode
        print('Mode:', mode)
        
    def left(self):
        print('Mode:', self.mode)
        if self.mode == 1:
            self.single_step_left()
        elif self.mode == 2:
            self.multi_step_left()
        elif self.mode == 3:
            self.perm_rot_left()
            
    def right(self):
        print('Mode:', self.mode)
        if self.mode == 1:
            self.single_step_right()
        elif self.mode == 2:
            self.multi_step_right()
        elif self.mode == 3:
            self.perm_rot_right()
            
    def store_pos(self, pos_idx):
        '''Store position of current active modules in a special instance
        variable for later use. Argument pos_idx (type=int) refers to the 
        index of the "stored position" column.'''
        # iterate over active modules:
        for module in self.active_modules:
            # Save current module position.
            module.module_positions[pos_idx] = module.motor.actual_position
            # find correct LCD for display of saved position value using the
            # store_lcds matrix-like list:
            # 1st dimension = row_idx (= module_idx),
            # 2nd dimension = col_idx (= pos_idx)
            if module.motor == module_L.motor:
                self.store_lcds[0][pos_idx].display(module.module_positions[pos_idx])
            # elif module.motor == module_R.motor:
            #     self.store_lcds[1][pos_idx].display(module.module_positions[pos_idx])
            
    def refresh_lcd_displays(self):
        '''Update the status LCDs.'''
        self.lcd_current_1.display(module_L.motor.actual_position)
        # self.lcd_current_2.display(module_R.motor.actual_position)
        # expand list for more modules...
        # time.sleep(0.1)
        
    # def single_module_control(self, action):
    #     # initial refresh:
    #     self.refresh_lcd_displays()
    #     action()
    #     # Check if motor is active:
    #     while not self.module.motor.get_position_reached():
    #         # Prevent blocking of the application by the while loop:
    #         QApplication.processEvents()
    #         # Refresh LCD
    #         self.refresh_lcd_displays()
            
    def multi_module_control(self, action):
        '''Add multi motor control capability. Argument "action" is one of
        the motor control functions below (e.g., single_step).'''
        # iterate over all active modules and apply the action function:
        for module in self.active_modules:
            # Prevent blocking of the application by the while loop:
            QApplication.processEvents()
            # initial refresh:
            self.refresh_lcd_displays()
            # set module and motor: IS THIS NEEDED?
            self.module = module
            self.motor = module.motor
            action()
            # final refresh:
            self.refresh_lcd_displays()
        # iterate over all active modules and refresh LCDs:
        for module in self.active_modules:
            # Check if motor is active:
            while not module.motor.get_position_reached():
                # Prevent blocking of the application by the while loop:
                QApplication.processEvents()
                # Refresh LCD
                self.refresh_lcd_displays()
            
    def goto(self, pos_idx):
        pps = round(self.rpmBox.value() * self.module.msteps_per_rev/60)
        pos = self.module.module_positions[pos_idx]
        self.module.motor.move_to(pos, pps)
        print('go to', pos)
        
    def single_step_left(self):
        '''Single fullstep mode. Required amount of msteps and pulse freqency
        are calculated from the module settings and the value of rpmBox.'''
        # initialize movement parameters for one fullstep:
        msteps = self.module.msteps_per_fstep
        pps = round(self.rpmBox.value() * self.module.msteps_per_rev/60)
        # move by needed amount of msteps at pps velocity in negative direction:
        self.motor.move_by(-msteps, pps)
        # Status message:
        print('single fullstep left')
        print('= rotate', -msteps)
        # self.refresh_lcd_displays()
        
    def single_step_right(self):
        '''As above.'''
        msteps = self.module.msteps_per_fstep
        pps = round(self.rpmBox.value() * self.module.msteps_per_rev/60)
        # move by needed amount of msteps at pps velocity in positive direction:
        self.motor.move_by(msteps, pps)
        print('single fullstep right')
        print('= rotate', msteps)
        # self.refresh_lcd_displays()
        
    def multi_step_left(self):
        '''Multiple fullsteps mode. Required amount of msteps and pulse freqency
        are calculated from the module settings, specified amount of fullsteps
        and the value of rpmBox.'''
        # initialize movement parameters for required fullsteps:
        msteps = self.module.msteps_per_fstep * self.multistep_numberBox.value()
        pps = round(self.rpmBox.value() * self.module.msteps_per_rev/60)
        # move by needed amount of msteps at pps velocity in negative direction:
        self.motor.move_by(-msteps, pps)
        # Status message:
        print(str(self.multistep_numberBox.value()), 'fullsteps left with', str(self.rpmBox.value()), 'rpm')
        
    def multi_step_right(self):
        '''As above.'''
        msteps = self.module.msteps_per_fstep * self.multistep_numberBox.value()
        pps = round(self.rpmBox.value() * self.module.msteps_per_rev/60)
        # move by needed amount of msteps at pps velocity in positive direction:
        self.motor.move_by(msteps, pps)
        # Status message:
        print(str(self.multistep_numberBox.value()), 'fullsteps right with', str(self.rpmBox.value()), 'rpm')
        
    def perm_rot_left(self):
        '''Permanent rotation mode. Required pulse frequency is calculated
        from the module settings and the value of rpmBox.'''
        # motor speed calculated from: rpmBox * msteps_per_rev / 60sec
        pps = round(self.rpmBox.value() * self.module.msteps_per_rev/60)
        # Rotate in negative direction:
        self.motor.rotate(-pps)
        # Status message:
        print('Rotating left with', str(self.rpmBox.value()), 'rpm')
        # self.refresh_lcd_displays()
        
    def perm_rot_right(self):
        '''As above.'''
        pps = round(self.rpmBox.value() * self.module.msteps_per_rev/60)
        # Rotate in positive direction:
        self.motor.rotate(pps)
        # Status message:
        print('Rotating right with', str(self.rpmBox.value()), 'rpm')
        # self.refresh_lcd_displays()
        
    def stop_motor(self):
        '''Stop signal to all motors; can always be sent to the motors.'''
        self.module.motor.stop()
        # ensure that the motors actually have time to slow down and stop:
        time.sleep(0.2)
        # set target_position to actual_position for the multi_control loop:
        act_pos = self.module.motor.get_axis_parameter(self.module.motor.AP.ActualPosition)
        self.module.motor.set_axis_parameter(self.module.motor.AP.TargetPosition, act_pos)
        # targ_pos = self.module.motor.get_axis_parameter(self.module.motor.AP.TargetPosition)
        # print('debug: stop', self.module.moduleID, act_pos, targ_pos) # debug message
        print('Motor', self.module.moduleID, 'stopped!')
        # self.refresh_lcd_displays()
        
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
        
    def close_app(self):
        # save current position of s3 module one last time 
        self.positions.loc[0, 'current'] = self.motor.actual_position
        self.positions.to_csv(
        'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index = False)
        # self.positions.to_csv(
        # 'C:/Daten/Peter/Studium/A_Programme_Hiwi/Projekte/griggs_control/src/position_quenched.csv', index = False) 
        print('saved current position!')
        self.close()
        
        

def run_app():
    app = 0
    '''Initialize GUI control flow management. Requires passing
    argument vector (sys.argv) or empty list [] as arg; the former allows
    to pass configuration commands on startup to the program from the
    command line, if such commands were implemented.'''
    # If app is already open, use that one, otherwise open new app:
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
