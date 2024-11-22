# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:46:11 2024

@author: wq271
"""

from PyQt5.QtWidgets import  QTabWidget
from PyQt5.QtCore import QEvent

class MyTabWidget(QTabWidget):
    oneshot = True
    def event(self, event):
        if event.type() == QEvent.MouseButtonPress:
            if MyTabWidget.oneshot == True:
                print("Please check the invert direction checkbox again!")
                MyTabWidget.oneshot = False
            else:
                pass
        return super().event(event)  # Call the base event handler