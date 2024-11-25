# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 13:15:12 2024

@author: wq271
"""

from PyQt5.QtGui import QColor

def init_gui(win):
    ### color tabbar ###
    for i in range(0, 5):
        win.tabWidget.tabBar().setTabTextColor(i, QColor(255, 0, 0))
        if i>=2:
            win.tabWidget.tabBar().setTabTextColor(i, QColor(0, 128, 0))