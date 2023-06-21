# griggs_control
Collection of tools to control a Griggs-type apparatus via a computer.

## Prerequisites

- install Anaconda, PyTrinamic, PyQt5

- prepare breakout board and adc: https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/linux

1. install and configure libusb: 

2. verify that pyftdi and blinka are installed

3. in case of a langid error, correct the permission settings: "sudo adduser $USER plugdev"; see also: https://eblot.github.io/pyftdi/installation.html

4. re-plug the device and re-login to a new session!

5. install ADS115 driver from adafruit (via Spyder or Python shell): "pip install adafruit-circuitpython-ads1x15"

- setup Spyder so that all variables are cleared before execution (in the settings)

- what else?


## Setup of Raspberry Pi (probably not needed anymore...)

1. write PI OS (via Pi Imager) onto microSD card and insert it into a RPI

2. connect the RPI to periphery devices and boot

3. follow OS setup instructions

4. when booting was completed, establish a temporary internet connection (e.g. via smartphone hotspot)

5. install openconnect to establish LAN connections to the protected uni network: "sudo apt install openconnect"

6. connect to VPN with your URZ username and password: "sudo openconnect -u username -b vpn-ac.urz.uni-heidelberg.de" and then enter password

7. now switch to the permanent network connection (e.g. disable personal hotspot)

8. then you can install python packages and clone the needed github repos

9. after reboot, you need to reconnect to the vpn to have an internet connection

setup of I2C interface:
for communication with ADC board ADS1115, see e.g.:
https://wiki.seeedstudio.com/4-Channel_16-Bit_ADC_for_Raspberry_Pi-ADS1115/

1. "sudo raspi-config", navigate to interface options and enable I2C interface

2. reboot. I2C should be working now

