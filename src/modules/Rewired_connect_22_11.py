# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:29:45 2024

@author: wq271
"""

import sys
import time

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import  QEvent

from modules.gui.Tab_class import MyTabWidget


from pytrinamic.connections import ConnectionManager

import pandas as pd 


import os
os.chdir('C:/Users/wq271/AAA_programming/Projects/griggs_control/src')
# print(os.getcwd())

from modules.gui.main_window_Test import Ui_MainWindow #TODO


class Window(QMainWindow, Ui_MainWindow):
    
    @staticmethod
    def first(bool1, bool2):
        if bool1 and not bool2:
            return True 
        else: 
            return False 
        
    @staticmethod
    def second(bool1, bool2):
        if bool2 and not bool1:
            return True 
        else:
            return False 
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.module_s1 = 's1'
        self.module_s3 = 's3'
        self.active_modules = []
        self.connectSignalsSlots()
        # print((lambda module: 'function 1 for module:' + module)(self.module_s1))
        

    def set_default_values(self):
        pass
   
    def connectSignalsSlots(self):
       self.tabWidget.currentChanged.connect(lambda: self.refresh_module_list((lambda index, arg1, arg2: arg1 if index<2 else arg2)
                                                                        (self.tabWidget.currentIndex(), self.module_s1, self.module_s3)))
    
    def refresh_module_list(self, module):
        self.active_modules = [module]
        print(f'module {module} selected')
    
    def multi_module_control(self, action):
        for module in self.active_modules:
            action(module)
            
            
            
def run_app():
    app = 0
    '''Initialize GUI control flow management. Requires passing argument 
    vector (sys.argv) or empty list [] as arg; the former allows to pass 
    configuration commands on startup to the program from the command 
    line, if such commands were implemented. If app is already open, 
    use that one, otherwise open new app:'''
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    # Create main window (= instance of custom Window Class):
    main_win = Window()
    # Open GUI window on screen:
    main_win.show()
    # Return an instance of a running QApplication = starts event handling
    return app.exec()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    