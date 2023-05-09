#!/bin/python
# -*- coding: utf-8 -*-

###Author: Jan Schmitt, Dec 2022
###Script for automatised batch-processing of single peak fitting.
###This script combines own approaches, parts of the lmfit documentation and the script of Charles Le Losq (2015, https://notebook.community/charlesll/RamPy/examples/Raman_spectrum_fitting)

"""pyinstaller can be used in cmd to create a single .exe file from the script. One must only keep in mind to add the images in a separate folder ./images/ lateron
cmd entry (after cd to directory of file:
pyinstaller --onefile Script.py
"""

##Import packages
import sys
import os
import time
#import numpy as np
#import scipy
#import random
#import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
#from datetime import datetime, timedelta
#import shutil
import threading
from threading import Thread
from threading import Event

#Packages for GUI
import pylab
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Label
from tkinter import filedialog as fd

#Custom colours
#blau = np.array([.326,.455,.733])
#gruen = np.array([.478,.702,.137])
#gelb = np.array([.984,.753,0])
#rot = np.array([.737,.153,.106])

#####Main window (root)#####
root =tk.Tk()
root.title('Griggs Control')
window_width = 680
window_height = 650
#Get screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
#Find center point
center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)
#Define geometry
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

#Define date format for the estimated analysis time
format = "%d.%m.%Y  %H:%M:%S"
#Define error messages
err1 = "Invalid ranges for baseline removal and/or fitting.\nThe values must be set from the lower to the higher boundary."
err2 = "Invalid entry. Please check that all the values are numbers."
err3 = 'Invalid entry for the R^2 threshold:\n0.00 <= R^2 <= 1.00'
err4 = 'Invalid directories. Please check destinations of input and output.\nIf you aborted the file dialog, please reselect your desired destination.'
err5 = 'Invalid values. Please check that no negative values are given.'

#####Info text for introduction#####
intro = Label(root, text='Griggs and PE control tool.', font='Helvetica 10')
intro.grid(columnspan=5, row=0, sticky=tk.N, padx=5, pady=10)

#####NOTEBOOK#####
notebook = ttk.Notebook(root)
notebook.grid(column=0, row=2, columnspan=5, pady=10)
#Create frames and add titles
frame1 = ttk.Frame(notebook, width=600, height=200)
frame2 = ttk.Frame(notebook, width=600, height=200)
frame3 = ttk.Frame(notebook, width=600, height=200)
notebook.add(frame1, text='Control')
notebook.add(frame2, text='Settings')
notebook.add(frame3, text='Information')

off_color = 'gray'
on_color = 'black'
#off_status = "Helvetica 10"
#on_status = "Helvetica 10 bold"

#####Frame 1 - Control#####
frame1.grid_columnconfigure(4, minsize=50)
frame1.grid_rowconfigure(13, minsize=15)
frame1.grid_rowconfigure(18, minsize=15)
frame1.grid_rowconfigure(21, minsize=25)
##Variables##
PosCont_Rev = tk.IntVar()
PosCont_DegOnAxis = tk.DoubleVar()
PosCont_RPM = tk.IntVar()

Perma_Forward = tk.IntVar()
Perma_Backward = tk.IntVar()
Perma_RPM = tk.IntVar()

WhenPush_RPM = tk.IntVar()

i=0 #Dummy variable for movement

##1 Position Control##
#Title
PosCont_isActive = 0
def PosCont_Active():
	global PosCont_isActive
	if PosCont_isActive == 0:
		PosCont_isActive = 1
		PosCont_label.configure(fg='red')
		PosCont_Rev_label["fg"] = on_color
		PosCont_Rev_entry.config(foreground=on_color,state='enabled')
		PosCont_DegOnAxis_label["fg"] = on_color
		PosCont_DegOnAxis_entry.config(foreground=on_color,state='enabled')
		PosCont_RPM_label["fg"] = on_color
		PosCont_RPM_entry.config(foreground=on_color,state='enabled')
		PosCont_GoTo_but.state(["!disabled"])
		PosCont_Stop_but.state(["!disabled"])
	else:
		PosCont_isActive = 0
		PosCont_label.configure(fg='grey')
		PosCont_Rev_label["fg"] = off_color
		PosCont_Rev_entry.config(foreground=off_color,state='disabled')
		PosCont_DegOnAxis_label["fg"] = off_color
		PosCont_DegOnAxis_entry.config(foreground=off_color,state='disabled')
		PosCont_RPM_label["fg"] = off_color
		PosCont_RPM_entry.config(foreground=off_color,state='disabled')
		PosCont_GoTo_but.state(["disabled"])
		PosCont_Stop_but.state(["disabled"])
		
