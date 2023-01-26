#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 11:50:07 2023

@author: pgross
"""

import time

class Timer:
    '''gives functionality for non-blocking timed actions'''
    def __init__(self, t_ini, interval):
        self.t_ini = t_ini
        self.interval = interval
        self.wait_since = self.t_ini
        self.dt_counter = [0]
        self.dt = 0
        self.last_dt = 0
        self.run = False
        self.first_halfstep = 0
        self.second_halfstep = 0
        
    def clock(self):
        '''Gives short signal pulses (True) at precise time intervals.
        Interval duration is given by "interval" value.'''
        self.dt = time.time() - self.wait_since
        if self.dt < self.interval:
            self.run = False
        elif self.dt >= self.interval:
            self.dt_counter.append(self.dt + self.dt_counter[-1])
            self.wait_since = time.time()
            self.run = True
            
    def wait(self):
        '''Gives alternating signals (True-False) for specified time intervals.
        The "interval" value defines the duration of one True-False cycle.
        The individual signal duration is therefore interval/2.'''
        self.dt = time.time() - self.wait_since
        if self.dt < self.interval/2:
            self.run = False
        elif self.dt >= self.interval/2 and self.dt < self.interval:
            self.run = True
        elif self.dt >= self.interval:
            self.dt_counter.append(self.dt + self.dt_counter[-1])
            self.wait_since = time.time()
            self.run = False
        #print(self.interval/2, round(self.dt, 4), round(self.dt_counter[-1], 4), self.run)
        

if False:
    import matplotlib.pyplot as plt
    step = 0.1 # base rate of commands, in sec
    timer = Timer(time.time(), step)
    while True:
        try:
            timer.clock()
            if timer.run == True:
                print('---> ', timer.dt_counter[-1])
                plt.clf()
                plt.plot(timer.dt_counter[-10:],'o-')
                plt.draw()
                plt.pause(0.0001)
            time.sleep(0.01)
        except KeyboardInterrupt:
            break
