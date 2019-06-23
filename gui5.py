# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 21:45:50 2019

@author: hw

reference
https://stackoverflow.com/questions/45046239/python-realtime-plot-using-pyqtgraph
"""
# Import libraries
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import PyQt5.QtWidgets


#pg.setConfigOptions(antialias=True)
#pg.setConfigOptions(useOpenGL=True)


## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()

## Create some widgets to be placed inside
btn = QtGui.QPushButton('press me')
text = QtGui.QLineEdit('enter text')
listw = QtGui.QListWidget()


raw_data_plot = pg.PlotWidget()
raw_data_lines = []
for i in range(22):
    line = raw_data_plot.plot(np.random.rand(450))
    raw_data_lines.append(line)

psp_plot = pg.PlotWidget()
psp_lines = []
for i in range(22):
    line = psp_plot.plot(np.random.rand(450))
    psp_lines.append(line)

voltage_plot = pg.PlotWidget()
voltage_lines = []
for i in range(10):
    line = voltage_plot.plot(np.random.rand(450))
    voltage_lines.append(line)

inspike_plot = pg.PlotWidget()
s1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
pos = np.random.normal(size=(2,300), scale=1e-5)
spots = [{'pos': pos[:,i], 'data': 1} for i in range(300)] + [{'pos': [0,0], 'data': 1}]
s1.addPoints(spots)
inspike_plot.addItem(s1)
#inspike_lines = []
#for i in range(110):
#    line = inspike_plot.plot(np.random.rand(450))
#    inspike_lines.append(line)

outspike_plot = pg.PlotWidget()
outspike_lines = []
for i in range(10):
    line = outspike_plot.plot(np.random.rand(450))
    outspike_lines.append(line)

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

layout.addWidget(btn, 0, 0)   # button goes in upper-left
layout.addWidget(text, 1, 0)   # text edit goes in middle-left
layout.addWidget(listw, 2, 0)  # list widget goes in bottom-left
layout.addWidget(raw_data_plot, 0, 1, 1, 1)  # 
layout.addWidget(inspike_plot, 0, 2, 1, 1)  # 
layout.addWidget(psp_plot, 1, 1, 1, 1)  # 
layout.addWidget(voltage_plot, 1, 2, 1, 1)  # 
layout.addWidget(outspike_plot, 2, 1, 1, 1)  # 

def update():
    for t in range(500):
        for i in range(22):
            raw_data_lines[i].setData(np.random.random(450) + i)  

        
        for i in range(10):
            voltage_lines[i].setData(np.random.random(450) + i)
            outspike_lines[i].setData(np.random.random(450) + i)
        
#        for i in range(110):
#            inspike_lines[i].setData(np.random.random(450) + i)
        
        for i in range(22):
            psp_lines[i].setData(np.random.random(450) + i)
            
        QtGui.QApplication.processEvents()    # you MUST process the plot now

btn.clicked.connect(update)

## Display the widget as a new window
w.show()

## Start the Qt event loop
app.exec_()