PosCont_label = tk.Button(frame1, text='1. Position Control', fg=off_color, command=PosCont_Active, relief='ridge', font='Helvetica 10 bold')
PosCont_label.grid(column=0, row=8, columnspan=2, sticky=tk.W, padx=5, pady=5)

#Revolutions
PosCont_Rev_label = tk.Label(frame1, text='Revolutions', foreground=off_color)
PosCont_Rev_label.grid(column=1, row=9, padx=5, pady=5, sticky=tk.W)
PosCont_Rev_entry = ttk.Entry(frame1, textvariable=PosCont_Rev, width=10, state='disabled')
PosCont_Rev_entry.grid(column=2, row=9, columnspan=2, sticky=tk.W, padx=5, pady=5)

#Degrees/mm on axis
PosCont_DegOnAxis_label = tk.Label(frame1, text='Degree/mm on Axis', foreground=off_color)
PosCont_DegOnAxis_label.grid(column=1, row=10, padx=5, pady=5, sticky=tk.W)
PosCont_DegOnAxis_entry = ttk.Entry(frame1, textvariable=PosCont_DegOnAxis, width=10, state='disabled')
PosCont_DegOnAxis_entry.grid(column=2, row=10, columnspan=2, sticky=tk.W, padx=5, pady=5)

#RPM
PosCont_RPM_label = tk.Label(frame1, text='RPM', foreground=off_color)
PosCont_RPM_label.grid(column=1, row=11, padx=5, pady=5, sticky=tk.W)
PosCont_RPM_entry = ttk.Entry(frame1, textvariable=PosCont_RPM, width=10, state='disabled')
PosCont_RPM_entry.grid(column=2, row=11, columnspan=2, sticky=tk.W, padx=5, pady=5)

#Go to button
def PosCont_GoTo():
	"""Function to move to desired position"""
	
def PosCont_Stop():
	"""Stop movement"""
	
PosCont_GoTo_but = ttk.Button(frame1, text='Go To', command=PosCont_GoTo)
PosCont_GoTo_but.grid(column=1,columnspan=1, row=12, rowspan=2, padx=5, pady=5)
PosCont_GoTo_but.state(["disabled"])

#Stop button
PosCont_Stop_but = ttk.Button(frame1, text='STOP', command=PosCont_Stop)
PosCont_Stop_but.grid(column=2,columnspan=1, row=12, rowspan=2, padx=5, pady=5)
PosCont_Stop_but.state(["disabled"])

##2 Permanent##
#Title
Perma_isActive = 0
def Perma_Active():
	global Perma_isActive
	if Perma_isActive == 0:
		Perma_isActive = 1
		Perma_label.configure(fg='red')
		Perma_Forward_check.configure(state='enabled')
		Perma_Backward_check.configure(state='enabled')
		Perma_Stop_but.state(["!disabled"])
		Perma_RPM_label["fg"] = on_color
		Perma_RPM_entry.config(foreground=off_color,state='enabled')
		
	else:
		Perma_isActive = 0
		Perma_label.configure(fg='gray')
		Perma_Forward_check.configure(state='disabled')
		Perma_Backward_check.configure(state='disabled')
		Perma_Stop_but.state(["disabled"])
		Perma_RPM_label["fg"] = off_color
		Perma_RPM_entry.config(foreground=off_color,state='disabled')


Perma_label = tk.Button(frame1, text='2. Permanent', fg=off_color, command=Perma_Active, relief='ridge', font='Helvetica 10 bold')
Perma_label.grid(column=0, row=14, columnspan=2, sticky=tk.W, padx=5, pady=5)

