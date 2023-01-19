#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 11:22:32 2023

@author: pgross

Stepper Motor Control Interface

currently, one on-halfstep duration is slightly longer than one off-halfstep duration,
i.e., the on-off signal is not perfectly symmetric. This effect is negligible 
at low frequencies, but gets stronger at frequencies on the order of 100s of Hz.
Still, the frequency of full steps remains stable for such high Hz-values.

Example A: steps = 240, rpm = 100, freq = 400 Hz;
theoretical step_duration = 0.0025 ms
average true step_duration = 0.0034 ms

Example B: steps = 240, rpm = 10, freq = 40 Hz;
theoretical step_duration = 0.025 ms
average true step_duration = 0.026 ms
"""

import time

class Stepper:
    '''
    Generates output signal to control a stepper motor:
    ser = instance of serial connection to Arduino
    motorsteps = number of on-off-steps needed fore one complete motor rotation
    enabled = turn on motor
    forward = rotation direction; True -> anti-cw?
    rpm = rotations (or rounds) per minute
    '''
    def __init__(self, ser, motorsteps, enabled, forward, rpm):
        self.ser = ser 
        self.motorsteps = motorsteps
        self.enabled = enabled
        self.forward = forward
        self.rpm = rpm
        self.freq = abs(rpm) * motorsteps / 60 # in Hz
        if self.freq > 1:
            self.step_duration = 1 / self.freq # in sec
        else:
            self.step_duration = 1
        
    def set_enable(self):
        # encode enabled variable as byte and send to Arduino
        if self.enabled == True:
            self.ser.write(b'E')
        else: 
            self.ser.write(b'D')
        
    def set_direction(self):
        # encode direction variable as byte and send to Arduino
        if self.forward == True:
            self.ser.write(b'F')
        else:
            self.ser.write(b'B')
    
    def set_direction_from_rpm(self):
        # encode direction variable as byte and send to Arduino
        if self.rpm >= 0:
            self.ser.write(b'F')
        else:
            self.ser.write(b'B')
        
    def rotate_single_step(self):
        # send step signal as one byte to Arduino and wait for half step duration
        self.ser.write(b'S')
        time.sleep(self.step_duration/2)
        # send hold signal as one byte to Arduino and wait for half step duration
        self.ser.write(b'H')
        time.sleep(self.step_duration/2)
        
    def open_connection(self):
        self.set_enable()
        self.set_direction()
        
    def close_connection(self):
        # set motor state to idle and close serial connection
        self.ser.write(b'H')
        self.ser.write(b'D')
        self.ser.close()
        
    def manual_control(self):
        # https://stackoverflow.com/questions/24072790/how-to-detect-key-presses/57644349#57644349
        # deleted a while True, try and except statement around the following, block;
        # not sure if needed, depends on use case...
        user_input = input('--> ')
        if user_input == "d":
            self.forward = True
            self.set_direction()
            self.rotate_single_step()
        if user_input == "a":
            self.forward = False
            self.set_direction()
            self.rotate_single_step() # backwards...
        if user_input == "w":
            for k in range(0,10):
                self.forward = True
                self.set_direction()
                self.rotate_single_step()
        if user_input == "s":
            for k in range(0,10):
                self.forward = False
                self.set_direction()
                self.rotate_single_step() # backwards...

            
    def move_steps(self, step_amount):
        for i in range(0, step_amount):
            try:
                # give instructions to the stepper motor
                self.rotate_single_step()
            except KeyboardInterrupt:
                break
         
