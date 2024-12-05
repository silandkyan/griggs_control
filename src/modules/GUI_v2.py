# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:29:45 2024

@author: wq271
"""

import sys
import time

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QLabel, QVBoxLayout, QDialog
from PyQt5.QtCore import  QEvent, Qt
from PyQt5.QtGui import QColor, QMouseEvent


from modules.gui.Tab_class import MyTabWidget

from modules.set_init_gui_settings_v2 import init_gui


from pytrinamic.connections import ConnectionManager

import pandas as pd 


import os
os.chdir('C:/Users/wq271/AAA_programming/Projects/griggs_control/src')
# print(os.getcwd())


# from modules.gui.main_window_Test import Ui_MainWindow #TODO

sys.path.append(r'C:\Users\wq271\AAA_programming\Projects\griggs_control\src\modules\gui')
# print(sys.modules)

from main_window_v1 import Ui_MainWindow #TODO

from modules.popup_warning_v0 import CustomDialog

# print(sys.modules)

'''TODO:
        - test 1000 bar label
        - test test get_adc (if print statement works use this also for gui_v3)'''


class Window(QMainWindow, Ui_MainWindow):
    
    valve_counter = 0
    booly = True
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.module_s1 = 's1'
        self.module_s3 = 's3'
        self.active_modules = []
        self.connectSignalsSlots()
        self.pushB_close_valve.setStyleSheet(f'color:{QColor(100, 200, 0)}')
        self.pushB_close_valve.pressed.connect(lambda: print(1))
        self.pushB_close_valve.released.connect(lambda: print(2))
        self.pushB_multi_up_s3.clicked.connect(lambda:print('yeeesssir'))
        self.pushB_perm_up_s3.clicked.connect(lambda: print('noosir'))
        self.pushB_multi_up_s3.setEnabled(False)
        self.pushB_perm_up_s3.setEnabled(False)
        self.pushB_perm_down_s3.pressed.connect(self.counter)
        self.pushB_perm_down_s3.released.connect(self.set_booly)
        self.pushB_get_adc.clicked.connect(lambda: print('channel sig1(value / voltage): 69 / 420 \n'
                                                      'channel sig3(value / voltage): 187 / 1312'))
        self.positions = pd.read_csv(
        r'C:\Users\wq271\AAA_programming\Projects\griggs_control\src\positions_valve.txt', sep='\t')
        self.valve_closed = self.positions.loc[0, 'closed']
        self.valve_distance = self.positions.loc[0, 'distance']
        self.valve_current = self.positions.loc[0, 'current']
        self.valve_opened = self.valve_closed + self.valve_distance
        self.label_s3.setText(f'{1000 - round(((self.valve_current - self.valve_closed)/self.valve_distance)*1000)} / 1000 bar')
        

    def set_default_values(self):
        pass
   
    def connectSignalsSlots(self):
        # self.tabWidget.setCurrentIndex(2)
        self.tabWidget.currentChanged.connect(lambda: self.refresh_module_list(
            (lambda i, arg: arg if i % 2 == 0 else None)(
                self.tabWidget.currentIndex(), 
                (lambda arg1, arg2: arg1 if self.tabWidget.currentIndex() < 2 else arg2)(self.module_s1, self.module_s3)
            )
        ))
        self.quitButton.clicked.connect(self.close)
        
    # def eventFilter(self, obj, event):
    #     print(f"Event type: {event.type()}, Object: {obj}")
    #     if isinstance(event, QMouseEvent):
    #         # Check if obj is in Tab2_widget_set and if it's a MouseButtonPress event
    #         if obj in self.Tab2_widget_set:  # Check if the clicked widget is in the set
    #             if event.type() == QEvent.MouseButtonPress:
    #                 self.oneshot = False
    #                 if (event.button() == Qt.LeftButton) or (event.button() == Qt.RightButton):
    #                     dialog = CustomDialog()
    #                     if dialog.exec_():  # Open as a modal dialog and check the return value
    #                         print("Dialog accepted!")
                    
    #         # Return True to stop the event from being propagated further, or False to allow default behavior
    #         return True  # We return True if we've handled the event (so it doesn't propagate)

    #     return False  # Otherwise, allow the event to be handled normally


    def counter(self):
        while Window.booly == True:
            QApplication.processEvents()
            Window.valve_counter += 1
            self.label_s3.setText(f'{Window.valve_counter} / 1000 bar')
            
    def set_booly(self):
        Window.booly = False
            
    def refresh_module_list(self, module):
        if module is not None:
            self.active_modules =  [module]
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
    init_gui(main_win)
    # Open GUI window on screen:
    main_win.show()
#     dialog = CustomDialog()
#     if dialog.exec_():  # Open as a modal dialog and check the return value
#         print("functions enabled!")   
    # Return an instance of a running QApplication = starts event handling
    return app.exec()
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    