Perma_Fwd = False
Perma_Bwd = False

event_Fwd = Event()
event_Bwd = Event()

def Perma_Movement_Fwd():
	global i
	global Perma_Fwd
	global event_Fwd
	event_Fwd.clear()
	while Perma_Fwd == True:
		time.sleep(0.5)
		i += int(Perma_RPM_entry.get())
		print(i)
		if event_Fwd.is_set():
			break
	else:
		event_Fwd.set()

#Forward
def check_forward():#change text colour when activated and uncheck backward movement
	if Perma_Forward.get() == 1:
		Perma_Forward_label["fg"] = on_color
		global Perma_Fwd
		global Perma_Bwd
		Perma_Fwd = True
		if Perma_Fwd == True:
			Perma_Bwd = False
			Perma_Thread = Thread(target=Perma_Movement_Fwd, args=())
			Perma_Thread.start()
	else:
		Perma_Forward_label["fg"] = off_color
		Perma_Fwd = False
		
	if Perma_Backward.get() == 1:
		Perma_Backward.set(0)
		Perma_Backward_label["fg"] = off_color
	else:
		pass
		
Perma_Forward_check = ttk.Checkbutton(frame1, command=check_forward, variable=Perma_Forward, onvalue = 1, offvalue = 0, state='disabled')
Perma_Forward_check.grid(column=0, row=15, padx=5, pady=5)
Perma_Forward_label = tk.Label(frame1, text='Forward', font='Helvetica 10', foreground=off_color)
Perma_Forward_label.grid(column=1, row=15, sticky=tk.W, padx=5, pady=5)

#Backward
def Perma_Movement_Bwd():
	global i
	global Perma_Bwd
	global event_Bwd
	event_Bwd.clear()
	while Perma_Bwd == True:
		time.sleep(0.5)
		i -= int(Perma_RPM_entry.get())
		print(i)
		if event_Bwd.is_set():
			break
	else:
		event_Bwd.set()


def check_backward():#change text colour when activated and uncheck forward movement
	if Perma_Backward.get() == 1:
		Perma_Backward_label["fg"] = on_color
		global Perma_Bwd
		global Perma_Fwd
		Perma_Bwd = True
		if Perma_Bwd == True:
			Perma_Fwd = False
			Perma_Thread = Thread(target=Perma_Movement_Bwd, args=())
			Perma_Thread.start()
	else:
		Perma_Backward_label["fg"] = off_color
		Perma_Bwd = False
		
	if Perma_Forward.get() == 1:
		Perma_Forward.set(0)
		Perma_Forward_label["fg"] = off_color
	else:
		pass
		
Perma_Backward_check = ttk.Checkbutton(frame1, command=check_backward, variable=Perma_Backward, onvalue = 1, offvalue = 0, state='disabled')
Perma_Backward_check.grid(column=0, row=16, padx=5, pady=5)
Perma_Backward_label = tk.Label(frame1, text='Backward', font='Helvetica 10', foreground=off_color)
Perma_Backward_label.grid(column=1, row=16, sticky=tk.W, padx=5, pady=5)

#Stop
def Perma_Stop():
	global Perma_Fwd
	global Perma_Bwd
	Perma_Forward.set(0)
	Perma_Forward_label["fg"] = off_color
	Perma_Fwd = False
	Perma_Backward.set(0)
	Perma_Backward_label["fg"] = off_color
	Perma_Bwd = False

Perma_Stop_but = ttk.Button(frame1, text='STOP', command=Perma_Stop)
Perma_Stop_but.grid(column=2,columnspan=1, row=15, rowspan=2, padx=5, pady=5)
Perma_Stop_but.state(["disabled"])

#RPM
Perma_RPM_label = tk.Label(frame1, text='RPM', foreground=off_color)
Perma_RPM_label.grid(column=1, row=17, padx=5, pady=5)
Perma_RPM_entry = ttk.Entry(frame1, textvariable=Perma_RPM, width=10, state='disabled')
Perma_RPM_entry.grid(column=2, row=17, columnspan=2, sticky=tk.W, padx=5, pady=5)


