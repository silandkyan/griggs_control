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
    timeout = None,# wait for data to arrive
    parity = serial.PARITY_NONE,# no extra bit is sent for checking data integrity
    stopbits = serial.STOPBITS_ONE,# use one stop bit to signal end of on data byte
    bytesize = serial.EIGHTBITS# use data length of 8 bits
    )
ser.close()
ser.open()
    
#First Serial (USB) handshake after arduino restart takes ca. 1,6 sec. - this is different than ser.open / close
#Any signal generated during this time is LOST (not read afterward)
#it would be good to find a way, to check is there was a handshake and Arduino is prepared to recieve
# https://stackoverflow.com/questions/21050671/how-to-check-if-device-is-connected-pyserial
time.sleep(2)

# initialize one instance of Stepper motor controller
motorsteps = 450 # approx. number of motor steps...
enabled = True
forward = True
rpm = 5 #120 seems to be  good max value with DM556T driver and old Motors (8-pin, serial wiring)
rpm_max = 10 # maybe add this property to stepper class
s = S.Stepper(ser, motorsteps, enabled, forward, rpm)
s.open_connection()
start_time = time.time()

# tests with timing; use stepper_control.ino
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
                plt.pause(0.0001)
            if timer2.run == True:
                time_mem.append(timer2.counter)
                print('-> ', timer2.counter)
        except KeyboardInterrupt:
            break
        
# tests with manual control; use stepper_control.ino
if False:
    while True:
        try:
            s.manual_control()
        except KeyboardInterrupt:
            break
        
# tests with finite steps; use stepper_control.ino
if False:
    s.move_steps(int(motorsteps/2))
    
if False:
    while True:
        try:
            s.rotate_single_step()
        except KeyboardInterrupt:
            break

# tests with potentiometer; use stepper_potentiometer.ino
if False:
    mem = [0]
    counter = [0]
    plot_interval = 20
    while True:
        try:
            print(counter[-1], '   ', mem[-1])
            data = ser.readline().decode('utf-8').strip()
            if data != '': # important to check for data integrity
                data = int(data)
                mem.append(data)
                counter.append(counter[-1]+1)
                if len(mem) > plot_interval:
                    plt.clf()
                    plt.plot(counter[-plot_interval:], mem[-plot_interval:])
                    plt.ylim((0, 1025))
                    plt.show()
                    plt.pause(0.001)
                    #time.sleep(0.1) # do not sleep in this loop, it slows down the code massively!
        except KeyboardInterrupt or UnicodeDecodeError:
            break
     
# test of motor control via potentiometer
if True:
    step = 0.1 # base rate of commands, in sec
    mem = [0]
    counter = [0]
    plot_interval = 20
    while True:
        try:
            print(counter[-1], '  ', mem[-1], '  ', s.rpm)
            data = ser.readline().decode('utf-8').strip()
            if data != '': # important to check for data integrity
                data = int(data)
                mem.append(data)
                counter.append(counter[-1]+1)
                s.rpm = (data - 512) / 512 * rpm_max # update rpm based on poti value
                s.set_direction_from_rpm() # update stepper direction
                if len(mem) > plot_interval:
                    plt.clf()
                    plt.plot(counter[-plot_interval:], mem[-plot_interval:])
                    plt.ylim((0, 1025))
                    plt.show()
                    plt.pause(0.001)
                    #time.sleep(0.1) # do not sleep in this loop, it slows down the code massively!
            #s.rotate_single_step() # this does not work since the rotation method is blocking...
        except KeyboardInterrupt or UnicodeDecodeError:
            break

s.close_connection()

end_time = time.time()
print('time elapsed during code runtime: ', end_time - start_time)