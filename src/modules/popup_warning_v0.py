# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 12:53:12 2024

@author: wq271
"""

import pandas as pd 

# df = pd.read_csv(r'C:\Users\wq271\AAA_programming\Projects\griggs_control\src\positions_valve.txt', sep='\t')
# df.columns = df.columns.str.strip()
# print(df.head)
# print(df.loc[0, 'closed'], df.loc[0, 'distance'], df.loc[0, 'current'])

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Dialog")
        self.setGeometry(200, 200, 200, 150)  # Set position and size

        # Create and set layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add a label
        label = QLabel("WARNING \n please make sure invert direction checkbox setting is correct before continuing!")
        font = QFont('Arial', 10)
        label.setFont(font)
        layout.addWidget(label)

        # Add an OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)  # Closes the dialog with an "accept" result
        layout.addWidget(ok_button)


# Main application
if __name__ == "__main__":
    app = QApplication([])

    # Create and show the dialog
    dialog = CustomDialog()
    if dialog.exec_():  # Open as a modal dialog and check the return value
        print("Dialog accSWepted!")

    app.exec_()
