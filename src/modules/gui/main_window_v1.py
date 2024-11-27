# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(835, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.quitButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitButton.setGeometry(QtCore.QRect(20, 380, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.quitButton.setFont(font)
        self.quitButton.setObjectName("quitButton")
        self.graphWidget = PlotWidget(self.centralwidget)
        self.graphWidget.setGeometry(QtCore.QRect(10, 430, 801, 211))
        self.graphWidget.setObjectName("graphWidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 0, 391, 371))
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setObjectName("tabWidget")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.rpmSlider_s1 = QtWidgets.QSlider(self.tab_4)
        self.rpmSlider_s1.setGeometry(QtCore.QRect(29, 250, 321, 20))
        self.rpmSlider_s1.setMinimum(-120)
        self.rpmSlider_s1.setMaximum(120)
        self.rpmSlider_s1.setOrientation(QtCore.Qt.Horizontal)
        self.rpmSlider_s1.setObjectName("rpmSlider_s1")
        self.pushB_multi_down_s1 = QtWidgets.QPushButton(self.tab_4)
        self.pushB_multi_down_s1.setGeometry(QtCore.QRect(310, 80, 61, 41))
        self.pushB_multi_down_s1.setObjectName("pushB_multi_down_s1")
        self.label_20 = QtWidgets.QLabel(self.tab_4)
        self.label_20.setGeometry(QtCore.QRect(190, 51, 81, 20))
        self.label_20.setObjectName("label_20")
        self.label_21 = QtWidgets.QLabel(self.tab_4)
        self.label_21.setGeometry(QtCore.QRect(190, 40, 81, 16))
        self.label_21.setObjectName("label_21")
        self.rpmBox_s1 = QtWidgets.QDoubleSpinBox(self.tab_4)
        self.rpmBox_s1.setGeometry(QtCore.QRect(200, 210, 81, 31))
        self.rpmBox_s1.setDecimals(4)
        self.rpmBox_s1.setObjectName("rpmBox_s1")
        self.label_22 = QtWidgets.QLabel(self.tab_4)
        self.label_22.setGeometry(QtCore.QRect(20, 17, 171, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_22.setFont(font)
        self.label_22.setStyleSheet("QLabel{color: rgb(255, 0, 0);}")
        self.label_22.setObjectName("label_22")
        self.label_23 = QtWidgets.QLabel(self.tab_4)
        self.label_23.setGeometry(QtCore.QRect(20, 80, 81, 31))
        self.label_23.setObjectName("label_23")
        self.spinB_multistep_s1 = QtWidgets.QDoubleSpinBox(self.tab_4)
        self.spinB_multistep_s1.setGeometry(QtCore.QRect(90, 90, 71, 26))
        self.spinB_multistep_s1.setMaximum(360.0)
        self.spinB_multistep_s1.setProperty("value", 30.0)
        self.spinB_multistep_s1.setObjectName("spinB_multistep_s1")
        self.label_24 = QtWidgets.QLabel(self.tab_4)
        self.label_24.setGeometry(QtCore.QRect(320, 50, 81, 21))
        self.label_24.setObjectName("label_24")
        self.pushB_perm_up_s1 = QtWidgets.QPushButton(self.tab_4)
        self.pushB_perm_up_s1.setGeometry(QtCore.QRect(180, 140, 61, 41))
        self.pushB_perm_up_s1.setObjectName("pushB_perm_up_s1")
        self.pushB_multi_up_s1 = QtWidgets.QPushButton(self.tab_4)
        self.pushB_multi_up_s1.setGeometry(QtCore.QRect(180, 80, 61, 41))
        self.pushB_multi_up_s1.setObjectName("pushB_multi_up_s1")
        self.pushB_stop_s1 = QtWidgets.QPushButton(self.tab_4)
        self.pushB_stop_s1.setGeometry(QtCore.QRect(250, 80, 51, 101))
        self.pushB_stop_s1.setObjectName("pushB_stop_s1")
        self.label_25 = QtWidgets.QLabel(self.tab_4)
        self.label_25.setGeometry(QtCore.QRect(320, 40, 81, 16))
        self.label_25.setObjectName("label_25")
        self.pushB_update_rpm_s1 = QtWidgets.QPushButton(self.tab_4)
        self.pushB_update_rpm_s1.setGeometry(QtCore.QRect(70, 210, 91, 31))
        self.pushB_update_rpm_s1.setObjectName("pushB_update_rpm_s1")
        self.pushB_perm_down_s1 = QtWidgets.QPushButton(self.tab_4)
        self.pushB_perm_down_s1.setGeometry(QtCore.QRect(310, 140, 61, 41))
        self.pushB_perm_down_s1.setObjectName("pushB_perm_down_s1")
        self.label_26 = QtWidgets.QLabel(self.tab_4)
        self.label_26.setGeometry(QtCore.QRect(30, 90, 81, 41))
        self.label_26.setObjectName("label_26")
        self.label_27 = QtWidgets.QLabel(self.tab_4)
        self.label_27.setGeometry(QtCore.QRect(300, 215, 31, 21))
        self.label_27.setObjectName("label_27")
        self.tabWidget.addTab(self.tab_4, "Manual σ1")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.pushB_start_const = QtWidgets.QPushButton(self.tab_2)
        self.pushB_start_const.setGeometry(QtCore.QRect(20, 80, 101, 41))
        self.pushB_start_const.setObjectName("pushB_start_const")
        self.pushB_stop_const = QtWidgets.QPushButton(self.tab_2)
        self.pushB_stop_const.setGeometry(QtCore.QRect(20, 140, 101, 41))
        self.pushB_stop_const.setObjectName("pushB_stop_const")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(230, 80, 111, 31))
        self.label_5.setObjectName("label_5")
        self.label_11 = QtWidgets.QLabel(self.tab_2)
        self.label_11.setGeometry(QtCore.QRect(20, 20, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setStyleSheet("QLabel{color: rgb(255, 0, 0);}")
        self.label_11.setObjectName("label_11")
        self.maxvel_spinBox = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.maxvel_spinBox.setGeometry(QtCore.QRect(160, 250, 71, 31))
        self.maxvel_spinBox.setDecimals(4)
        self.maxvel_spinBox.setMaximum(120.0)
        self.maxvel_spinBox.setProperty("value", 60.0)
        self.maxvel_spinBox.setObjectName("maxvel_spinBox")
        self.label_7 = QtWidgets.QLabel(self.tab_2)
        self.label_7.setGeometry(QtCore.QRect(240, 255, 81, 21))
        self.label_7.setObjectName("label_7")
        self.sigma1_SP_spinBox = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.sigma1_SP_spinBox.setGeometry(QtCore.QRect(160, 80, 61, 31))
        self.sigma1_SP_spinBox.setDecimals(4)
        self.sigma1_SP_spinBox.setMaximum(15000.0)
        self.sigma1_SP_spinBox.setObjectName("sigma1_SP_spinBox")
        self.pushB_update_const = QtWidgets.QPushButton(self.tab_2)
        self.pushB_update_const.setGeometry(QtCore.QRect(60, 250, 91, 31))
        self.pushB_update_const.setObjectName("pushB_update_const")
        self.line_3 = QtWidgets.QFrame(self.tab_2)
        self.line_3.setGeometry(QtCore.QRect(10, 210, 361, 16))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.pushB_multi_up_s3 = QtWidgets.QPushButton(self.tab)
        self.pushB_multi_up_s3.setGeometry(QtCore.QRect(180, 80, 61, 41))
        self.pushB_multi_up_s3.setCheckable(False)
        self.pushB_multi_up_s3.setObjectName("pushB_multi_up_s3")
        self.pushB_stop_s3 = QtWidgets.QPushButton(self.tab)
        self.pushB_stop_s3.setGeometry(QtCore.QRect(250, 80, 51, 101))
        self.pushB_stop_s3.setObjectName("pushB_stop_s3")
        self.spinB_multistep_s3 = QtWidgets.QDoubleSpinBox(self.tab)
        self.spinB_multistep_s3.setGeometry(QtCore.QRect(90, 90, 71, 26))
        self.spinB_multistep_s3.setMaximum(2000.0)
        self.spinB_multistep_s3.setProperty("value", 100.0)
        self.spinB_multistep_s3.setObjectName("spinB_multistep_s3")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(20, 80, 81, 31))
        self.label_2.setObjectName("label_2")
        self.pushB_perm_up_s3 = QtWidgets.QPushButton(self.tab)
        self.pushB_perm_up_s3.setGeometry(QtCore.QRect(180, 140, 61, 41))
        self.pushB_perm_up_s3.setObjectName("pushB_perm_up_s3")
        self.label_10 = QtWidgets.QLabel(self.tab)
        self.label_10.setGeometry(QtCore.QRect(20, 17, 171, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setStyleSheet("QLabel{color: rgb(0, 128, 0);}")
        self.label_10.setObjectName("label_10")
        self.rpmSlider_s3 = QtWidgets.QSlider(self.tab)
        self.rpmSlider_s3.setGeometry(QtCore.QRect(29, 250, 321, 20))
        self.rpmSlider_s3.setMinimum(-120)
        self.rpmSlider_s3.setMaximum(120)
        self.rpmSlider_s3.setOrientation(QtCore.Qt.Horizontal)
        self.rpmSlider_s3.setObjectName("rpmSlider_s3")
        self.rpmBox_s3 = QtWidgets.QDoubleSpinBox(self.tab)
        self.rpmBox_s3.setGeometry(QtCore.QRect(200, 210, 81, 31))
        self.rpmBox_s3.setDecimals(4)
        self.rpmBox_s3.setMaximum(120.0)
        self.rpmBox_s3.setObjectName("rpmBox_s3")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(300, 215, 31, 21))
        self.label_3.setObjectName("label_3")
        self.label_8 = QtWidgets.QLabel(self.tab)
        self.label_8.setGeometry(QtCore.QRect(190, 30, 81, 31))
        self.label_8.setObjectName("label_8")
        self.pushB_update_rpm_s3 = QtWidgets.QPushButton(self.tab)
        self.pushB_update_rpm_s3.setGeometry(QtCore.QRect(70, 210, 91, 31))
        self.pushB_update_rpm_s3.setObjectName("pushB_update_rpm_s3")
        self.label_17 = QtWidgets.QLabel(self.tab)
        self.label_17.setGeometry(QtCore.QRect(190, 50, 81, 21))
        self.label_17.setObjectName("label_17")
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(30, 100, 46, 21))
        self.label_4.setObjectName("label_4")
        self.pushB_perm_down_s3 = QtWidgets.QPushButton(self.tab)
        self.pushB_perm_down_s3.setGeometry(QtCore.QRect(310, 110, 61, 41))
        self.pushB_perm_down_s3.setObjectName("pushB_perm_down_s3")
        self.label_9 = QtWidgets.QLabel(self.tab)
        self.label_9.setGeometry(QtCore.QRect(320, 40, 81, 31))
        self.label_9.setObjectName("label_9")
        self.label_18 = QtWidgets.QLabel(self.tab)
        self.label_18.setGeometry(QtCore.QRect(320, 50, 81, 21))
        self.label_18.setObjectName("label_18")
        self.line_2 = QtWidgets.QFrame(self.tab)
        self.line_2.setGeometry(QtCore.QRect(10, 270, 361, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.pushB_set_closed = QtWidgets.QPushButton(self.tab)
        self.pushB_set_closed.setGeometry(QtCore.QRect(260, 290, 101, 41))
        self.pushB_set_closed.setObjectName("pushB_set_closed")
        self.pushB_close_valve = QtWidgets.QPushButton(self.tab)
        self.pushB_close_valve.setGeometry(QtCore.QRect(30, 290, 131, 41))
        self.pushB_close_valve.setStyleSheet("QPushButton{color: rgb(0, 200, 100);}")
        self.pushB_close_valve.setObjectName("pushB_close_valve")
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.pushB_quench_stop = QtWidgets.QPushButton(self.tab_3)
        self.pushB_quench_stop.setGeometry(QtCore.QRect(20, 140, 101, 41))
        self.pushB_quench_stop.setObjectName("pushB_quench_stop")
        self.label_14 = QtWidgets.QLabel(self.tab_3)
        self.label_14.setGeometry(QtCore.QRect(20, 20, 201, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_14.setFont(font)
        self.label_14.setStyleSheet("QLabel{color: rgb(0, 128, 0);}")
        self.label_14.setObjectName("label_14")
        self.dsigma_SP_spinBox = QtWidgets.QSpinBox(self.tab_3)
        self.dsigma_SP_spinBox.setGeometry(QtCore.QRect(160, 250, 61, 31))
        self.dsigma_SP_spinBox.setMaximum(600)
        self.dsigma_SP_spinBox.setProperty("value", 200)
        self.dsigma_SP_spinBox.setObjectName("dsigma_SP_spinBox")
        self.pushB_quench_start = QtWidgets.QPushButton(self.tab_3)
        self.pushB_quench_start.setGeometry(QtCore.QRect(20, 80, 101, 41))
        self.pushB_quench_start.setObjectName("pushB_quench_start")
        self.label_6 = QtWidgets.QLabel(self.tab_3)
        self.label_6.setGeometry(QtCore.QRect(230, 250, 111, 31))
        self.label_6.setObjectName("label_6")
        self.rpmBox_prequench = QtWidgets.QDoubleSpinBox(self.tab_3)
        self.rpmBox_prequench.setGeometry(QtCore.QRect(160, 80, 62, 31))
        self.rpmBox_prequench.setDecimals(3)
        self.rpmBox_prequench.setProperty("value", 0.5)
        self.rpmBox_prequench.setObjectName("rpmBox_prequench")
        self.rpmBox_quench = QtWidgets.QDoubleSpinBox(self.tab_3)
        self.rpmBox_quench.setGeometry(QtCore.QRect(160, 141, 62, 31))
        self.rpmBox_quench.setDecimals(3)
        self.rpmBox_quench.setProperty("value", 0.005)
        self.rpmBox_quench.setObjectName("rpmBox_quench")
        self.prequenchrpm = QtWidgets.QLabel(self.tab_3)
        self.prequenchrpm.setGeometry(QtCore.QRect(160, 110, 141, 21))
        self.prequenchrpm.setObjectName("prequenchrpm")
        self.label_15 = QtWidgets.QLabel(self.tab_3)
        self.label_15.setGeometry(QtCore.QRect(160, 170, 121, 21))
        self.label_15.setObjectName("label_15")
        self.pushB_update_quench = QtWidgets.QPushButton(self.tab_3)
        self.pushB_update_quench.setGeometry(QtCore.QRect(60, 250, 91, 31))
        self.pushB_update_quench.setObjectName("pushB_update_quench")
        self.pushB_goto_prequench = QtWidgets.QPushButton(self.tab_3)
        self.pushB_goto_prequench.setGeometry(QtCore.QRect(260, 140, 101, 41))
        self.pushB_goto_prequench.setObjectName("pushB_goto_prequench")
        self.line = QtWidgets.QFrame(self.tab_3)
        self.line.setGeometry(QtCore.QRect(10, 210, 361, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tabWidget.addTab(self.tab_3, "")
        self.invert_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.invert_checkBox.setGeometry(QtCore.QRect(130, 390, 191, 21))
        self.invert_checkBox.setObjectName("invert_checkBox")
        self.lcd_actvel_s1 = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_actvel_s1.setGeometry(QtCore.QRect(510, 130, 64, 23))
        self.lcd_actvel_s1.setSmallDecimalPoint(False)
        self.lcd_actvel_s1.setObjectName("lcd_actvel_s1")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(510, 100, 91, 21))
        self.label_13.setObjectName("label_13")
        self.initADC_s1 = QtWidgets.QCheckBox(self.centralwidget)
        self.initADC_s1.setGeometry(QtCore.QRect(410, 30, 151, 21))
        self.initADC_s1.setObjectName("initADC_s1")
        self.initADC_s3 = QtWidgets.QCheckBox(self.centralwidget)
        self.initADC_s3.setGeometry(QtCore.QRect(410, 60, 151, 21))
        self.initADC_s3.setObjectName("initADC_s3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(410, 200, 441, 231))
        self.label.setObjectName("label")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setGeometry(QtCore.QRect(650, 0, 181, 101))
        self.label_16.setObjectName("label_16")
        self.lcd_actvel_s3 = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_actvel_s3.setGeometry(QtCore.QRect(510, 170, 64, 23))
        self.lcd_actvel_s3.setObjectName("lcd_actvel_s3")
        self.label_28 = QtWidgets.QLabel(self.centralwidget)
        self.label_28.setGeometry(QtCore.QRect(430, 120, 61, 31))
        self.label_28.setStyleSheet("QLabel{color: rgb(255, 0, 0);}")
        self.label_28.setObjectName("label_28")
        self.label_29 = QtWidgets.QLabel(self.centralwidget)
        self.label_29.setGeometry(QtCore.QRect(430, 160, 61, 31))
        self.label_29.setStyleSheet("QLabel{color: rgb(0, 128, 0)\n"
";}")
        self.label_29.setObjectName("label_29")
        self.lcd_stress_s1 = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_stress_s1.setGeometry(QtCore.QRect(600, 130, 64, 23))
        self.lcd_stress_s1.setStyleSheet("QLCDNumber {\n"
"    background-color: rgb(255, 0, 0, 64);\n"
"}\n"
"")
        self.lcd_stress_s1.setSmallDecimalPoint(False)
        self.lcd_stress_s1.setObjectName("lcd_stress_s1")
        self.label_30 = QtWidgets.QLabel(self.centralwidget)
        self.label_30.setGeometry(QtCore.QRect(600, 100, 91, 21))
        self.label_30.setObjectName("label_30")
        self.lcd_stress_s3 = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_stress_s3.setGeometry(QtCore.QRect(600, 170, 64, 23))
        self.lcd_stress_s3.setStyleSheet("QLCDNumber{background-color: rgb(0, 128, 0, 64);}")
        self.lcd_stress_s3.setProperty("value", 0.0)
        self.lcd_stress_s3.setObjectName("lcd_stress_s3")
        self.label_31 = QtWidgets.QLabel(self.centralwidget)
        self.label_31.setGeometry(QtCore.QRect(680, 100, 131, 21))
        self.label_31.setObjectName("label_31")
        self.lcd_dstress = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcd_dstress.setGeometry(QtCore.QRect(710, 150, 64, 21))
        self.lcd_dstress.setObjectName("lcd_dstress")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 835, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.quitButton.setText(_translate("MainWindow", "QUIT"))
        self.pushB_multi_down_s1.setText(_translate("MainWindow", "step down"))
        self.label_20.setText(_translate("MainWindow", "pistion"))
        self.label_21.setText(_translate("MainWindow", "<html><head/><body><p>retract </p><p><br/></p></body></html>"))
        self.label_22.setText(_translate("MainWindow", "<html><head/><body><p>Manual Mode σ<span style=\" vertical-align:sub;\">1</span></p></body></html>"))
        self.label_23.setText(_translate("MainWindow", "multi step"))
        self.label_24.setText(_translate("MainWindow", "sample"))
        self.pushB_perm_up_s1.setText(_translate("MainWindow", "perm up"))
        self.pushB_multi_up_s1.setText(_translate("MainWindow", "step up"))
        self.pushB_stop_s1.setText(_translate("MainWindow", "stop"))
        self.label_25.setText(_translate("MainWindow", "<html><head/><body><p>shorten </p><p><br/></p><p><br/></p></body></html>"))
        self.pushB_update_rpm_s1.setText(_translate("MainWindow", "Update"))
        self.pushB_perm_down_s1.setText(_translate("MainWindow", "perm down"))
        self.label_26.setText(_translate("MainWindow", "[deg]"))
        self.label_27.setText(_translate("MainWindow", "RPM"))
        self.pushB_start_const.setText(_translate("MainWindow", "START"))
        self.pushB_stop_const.setText(_translate("MainWindow", "STOP"))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p>σ<span style=\" vertical-align:sub;\">1 </span>setpoint [MPa]</p></body></html>"))
        self.label_11.setText(_translate("MainWindow", "Const Stress Mode"))
        self.label_7.setText(_translate("MainWindow", "<html><head/><body><p>max. RPM</p></body></html>"))
        self.pushB_update_const.setText(_translate("MainWindow", "Update "))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Const Stress"))
        self.pushB_multi_up_s3.setText(_translate("MainWindow", "step up"))
        self.pushB_stop_s3.setText(_translate("MainWindow", "stop"))
        self.label_2.setText(_translate("MainWindow", "quench by "))
        self.pushB_perm_up_s3.setText(_translate("MainWindow", "perm up"))
        self.label_10.setText(_translate("MainWindow", "<html><head/><body><p>Manual Mode σ<span style=\" vertical-align:sub;\">3</span></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "RPM"))
        self.label_8.setText(_translate("MainWindow", "<html><head/><body><p>open </p></body></html>"))
        self.pushB_update_rpm_s3.setText(_translate("MainWindow", "Update"))
        self.label_17.setText(_translate("MainWindow", "valve"))
        self.label_4.setText(_translate("MainWindow", "[MPa]"))
        self.pushB_perm_down_s3.setText(_translate("MainWindow", "perm down"))
        self.label_9.setText(_translate("MainWindow", "<html><head/><body><p>close</p><p><br/></p></body></html>"))
        self.label_18.setText(_translate("MainWindow", "<html><head/><body><p>valve</p></body></html>"))
        self.pushB_set_closed.setText(_translate("MainWindow", "set_closed"))
        self.pushB_close_valve.setText(_translate("MainWindow", "close oil valve"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Manual σ3"))
        self.pushB_quench_stop.setText(_translate("MainWindow", "STOP"))
        self.label_14.setText(_translate("MainWindow", "Quenching Mode"))
        self.pushB_quench_start.setText(_translate("MainWindow", "START"))
        self.label_6.setText(_translate("MainWindow", "∆σ  setpoint [MPa]"))
        self.prequenchrpm.setText(_translate("MainWindow", "prequench RPM"))
        self.label_15.setText(_translate("MainWindow", "quench RPM"))
        self.pushB_update_quench.setText(_translate("MainWindow", "Update "))
        self.pushB_goto_prequench.setText(_translate("MainWindow", "prequench velocity"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Quenching"))
        self.invert_checkBox.setText(_translate("MainWindow", "invert direction: pos 2 / 4"))
        self.label_13.setText(_translate("MainWindow", "actual velocity"))
        self.initADC_s1.setText(_translate("MainWindow", "read ADC: σ1"))
        self.initADC_s3.setText(_translate("MainWindow", "read ADC: σ3"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">For Quenching: </span></p><p>- prequench rpm: to open valve until oilpressure changes (fast)</p><p>- quench rpm: to open the valve all the way open (slow)</p><p>(target position := valve all the way opened)</p><p>- dsigma setpoint is the const. diff. stress [Mpa] </p><p>s1 establishes via PID as a passive reaction on s3 action</p><p><br/></p></body></html>"))
        self.label_16.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">close</span> app<span style=\" font-weight:600;\"> only </span></p><p align=\"center\">via the <span style=\" font-weight:600;\">QUIT-button!</span></p></body></html>"))
        self.label_28.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:9pt;\">Motor σ</span><span style=\" font-size:9pt; vertical-align:sub;\">1</span></p></body></html>"))
        self.label_29.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:9pt;\">Motor σ</span><span style=\" vertical-align:sub;\">3</span></p></body></html>"))
        self.label_30.setText(_translate("MainWindow", "stress [MPa]"))
        self.label_31.setText(_translate("MainWindow", "differential Stress [MPa]"))
from pyqtgraph import PlotWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
