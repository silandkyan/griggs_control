#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 11:22:32 2023

@author: pgross
"""

import serial # must be installed, e.g.: conda install pyserial
import time
import matplotlib.pyplot as plt

import modules.Stepper as S
import modules.Timer as T

# initialize serial connection to Arduino, address must be corrected after reconnection
ser = serial.Serial(
    port = '/dev/ttyACM1',
    baudrate = 115200,
    timeout = 0.1,# wait for data to arrive
    parity = serial.PARITY_NONE,# no extra bit is sent for checking data integrity
    stopbits = serial.STOPBITS_ONE,# use one stop bit to signal end of on data byte
    bytesize = serial.EIGHTBITS# use data length of 8 bits
    )
    
#First Serial (USB) handshake after arduino restart takes ca. 1,6 sec. - this is different than ser.open / close
#Any signal generated during this time is LOST (not read afterward)
#it would be good to find a way, to check is there was a handshake and Arduino is prepared to recieve

# if ser.isOpen():     #https://stackoverflow.com/questions/21050671/how-to-check-if-device-is-connected-pyserial
#     print("serial is open!")
# else:
#     print ("connecting Serial. hold on 2 sec")
time.sleep(2)

# initialize one instance of Stepper motor controller
motorsteps = 450 # approx. number of motor steps...
enabled = True
forward = True
rpm = 10 #120 seems to be  good max value with DM556T driver and old Motors (8-pin, serial wiring)
s = S.Stepper(ser, motorsteps, enabled, forward, rpm)
s.open_connection()
start_time = time.time()

# tests with timing
if False:
    # initialize instances of timer for running threads in parallel
    step = 1 # base rate of commands, in sec
    timer1 = T.Timer(start_time, step)
    timer2 = T.Timer(start_time, step/10)
    time_mem = [0]
    while True:
        try:
            timer1.wait()
            timer2.wait()
            if timer1.run == True:
                print('---> ', timer1.counter)
                plt.clf()
                plt.plot(time_mem[-10:])
                plt.draw()
                plt.pause(0.001)
            if timer2.run == True:
                time_mem.append(timer2.counter)
                print('-> ', timer2.counter)
        except KeyboardInterrupt:
            break
        
# tests with manual control
if True:
    while True:
        try:
            s.manual_control()
        except KeyboardInterrupt:
            break
        
# tests with finite steps
if False:
    s.move_steps(int(motorsteps/2))

# tests with potentiometer
if False:
    while True:
        try:
           data = ser.readline().decode('utf-8') 
           print(data) 
        except KeyboardInterrupt:
            break 

s.close_connection()

end_time = time.time()
print('time elapsed during code runtime: ', end_time - start_time)