##3 When Pushed##
#Title
WhenPush_isActive = 0
def WhenPush_Active():
	global WhenPush_isActive
	if WhenPush_isActive == 0:
		WhenPush_isActive = 1
		WhenPush_label.configure(fg='red')
		WhenPush_RPM_label["fg"] = on_color
		WhenPush_RPM_entry.config(foreground=on_color,state='enabled')
		WhenPush_Forward_but.state(["!disabled"])
		WhenPush_Backward_but.state(["!disabled"])
		WhenPush_Forward_but.bind('<ButtonPress-1>',WhenPushed_Move_Forward)
		WhenPush_Forward_but.bind('<ButtonRelease-1>',WhenPushed_Stop_Forward)
		WhenPush_Backward_but.bind('<ButtonPress-1>',WhenPushed_Move_Backward)
		WhenPush_Backward_but.bind('<ButtonRelease-1>',WhenPushed_Stop_Backward)
	else:
		WhenPush_isActive = 0
		WhenPush_label.configure(fg='grey')
		WhenPush_RPM_label["fg"] = off_color
		WhenPush_RPM_entry.config(foreground=off_color,state='disabled')
		WhenPush_Forward_but.state(["disabled"])
		WhenPush_Backward_but.state(["disabled"])
		WhenPush_Forward_but.unbind('<ButtonPress-1>')
		WhenPush_Forward_but.unbind('<ButtonRelease-1>')
		WhenPush_Backward_but.unbind('<ButtonPress-1>')
		WhenPush_Backward_but.unbind('<ButtonRelease-1>')
		
WhenPush_label = tk.Button(frame1, text='3. When pushed', fg=off_color, command=WhenPush_Active, relief='ridge', font='Helvetica 10 bold')
WhenPush_label.grid(column=5, row=14, columnspan=2, sticky=tk.W, padx=5, pady=5)

#Move Forward
WhenPushed_Forward = False
event = Event()

def WhenPushed_Movement_Fwd():
	global i
	global WhenPushed_Forward
	global event
	event.clear()
	while WhenPushed_Forward == True:
		time.sleep(0.5)
		i += int(WhenPush_RPM_entry.get())
		print(i)
		if event.is_set():
			break
	else:
		event.set()

def WhenPushed_Move_Forward(*unused):
	global WhenPushed_Forward
	WhenPushed_Forward = True
	if WhenPushed_Forward == True:
		WhenPushed_Thread = Thread(target=WhenPushed_Movement_Fwd, args=())
		WhenPushed_Thread.start()
		"""print("Is thread alive?")
		print(id(WhenPushed_Thread)) #id of thread instances
		print("All threads running:")
		for thread in threading.enumerate(): #to check that the threads are actually terminated
			print(thread.name)
		print("\n\n")"""


def WhenPushed_Stop_Forward(*unused):
	global WhenPushed_Forward
	WhenPushed_Forward = False
	#print(WhenPushed_Forward)	

#Forward Button
WhenPush_Forward_but = ttk.Button(frame1, text='Forward')
WhenPush_Forward_but.grid(column=6,columnspan=1, row=15, padx=5, pady=5)
WhenPush_Forward_but.state(["disabled"])

#Move Backward
WhenPushed_Backward = False
event = Event()

def WhenPushed_Movement_Bwd():
	global i
	global WhenPushed_Backward
	global event
	event.clear()
	while WhenPushed_Backward == True:
		time.sleep(0.5)
		i -= int(WhenPush_RPM_entry.get())
		print(i)
		if event.is_set():
			break
	else:
		event.set()

def WhenPushed_Move_Backward(*unused):
	global WhenPushed_Backward
	WhenPushed_Backward = True
	if WhenPushed_Backward == True:
		WhenPushed_Thread = Thread(target=WhenPushed_Movement_Bwd, args=())
		WhenPushed_Thread.start()

def WhenPushed_Stop_Backward(*unused):
	global WhenPushed_Backward
	WhenPushed_Backward = False


#Backward Button
WhenPush_Backward_but = ttk.Button(frame1, text='Backward')
WhenPush_Backward_but.grid(column=6,columnspan=1, row=16, padx=5, pady=5)
WhenPush_Backward_but.state(["disabled"])

