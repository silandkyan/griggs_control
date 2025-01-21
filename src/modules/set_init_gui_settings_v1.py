# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 13:15:12 2024

@author: wq271
"""

import time 

def init_gui(win):
    
    '''User input: Specify default values here.'''
    ### User input values (with allowed min-max ranges)
    # set initial Tab
    win.tabWidget.setCurrentIndex(2)
    # rpm for all constant speed modes (single, multi, constant):
    win.rpmBox_s3.setValue(10)    # default rpm
    win.rpmBox_s1.setValue(10) 
    # adjust slider position to match rpmBox value:
    win.rpmSlider_s1.setValue(int(round(win.rpmBox_s1.value() * win.module_s1.msteps_per_rev/60)))
    win.rpmSlider_s3.setValue(int(round(win.rpmBox_s3.value() * win.module_s3.msteps_per_rev/60)))
    # initial calculation of pps:
    win.module_s1.rpm = win.rpmBox_s1.value()
    win.module_s3.rpm = win.rpmBox_s3.value()
    win.module_s1.update_pps()
    win.module_s3.update_pps()
    win.write_stress = False
    # win.enable_display_stress = False 
    win.invert_checkBox.setChecked(False)
    # set initial stress setpoint value:
    win.sigma1_SP_spinBox.setValue(0)
    win.dsigma_SP_spinBox.setValue(0)
    # set initial maxvel value:
    win.maxvel_spinBox.setValue(120)
    win.module_s1.maxvel = win.maxvel_spinBox.value()
    win.module_s3.maxvel = 60
    # disable usability for opening valve functions in manual s3 mode
    win.pushB_multi_up_s3.setEnabled(False)
    win.pushB_perm_up_s3.setEnabled(False)
    # set color of clo0sed button default to opened:
    # win.pushB_close_valve.setStyleSheet('color: rgb(200, 50, 0)')
    
    '''init graph window'''
    win.graphWidget.setBackground('w')
    win.graphWidget.addLegend()
    win.graphWidget.setLabel('left', 'velocity (rpm)')
    win.graphWidget.setLabel('bottom', 'time (s)')
    # s1/PID
    win.line1 = win.plot(win.time, win.act_vel_s1, 'actual velocity s1', 'k')
    win.line2 = win.plot(win.time, win.set_vel, 'set velocity', 'b')
    win.line3 = win.plot(win.time, win.sigma1_SP, 'SP', 'c')
    win.line4 = win.plot(win.time, win.sigma1_PV, 'PV', 'g')
    win.line5 = win.plot(win.time, win.error, 'error', 'r')
    # s3
    win.line6 = win.plot(win.time, win.act_vel_s3, 'actual velocity s3', 'y') 
    # LCDs:
    win.lcd_actvel_s1.display(win.pps_rpm_converter(win.module_s1, abs(win.motor_s1.actual_velocity)))
    win.lcd_actvel_s3.display(win.pps_rpm_converter(win.module_s3, abs(win.motor_s3.actual_velocity)))
    
    '''Specify allowed min-max ranges for values that can 
    be changed in the GUI. These should usually be fine...'''
    ### User input values (with allowed min-max ranges)
    # rpm for all constant speed modes (single, multi, constant):
    win.rpmBox_s1.setMinimum(0)
    win.rpmBox_s1.setMaximum(120)
    win.rpmBox_s3.setMinimum(0)
    win.rpmBox_s3.setMaximum(120)
    # set slider limits and position
    win.rpmSlider_s1.setMinimum(int(round(win.rpmBox_s1.minimum() * win.module_s1.msteps_per_rev / 60)))
    win.rpmSlider_s1.setMaximum(int(round(win.rpmBox_s1.maximum() * win.module_s1.msteps_per_rev / 60)))
    win.rpmSlider_s3.setMinimum(int(round(win.rpmBox_s3.minimum() * win.module_s3.msteps_per_rev / 60)))
    win.rpmSlider_s3.setMaximum(int(round(win.rpmBox_s3.maximum() * win.module_s3.msteps_per_rev / 60)))
    # amount of single steps in multistep mode:
    win.spinB_multistep_s3.setMinimum(0)
    win.spinB_multistep_s3.setMaximum(2000)
    win.spinB_multistep_s1.setMinimum(0)
    win.spinB_multistep_s1.setMaximum(360)
    # set maxvel spinBox:
    win.maxvel_spinBox.setMinimum(0)
    win.maxvel_spinBox.setMaximum(120)
    
    # '''init data containers for graph'''
    # win.data_chunk_size = 99
    # win.savecounter = 1 # != 0 because of initialization, etc.
    # win.time = [0] # time
    # win.t0 = time.time()
    # win.act_vel_s3 = [win.pps_rpm_converter(win.module_s3, abs(win.motor_s3.actual_velocity))]
    # win.act_vel_s1 = [win.pps_rpm_converter(win.module_s1, abs(win.motor_s1.actual_velocity))]
    # win.set_vel = [win.pps_rpm_converter(win.module_s1, win.module_s1.pps)]
    # # win.SP = [win.setpointSlider.value()]
    # win.sigma1_SP = [win.sigma1_SP_spinBox.value()]
    # win.dsigma_SP = [win.dsigma_SP_spinBox.value()]
    # if win.initADC_s1.isChecked() == True:
    #     win.sigma1_PV = [int(win.chan_s1.value/win.adc_sigma1_scaling)]
    #     # win.PV = [win.procvarSlider.value()]
    #     if win.initADC_s3.isChecked() == True:
    #         win.sigma3_PV = [int(win.chan_s3.value/win.adc_sigma3_scaling)]
    #         win.dsigma_PV = [win.sigma1_PV[0] - win.sigma3_PV[0]]
    #     else:
    #         win.sigma3_PV = [0]
    #         win.dsigma_PV = [0]
    # else:
    #     win.sigma1_PV = [0]
    #     win.sigma3_PV = [0]
    #     win.dsigma_PV = [0]
    #     # win.PV = [win.procvarSlider.value()]
    # # win.CV = [0]
    # # win.error = [0, 0, 0]
    # win.error = [win.sigma1_SP[-1] - win.sigma1_PV[-1]]
    # # print(win.time, win.act_vel, win.set_vel)
    # win.init_save_files()