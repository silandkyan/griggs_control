# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:48:38 2024

@author: wq271
"""


# TODO: 
    # up / down (based on motor pos.)
#####   Importing Packages   #####
import os
os.chdir('C:/Users/wq271/AAA_programming/Projects/griggs_control/src')
from modules.GUI_v2 import run_app
# from modules.Motor import disconnect_motors


#####   Main GUI program starts here   #####
if __name__ == "__main__":
    # Start main program with event handling loop:
    try:
        app = run_app()
    except Exception:
        #pass
        print('ERROR')
    finally:
        pass
        # This should make a clean disconnect of the USB Serial connection 
        # after closing the main window or after an error:
        # disconnect_motors()