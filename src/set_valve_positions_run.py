#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 16:38:18 2023

@author: pgross

When running this program with Spyder, make sure that all variables are 
cleared before execution in the settings.
"""

#####   Importing Packages   #####

from modules.set_valve_positions import run_app
# from modules.gui.gui_simple import run_app
from modules.Motor import disconnect_motors


#####   Main GUI program starts here   #####
if __name__ == "__main__":
    # Start main program with event handling loop:
    try:
        app = run_app()
    except Exception:
        #pass
        print('ERROR')
    finally:
        # This should make a clean disconnect of the USB Serial connection 
        # after closing the main window or after an error:
        disconnect_motors()