#RPM
WhenPush_RPM_label = tk.Label(frame1, text='RPM', foreground=off_color)
WhenPush_RPM_label.grid(column=5, row=17, padx=5, pady=5)
WhenPush_RPM_entry = ttk.Entry(frame1, textvariable=WhenPush_RPM, width=10, state='disabled')
WhenPush_RPM_entry.grid(column=6, row=17, columnspan=2, sticky=tk.W, padx=5, pady=5)


##4 Keyboard Control##
#Title
Key_isActive = 0
def Key_Active():
	global Key_isActive
	if Key_isActive == 0:
		Key_isActive = 1
		Key_label.configure(fg='red')
		Key_info["fg"] = on_color
		root.bind('<Up>',Key_Up)
		root.bind('<Down>',Key_Down,'+')
		root.bind('<Left>',Key_Left,'+')
		root.bind('<Right>',Key_Right,'+')
		#WhenPush_RPM_label["fg"] = on_color
		#WhenPush_RPM_entry.config(foreground=on_color,state='enabled')
		#WhenPush_Forward_but.state(["!disabled"])
		#WhenPush_Backward_but.state(["!disabled"])
	else:
		Key_isActive = 0
		Key_label.configure(fg='grey')
		Key_info["fg"] = off_color
		root.unbind('<Up>')
		root.unbind('<Down>')
		root.unbind('<Left>')
		root.unbind('<Right>')
		#WhenPush_RPM_label["fg"] = off_color
		#WhenPush_RPM_entry.config(foreground=off_color,state='disabled')
		#WhenPush_Forward_but.state(["disabled"])
		#WhenPush_Backward_but.state(["disabled"])
		
Key_label = tk.Button(frame1, text='4. Keyboard Control', fg=off_color, command=Key_Active, relief='ridge', font='Helvetica 10 bold')
Key_label.grid(column=0, row=19, columnspan=2, sticky=tk.W, padx=5, pady=5)

Key_Up_val = 10
Key_Down_val = 10
Key_Left_val = 1
Key_Right_val = 1

def Key_Up(*unused):
	global i
	global Key_Up_val
	i += Key_Up_val
	print(i)#

def Key_Down(*unused):
	global i
	global Key_Down_val
	i -= Key_Down_val
	print(i)#
	
def Key_Left(*unused):
	global i
	global Key_Left_val
	i -= Key_Left_val
	print(i)#

def Key_Right(*unused):
	global i
	global Key_Right_val
	i += Key_Right_val
	print(i)#
	
Key_info = tk.Label(frame1, text='Used for small adjustments.\nClicking and holding the keyboard arrows produces a defined motion distance.\nKeyboard arrows control the number of steps. Check settings for details.'	, font='Helvetica 10', justify='left', fg=off_color)
Key_info.grid(column=1, columnspan=10, row=20, sticky=tk.W, padx=5, pady=5)

##Short Info##
Gen_title_info = tk.Label(frame1, text='Information:'	, font='Helvetica 10 bold', justify='left')
Gen_title_info.grid(column=0, columnspan=10, row=22, sticky=tk.W, padx=5, pady=5)
Gen_info = tk.Label(frame1, text='- Usually 30-120 RPM is a good choice. At higher RPM, torque decreases.\n- ...', font='Helvetica 10', justify='left')
Gen_info.grid(column=0, columnspan=10, row=23, sticky=tk.W, padx=5, pady=5)


##Go To Shortcuts##
GoTo_info = tk.Label(frame1, text='Go to:'	, font='Helvetica 10 bold', justify='left')
GoTo_info.grid(column=5, columnspan=2, row=8, sticky=tk.W, padx=5, pady=5)

GoTo_PosA_but = ttk.Button(frame1, text='Pos. A')
GoTo_PosA_but.grid(column=5,columnspan=1, row=9, padx=5, pady=5)
GoTo_PosB_but = ttk.Button(frame1, text='Pos. B')
GoTo_PosB_but.grid(column=5,columnspan=1, row=10, padx=5, pady=5)
GoTo_PosC_but = ttk.Button(frame1, text='Pos. C')
GoTo_PosC_but.grid(column=5,columnspan=1, row=11, padx=5, pady=5)
GoTo_PosD_but = ttk.Button(frame1, text='Pos. D')
GoTo_PosD_but.grid(column=5,columnspan=1, row=12, padx=5, pady=5)

