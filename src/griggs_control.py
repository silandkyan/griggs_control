#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 11:22:32 2023

@author: pgross
"""

import serial # must be installed, e.g.: conda install pyserial
import time

import modules.Stepper as S

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

#s.manual_control()
s.move_steps(int(motorsteps/2))


s.close_connection()