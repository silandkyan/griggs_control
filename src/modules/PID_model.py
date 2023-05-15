#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 18:09:33 2022

@author: philip

algorithm from https://en.wikipedia.org/wiki/PID_controller#Pseudocode

"""

import numpy as np
import matplotlib.pyplot as plt

plt.clf()

# def PID_controller(value, setpoint, Kp, Ki, Kd):
#     error = setpoint - value
#     output = ( output[k-1] + a0 * error[k] + a1 * error[k-1] + a2 * error[k-2] ) 
#     return output


# parameters
#Kp, Ki, Kd = 0.5, 0.0, 0.0 # P
#Kp, Ki, Kd = 0.45, 0.54, 0.0 # PI
Kp, Ki, Kd = 0.8, 1.0, 0.001 # PID

#Kp = 0.5
#Ki = 0.5
#Kd = 0.0

efficiancy_factor = 0.9 # arbitrary value to simulate response lag

t_start = 0
t_end = 10
dt = 0.1

t = np.arange(t_start, t_end, dt)
#setpoint = np.sin(t)
setpoint = np.zeros_like(t)
setpoint[5:50] = 1
setpoint[50:70] = 2
setpoint[70:] = -1
#print(setpoint)

output = np.zeros_like(t)
error = np.zeros_like(t)
value = np.zeros_like(t)

a0 = Kp + Ki*dt + Kd/dt
a1 = - Kp - 2*Kd/dt
a2 = Kd/dt
#print(a0, a1, a2)

for k in np.arange(2, len(t)-1):
    #print(k)
    #print('value before: ' + str(value[k]))
    #print('setpoint: ' + str(setpoint[k]))
    #print('error k-2: ' + str(error[k-2]))
    #print('error k-1: ' + str(error[k-1]))
    
    error[k] = setpoint[k] - value[k]
    #print('error k: ' + str(error[k]))
    
    output[k] = ( output[k-1] + a0 * error[k] + a1 * error[k-1] + a2 * error[k-2] ) 
    #print('output: ' + str(output[k]))
    
    value[k+1] = (value[k] + output[k]) * efficiancy_factor
    #print('value after: ' + str(value[k+1]))

plt.plot(t, setpoint, label='set')
plt.plot(t, output, label='out')
plt.plot(t, value, label='value')
plt.legend()

#x = 0
#while True:
    #print(x)
    #x += 1


