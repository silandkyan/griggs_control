#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 11:50:07 2023

@author: pgross
"""

import time

class Timer:
    '''gives functionality for non-blocking timed actions'''
    def __init__(self, t_ini, wait_duration):
        self.t_ini = t_ini
        self.wait_duration = wait_duration
        self.wait_since = self.t_ini
        self.counter = 0
        self.dt = 0
        self.run = False
        
    def wait(self):
        self.dt = time.time() - self.wait_since
        if self.dt < self.wait_duration:
            self.run = False
        elif self.dt >= self.wait_duration:
            self.counter += self.dt
            self.wait_since = time.time()
            self.run = True
