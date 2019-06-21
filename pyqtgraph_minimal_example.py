# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 22:47:37 2019

@author: hw
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import time
from PyQt5 import QtTest


app = QtGui.QApplication(sys.argv)
w = gl.GLViewWidget()
w.setBackgroundColor('w')
w.opts['azimuth'] = 90
w.opts['elevation'] = 0
w.setGeometry(0, 110, 1920, 1080)
w.show()

traces = dict()

#add 110 lines to plot
for i in range(110):
    x = np.array(range(450))
    y = np.zeros(450)
    z = np.zeros(450)
    pts = np.vstack([x, y, z]).transpose()
    traces[i] = gl.GLLinePlotItem(
        pos=pts,
        color=pg.glColor((i, 110 * 1.3)),
        width=(i + 1) / 10,
        antialias=True,
    )
    #if use white background
    #reference: https://github.com/pyqtgraph/pyqtgraph/issues/193
    traces[i].setGLOptions('translucent')
    w.addItem(traces[i])

for j in range(450):
    for i in range(110):  
        #coordinates
        x = np.array(range(j))
        #all lines in one plane
        y = np.zeros(j)
        #random z coordinate
        z = np.random.rand(j) + i     
        pts = np.vstack([x, y, z]).transpose()
        
        traces[i].setData(pos=pts, color=pg.glColor((i, 110 * 1.3)), width=3)
    
    #if you want the animation slower, uncomment this.
    #it can slow down animation while keep the window still responsive
#    QtTest.QTest.qWait(1000)
    
    #without this, no animation
    app.processEvents()
