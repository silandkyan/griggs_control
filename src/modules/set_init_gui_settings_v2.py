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
    # win.Tab2_widget_set = {win.spinB_multistep_s3, win.pushB_multi_up_s3, 
    #                           win.pushB_perm_up_s3, win.pushB_stop_s3, win.pushB_perm_down_s3,
    #                           win.pushB_update_rpm_s3, win.rpmBox_s3, win.rpmSlider_s3, 
    #                           win.pushB_close_valve, win.pushB_set_closed}
    # for obj in win.Tab2_widget_set:
    #     obj.installEventFilter(win)