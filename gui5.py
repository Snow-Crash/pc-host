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
from pyqtgraph.widgets.RemoteGraphicsView import RemoteGraphicsView

WINDOW = 450

#pg.setConfigOptions(antialias=True)
#pg.setConfigOptions(useOpenGL=True)
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', (0, 0, 0))


## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
              '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
              '#bcbd22', '#17becf']

## Create some widgets to be placed inside
btn = QtGui.QPushButton('Run')
text = QtGui.QLineEdit('enter text')
listw = QtGui.QListWidget()
control_panel = QtGui.QVBoxLayout()
control_panel.addWidget(btn)
control_panel.addWidget(text)
control_panel.addWidget(listw)

raw_data_plot = pg.PlotWidget()
raw_data_lines = []
for i in range(22):
    line = raw_data_plot.plot(np.random.rand(WINDOW), pen=colors[i%len(colors)])
    raw_data_lines.append(line)
raw_data_plot.plotItem.setTitle('Input stimulus')

psp_plot = pg.PlotWidget()
psp_plot.plotItem.setTitle('PSP')
psp_lines = []
for i in range(22):
    line = psp_plot.plot(np.random.rand(WINDOW))
    psp_lines.append(line)

voltage_plot = pg.PlotWidget()
voltage_lines = []
for i in range(10):
    line = voltage_plot.plot(np.random.rand(WINDOW))
    voltage_lines.append(line)
voltage_plot.plotItem.setTitle('Membrane Potential')

inspike_plot = pg.PlotWidget()
in_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 0, 120))
in_scatter.addPoints(np.random.rand(20), np.random.rand(20))
inspike_plot.addItem(in_scatter)
inspike_plot.plotItem.setTitle('Input Spike Train')

outspike_plot = pg.PlotWidget()
out_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 0, 120))
out_scatter.addPoints(np.random.rand(20), np.random.rand(20))
outspike_plot.addItem(out_scatter)
outspike_plot.plotItem.setTitle('Output Spike Train')

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

layout.addLayout(control_panel, 0, 0)   
#layout.addWidget(text, 1, 0)  
#layout.addWidget(listw, 2, 0)  
layout.addWidget(raw_data_plot, 0, 1, 1, 1)  # 
layout.addWidget(inspike_plot, 0, 2, 1, 1)  # 
layout.addWidget(psp_plot, 1, 1, 1, 1)  # 
layout.addWidget(voltage_plot, 1, 2, 1, 1)  # 
layout.addWidget(outspike_plot, 2, 1, 1, 1)  # 

def update():
    
    for t in range(300):
        for i in range(22):
            raw_data_lines[i].setData(np.random.random(WINDOW) + i)
            psp_lines[i].setData(np.random.random(WINDOW) + i)

        for i in range(10):
            voltage_lines[i].setData(np.random.random(WINDOW) + i)
        
        in_scatter.setData(np.random.rand(20), np.random.rand(20))
        out_scatter.setData(np.random.rand(20), np.random.rand(20))
        QtGui.QApplication.processEvents()    # you MUST process the plot now

btn.clicked.connect(update)

## Display the widget as a new window
w.show()

## Start the Qt event loop
app.exec_()