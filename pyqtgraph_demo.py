# -*- coding: utf-8 -*-
"""
    Animated 3D sinc function

    requires:
        1. pyqtgraph
            - download from here http://www.pyqtgraph.org/
        2. pyopenGL
            - if you have Anaconda, run the following command
            >>> conda install -c anaconda pyopengl
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import time


class Visualizer(object):
    def __init__(self):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 40
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 110, 1920, 1080)
        self.w.show()

        self.phase = 0
        self.lines = 50
        self.points = 1000
#        self.y = np.linspace(-10, 10, self.lines)
        self.y = np.zeros(self.lines)
        self.x = np.linspace(-10, 10, self.points)

        for i, line in enumerate(self.y):
            y = np.array([line] * self.points)
            d = np.sqrt(self.x ** 2 + y ** 2)
            sine = 10 * np.sin(d + self.phase)
            pts = np.vstack([self.x, y, sine]).transpose()
            self.traces[i] = gl.GLLinePlotItem(
                pos=pts,
                color=pg.glColor((i, self.lines * 1.3)),
                width=(i + 1) / 10,
                antialias=True
            )
            self.w.addItem(self.traces[i])

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points, color, width):
        self.traces[name].setData(pos=points, color=color, width=width)

    def update(self):
        stime = time.time()
        for j in range(100):
            for i, line in enumerate(self.y):
                y = np.array([line] * self.points)
    
                amp = 10 / (i + 1)
                phase = self.phase * (i + 1) - 10
                freq = self.x * (i + 1) / 10
    
                sine = amp * np.sin(freq - phase)
                pts = np.vstack([self.x, y, sine]).transpose()
    
                self.set_plotdata(
                    name=i, points=pts,
                    color=pg.glColor((i, self.lines * 1.3)),
                    width=3
                )
                self.phase -= .0002
                print('i:',i)
            print('j:',j)
            self.app.processEvents()

        print('{:.0f} FPS'.format(1 / (time.time() - stime)))

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10000)
        self.start()


# Start event loop.
if __name__ == '__main__':
#    v = Visualizer()
#    v.animation()
    
#    pg.setConfigOption('background', 'w')
    app = QtGui.QApplication(sys.argv)
    w = gl.GLViewWidget()
    w.setBackgroundColor('w')
#    w.opts['bgcolor'] = 'w'
    w.opts['azimuth'] = 90
    w.opts['elevation'] = 0
    w.setGeometry(0, 110, 1920, 1080)
    w.show()
    
    traces = dict()
    
    phase = 0
    lines = 110
    points = 450
#        self.y = np.linspace(-10, 10, self.lines)
    yy = np.zeros(lines)
#    x = np.linspace(0, 450, points)
    x = np.array(np.arange(0,450))

    for i, line in enumerate(yy):
        y = np.array([line] * points)
        d = np.sqrt(x ** 2 + y ** 2)
        sine = 10 * np.sin(d + phase)
        pts = np.vstack([x, y, sine]).transpose()
        traces[i] = gl.GLLinePlotItem(
            pos=pts,
            color=pg.glColor((i, lines * 1.3)),
            width=(i + 1) / 10,
            antialias=True,
        )
        #if use white background
        #reference: https://github.com/pyqtgraph/pyqtgraph/issues/193
        traces[i].setGLOptions('translucent')
        w.addItem(traces[i])
    
    for j in range(100):
        for i, line in enumerate(yy):
            y = np.array([line] * points)
    
            amp = 10 / (i + 1)
            phase = phase * (i + 1) - 10
            freq = x * (i + 1) / 10

            x =  np.array(np.arange(0,j))
            phase = phase * (i + 1) - 10
            freq = x * (i + 1) / 10
            y = np.zeros(j)
            z = np.random.rand(j) + i - 25
            
            pts = np.vstack([x, y, z]).transpose()
            
            traces[i].setData(pos=pts, color=pg.glColor((i, lines * 1.3)), width=3)
            phase -= .0002

        app.processEvents()
        time.sleep(1)
    
