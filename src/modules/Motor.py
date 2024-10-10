#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 11:24:03 2023

@author: pgross
"""

from pytrinamic.connections import ConnectionManager
from pytrinamic.modules import TMCM1260
from pytrinamic.modules import TMCLModule
import time


##### General functions #####

def disconnect_motors():
    '''Disconnection routine; should be run at the end of the program.'''
    time.sleep(0.2)
    for inst in Motor.instances:
        inst.motor.stop()
    time.sleep(0.2)
    ConnectionManager().disconnect
    print('Motors disconnected!')


##### Motor class definition #####

class Motor(TMCM1260):
    instances = []
    
    @classmethod
    def sort_module_list(cls, moduleID_list):
        '''This function handles the assignment of the physical motors to a
        list of active modules (given as argument), so that the connected
        modules are sorted by increasing moduleID. The moduleIDs must be 
        permanently stored on the Trinamic motor driver module (using 
        TMCL-IDE), currently in the Global Parameter "Serial Address", 
        (Number 66, Bank 0).'''
        module_list = []
        i = 0
        # iterate over moduleIDs:
        for ID in moduleID_list:
            # iterate over all active modules:
            for inst in cls.instances:
                # match IDs of active modules with the given ID_list:
                if inst.moduleID == ID:
                    module_list.append(inst)
                    print('Module', inst.moduleID, 'assigned to module_list[', i, ']')
                    i += 1
        return module_list
    
    def __init__(self, port):
        self.port = port
        self.interface, self.module, self.motor = self.setup_motor(self.port)
        # list of stored positions [A, B, C]:
        self.module_positions = [0, 0, 0]
        self.__class__.instances.append(self)
    
    
        ### MOTOR SETUP ###
        
    def init_drive_settings(self, motor):
        '''Set initial motor drive settings. Speed values are in pps and are
        now scaled to microstep resolution.'''
        motor.down_enabled = True
        motor.up_enabled = True
        motor.max_pos_up = None
        motor.max_pos_down = None       
        motor.drive_settings.max_current = 150
        motor.drive_settings.standby_current = 10
        motor.drive_settings.boost_current = 0
        motor.drive_settings.boost_current = 0
        # maximum velocity:
        self.maxvel = 120
        # Fullsteps/revolution:
        self.fsteps_per_rev = 200
        # direction and inversion modifier:
        self.dir = -1 # switch up(+1)/down(-1)
        self.dir_inv_mod = 1 # pytrinamics built-in axis parameter is not working...
        # set mstep resolution:
        self.mstep_res_factor = motor.ENUM.MicrostepResolution128Microsteps
        # print(self.mstep_res_factor)
        motor.drive_settings.microstep_resolution = self.mstep_res_factor
        # calculate msteps/revolution
        self.msteps_per_fstep = 2 ** self.mstep_res_factor
        self.msteps_per_rev = self.msteps_per_fstep * self.fsteps_per_rev
        # store pps value (for 1 rpm):
        self.pps = self.msteps_per_rev / 60 * self.dir_inv_mod
        # store rpm value:
        self.rpm = 20.0 # default = 20 rpm
        # Toggle step interpolation (works only with 16 microsteps):
        motor.set_axis_parameter(motor.AP.Intpol, value=1)
        # Toggle RelativePositioningOption:
        motor.set_axis_parameter(motor.AP.RelativePositioningOption, 1)
        #print(motor, motor.drive_settings)
        
    def update_pps(self):
        # self.rpm = rpm_value
        self.pps = int(round(self.rpm * self.msteps_per_rev/60) * self.dir * self.dir_inv_mod)
        # print('update_pps', self.rpm, self.pps)

    def init_ramp_settings(self, motor):
        '''Set initial motor ramp settings. Values are in pps and are now scaled 
        to microstep resolution.'''
        # set max values for ramp. trailing factors were tested for 16 msteps.
        # motor.linear_ramp.max_velocity =  int(round(self.msteps_per_rev * 10))
        # motor.linear_ramp.max_acceleration = int(round(self.msteps_per_rev * 5))
        motor.linear_ramp.max_velocity =  50000 # TODO: seems to have no effect...
        motor.linear_ramp.max_acceleration = 3000 # TODO: good value? was 300 before but that was very slow...
        #print(motor, motor.linear_ramp)
            
    def setup_motor(self, port):
        '''Aggregate function that goes through the entire motor setup.'''
        # Establish connection between Trinamic module and USB port:
        self.interface = ConnectionManager('--port ' + port).connect()
        self.module = TMCM1260(self.interface)
        # Activate motor on its respective Trinamic module:
        self.motor = self.module.motors[0]
        self.moduleID = TMCLModule.get_global_parameter(self.module, self.module.GP0.SerialAddress, bank=0)
        print('Connecting module', self.moduleID, '... done!')
        self.init_drive_settings(self.motor)
        self.init_ramp_settings(self.motor)
        print('Setting up module', self.moduleID, '... done!')
        return self.interface, self.module, self.motor
    
    def status_message(self):
        return str('moduleID: ' + str(self.moduleID))
    
    
    ### MOVEMENT CONTROL ###

    # def move_by_msteps(self, msteps, velocity):
    #     '''Wrapper function for Pytrinamics move_by that also gives 
    #     automatic status messages.'''
    #     self.motor.set_axis_parameter(self.motor.AP.RelativePositioningOption, 1)
    #     print('Moving by ' + str(msteps) + ' steps.')
    #     self.motor.move_to(self.motor.actual_position + msteps, velocity)
    #     # wait till position_reached
    #     while not self.motor.get_position_reached():
    #         print('Moving...')
    #         time.sleep(0.2)
    #     print('Moving completed.')
        
    # def move_to_pos(self, pos, velocity):
    #     '''Wrapper function for Pytrinamics move_to that also gives 
    #     automatic status messages.'''
    #     self.motor.set_axis_parameter(self.motor.AP.RelativePositioningOption, 1)
    #     print('Moving to position ' + str(pos) + '.')
    #     self.motor.move_to(pos, velocity)
    #     # wait till position_reached
    #     while not self.motor.get_position_reached():
    #         print('Moving...')
    #         time.sleep(0.2)
    #     print('Moving completed.')

#