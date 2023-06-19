#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 10:19:13 2023

@author: pgross

prerequisites: https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/linux
    1. install and configure libusb: 
    2. verify that pyftdi and blinka are installed
    3. in case of a langid error, correct the permission settings: "sudo adduser $USER plugdev"
        see also: https://eblot.github.io/pyftdi/installation.html
    4. re-plug the device and re-login to a new session!
    

"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 1
chan = AnalogIn(ads, ADS.P1)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}".format('raw', 'v'))

# track time
# t0 = time.time()

while True:
    t0 = time.time()
    print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
    time.sleep(0.5)
    print(round(time.time() - t0, 2))
