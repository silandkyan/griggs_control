# griggs_control
Collection of tools to control a Griggs-type apparatus via a computer.

## Prerequisites

- install Anaconda, PyTrinamic, PyQt5

- prepare breakout board and adc: [https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/](https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/running-circuitpython-code-without-circuitpython)

    1. install and configure libusb driver (or libusbk on Windows, with zadig), setup udev rules on linux
    2. verify that pyftdi and blinka are installed
    3. in case of a langid error, correct the permission settings: "sudo adduser $USER plugdev"; see also: https://eblot.github.io/pyftdi/installation.html
    4. re-plug the device and re-login to a new session!
    5. install ADS115 driver from adafruit (via Spyder or Python shell): "pip install adafruit-circuitpython-ads1x15"
    6. install pyqtgraph (via Spyder or Python shell): "conda install pyqtgraph"

- setup Spyder so that all variables are cleared before execution (in the settings)

- what else?


## Program structure

The actual program is found within the folder /griggs_control/src. The entire program consists of several subroutines and additional files that are organized in the following way:

```
├── /griggs_control/src             (main program folder)
│   ├── mocopa.py                   (main program; run this file with Python)
│   ├── act_vel.txt                 (file for externally saving of the motor rotation velocity during an experiment)
│   ├── time.txt                    (file for externally saving the timesteps of an experiment)
│   ├── /modules                    (all subroutines and other necessary files are stored here)
│   │   ├── Motor.py                (definition of Motor class, for motor management)
│   │   ├── Controller.py           (definition of Controller class for PID-controlled operation)
│   │   ├── GUI.py                  (definition of GUI behaviour)
│   │   ├── /gui                    (contains other GUI-related files)
│   │   │   ├── main_window_ui.py   (definition of GUI content and appearence)
│   │   │   ├── main window.ui      (XML-file, contains all GUI elements)
```

Important: Do NOT delete __init__.py files od __pycache__ folders, these are reqired and directly managed by Python.


## Functionality and GUI

The GUI currently offers 3 modes of operation, which are organized in tabs:

- Manual: Motor/piston movement and speed are controlled manually.
- Const Stress: Automatic motor/piston movement is PID-controlled, using &sigma;1 from continuous sensor reading as setpoint. 
- Quenching: Automatic piston retraction during experiment quenching is PID-controlled, using &Delta;&sigma; (from &sigma;1-&sigma;3 sensor reading) as setpoint.


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

TODO: prevent negative output mode of PID controller not working properly...

