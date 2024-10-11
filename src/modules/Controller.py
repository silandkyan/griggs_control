#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 10:39:55 2023

@author: pgross

Algorithm from https://en.wikipedia.org/wiki/PID_controller#Pseudocode

Remember that the controller is sensitive to the update interval, so change 
this interval with care.

"""

##### Controller class definition #####

class Controller():
    # instances = []
    
    def __init__(self, dt, Kp, Ki, Kd, prevent_negative_output):
        '''Class for managing PID controlled operation of a stepper motor.
        Parameters:
            dt: int/float; control loop updating timestep, in seconds
            Kp, Ki, Kd: int/float; PID parameters, need manual tuning
            prevent_negative_output: bool; specifies controller mode'''
        self.dt = dt
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prevent_negative_output = prevent_negative_output
        self.error = [0, 0, 0] # with errors at [t-2, t-1, t0]
        self.output = 0
        self.controller_setup()

    def controller_setup(self):
        '''Compute initial controller values (timestep-dependent!).'''
        self.a0 = self.Kp + self.Ki * self.dt + self.Kd / self.dt
        self.a1 = -self.Kp - 2 * self.Kd / self.dt
        self.a2 = self.Kd / self.dt
        print('a-values:', self.a0, self.a1, self.a2)
        
    def controller_update(self, setpoint, procvar, contvar, out_max):
        '''This method calculates controller output based on monitored values 
        of SP, PV, CV. For a continuous control loop, call this function from 
        a loop of frequency dt (see above) with updated values of SP, PV, CV.
        The method will then compute the controller output and update the 
        instance variable (self.output) accordingly.
        Parameters:
            setpoint, procvar, contvar: int/float; 
            out_max: int/float; max allowed output value to avoid hardware damage'''
        # update values:
        self.setpoint = setpoint
        self.procvar = procvar
        self.contvar = contvar
        # update error list:
        self.error.pop(0) # delete oldest element in error list
        self.error.append(self.setpoint - self.procvar) # append current error to list
        print("error array:", self.error)
        # check for prevent_negative_output:
        if self.prevent_negative_output == False:
            # calculate output for new control variable:
            temp = (self.contvar + self.a0 * -self.error[-1] 
                           + self.a1 * -self.error[-2] 
                           + self.a2 * -self.error[-3])
            temp = -temp
            
            # whith correct dir of contvar (here negative) this is the same as above
            # temp = (self.contvar + self.a0 * self.error[-1] 
            #                 + self.a1 * self.error[-2] 
            #                 + self.a2 * self.error[-3])
            print("temp:",temp)
            if temp >= 0: # TODO: chagned self.error[-1] to temp
                temp = 0
            
        elif self.prevent_negative_output == True:
            # calculate output for new control variable:
            temp = (self.contvar + self.a0 * self.error[-1] 
                           + self.a1 * self.error[-2] 
                           + self.a2 * self.error[-3])
            # if temp >= 0: # this does not work!
            if temp <= 0: # TODO: chagned self.error[-1] to temp
                temp = 0
                
        # prevent too large output values:
        if temp <= out_max:
            self.output = temp
        else:
            self.output = out_max
            
        # print('PID values:', self.setpoint, round(self.procvar,2), round(self.contvar, 2),
        #       '--', round(self.error[-1],3), round(self.output, 2))