PosA = [0,0] #[Rev,mm]
PosB = [100,200]
PosC = [500,1000]
PosD = [2000,4000]

GoTo_Rev_label = tk.Label(frame1, text='Rev.' , font='Helvetica 10')
GoTo_Rev_label.grid(column=6, columnspan=1, row=8, sticky=tk.S, padx=5, pady=5)
GoTo_mm_label = tk.Label(frame1, text='mm' , font='Helvetica 10')
GoTo_mm_label.grid(column=7, columnspan=1, row=8, sticky=tk.S, padx=5, pady=5)

GoTo_PosA_rev = tk.Label(frame1, text=PosA[0] , font='Helvetica 10')
GoTo_PosA_rev.grid(column=6, columnspan=1, row=9, sticky=tk.S, padx=5, pady=5)
GoTo_PosA_mm = tk.Label(frame1, text=PosA[1] , font='Helvetica 10')
GoTo_PosA_mm.grid(column=7, columnspan=1, row=9, sticky=tk.S, padx=5, pady=5)

GoTo_PosB_rev = tk.Label(frame1, text=PosB[0] , font='Helvetica 10')
GoTo_PosB_rev.grid(column=6, columnspan=1, row=10, sticky=tk.S, padx=5, pady=5)
GoTo_PosB_mm = tk.Label(frame1, text=PosB[1] , font='Helvetica 10')
GoTo_PosB_mm.grid(column=7, columnspan=1, row=10, sticky=tk.S, padx=5, pady=5)

GoTo_PosC_rev = tk.Label(frame1, text=PosC[0] , font='Helvetica 10')
GoTo_PosC_rev.grid(column=6, columnspan=1, row=11, sticky=tk.S, padx=5, pady=5)
GoTo_PosC_mm = tk.Label(frame1, text=PosC[1] , font='Helvetica 10')
GoTo_PosC_mm.grid(column=7, columnspan=1, row=11, sticky=tk.S, padx=5, pady=5)

GoTo_PosD_rev = tk.Label(frame1, text=PosD[0] , font='Helvetica 10')
GoTo_PosD_rev.grid(column=6, columnspan=1, row=12, sticky=tk.S, padx=5, pady=5)
GoTo_PosD_mm = tk.Label(frame1, text=PosD[1] , font='Helvetica 10')
GoTo_PosD_mm.grid(column=7, columnspan=1, row=12, sticky=tk.S, padx=5, pady=5)

def OW_Pos():
	"""function to overwrite position"""

PosA_OW = tk.Button(frame1, text='OW', command=OW_Pos, relief='groove', font='Helvetica 10')
PosA_OW.grid(column=8, row=9, columnspan=2, sticky=tk.W, padx=5, pady=5)
PosB_OW = tk.Button(frame1, text='OW', command=OW_Pos, relief='groove', font='Helvetica 10')
PosB_OW.grid(column=8, row=10, columnspan=2, sticky=tk.W, padx=5, pady=5)
PosC_OW = tk.Button(frame1, text='OW', command=OW_Pos, relief='groove', font='Helvetica 10')
PosC_OW.grid(column=8, row=11, columnspan=2, sticky=tk.W, padx=5, pady=5)
PosD_OW = tk.Button(frame1, text='OW', command=OW_Pos, relief='groove', font='Helvetica 10')
PosD_OW.grid(column=8, row=12, columnspan=2, sticky=tk.W, padx=5, pady=5)

"""###FRAME 3 - Information###
info = tk.Label(frame3, text=''	, font='Helvetica 10', justify='left')
info.grid(column=0, columnspan=10, row=11, sticky=tk.W, padx=5, pady=5)
"""

###FOOTNOTE###
footnote = Label(root, text='2023', font='Helvetica 10 italic')
footnote.grid(columnspan=5, row=22, sticky=tk.S, padx=5, pady=5)

root.mainloop()
