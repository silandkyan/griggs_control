#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 10:39:55 2023

@author: pgross
"""
# controller works in...
# P-mode, negative output allowed
# P-mode, negative output prevented
# PI-mode, negative output allowed, but params need tuning
# PI-mode, negative output prevented, but params need tuning
# PID-mode, negative output allowed, but params need tuning
# PID-mode, negative output prevented, but params need tuning

# controller is sensitive of update interval, some real-world testing is needed here...

##### Controller class definition #####

class Controller():
    # instances = []
    
    def __init__(self, dt, Kp, Ki, Kd, prevent_negative_output):
        self.dt = dt
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prevent_negative_output = prevent_negative_output
        self.error = [0, 0, 0] # with errors at [t-2, t-1, t0]
        self.output = 0
        self.controller_setup()

    def controller_setup(self):
        '''Set initial controller values.'''
        self.a0 = self.Kp + self.Ki * self.dt + self.Kd / self.dt
        self.a1 = -self.Kp - 2 * self.Kd / self.dt
        self.a2 = self.Kd / self.dt
        # print('a-values:', self.a0, self.a1, self.a2)
        
    def controller_update(self, setpoint, procvar, contvar, out_max):
        # update values:
        self.setpoint = setpoint
        self.procvar = procvar
        self.contvar = contvar
        # update error list:
        self.error.pop(0) # delete oldest element in error list
        self.error.append(self.setpoint - self.procvar) # append current error to list
        
        # check for prevent_negative_output:
        if self.prevent_negative_output == False:
            # calculate output for new control variable:
            temp = (self.contvar + self.a0 * self.error[-1] 
                           + self.a1 * self.error[-2] 
                           + self.a2 * self.error[-3])
            
        elif self.prevent_negative_output == True:
            # calculate output for new control variable:
            temp = (self.contvar + self.a0 * self.error[-1] 
                           + self.a1 * self.error[-2] 
                           + self.a2 * self.error[-3])
            # if temp >= 0: # this does not work!
            if self.error[-1] <= 0:
                temp = 0
                
        # prevent too large output values:
        if temp <= out_max:
            self.output = temp
        else:
            self.output = out_max
            
        print('PID values:', self.setpoint, self.procvar, round(self.contvar, 1),
              '--', self.error[-1], round(self.output, 1))
