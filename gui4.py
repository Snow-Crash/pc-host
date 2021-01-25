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
from timeit import default_timer as timer


# Create object serial port
portName = "COM12"                      # replace this port name by yours!
baudrate = 9600

### START QtApp #####
app = QtGui.QApplication([])            # you MUST do this once (initialize things)
####################



win = pg.GraphicsWindow(title="Signal from serial port") # creates a window


p = win.addPlot(title="Realtime plot")  # creates empty space for the plot in the window

lines = []
for i in range(110):
    curve = p.plot()                        # create an empty "plot" (a curve to plot)
    lines.append(curve)

windowWidth = 500                       # width of the window displaying the curve
Xm = np.linspace(0,0,windowWidth)          # create array that will contain the relevant time series     
ptr = -windowWidth                      # set first x position

# Realtime data plot. Each time this function is called, the data display is updated
def update():
    global curve, ptr, Xm, lines    
    Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    value = np.random.rand()                # read line (single value) from the serial port
    Xm[-1] = float(value)                 # vector containing the instantaneous values      
    ptr += 1                              # update x position for displaying the curve
#    curve.setData(Xm)                     # set the curve with this data
#    curve.setPos(ptr,0)                   # set x position in the graph to 0
    for i in range(60):
        lines[i].setData(np.random.random(450) + i)  
#        lines[i].setPos(ptr,0)  
    QtGui.QApplication.processEvents()    # you MUST process the plot now

start = timer()
### MAIN PROGRAM #####    
# this is a brutal infinite loop calling your realtime data plot
for i in range(450):
    update()
end = timer()
print(end - start)

### END QtApp ####
pg.QtGui.QApplication.exec_() # you MUST put this at the end
##################