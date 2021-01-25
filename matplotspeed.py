# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 03:27:06 2019

@author: hw
"""

import matplotlib.pyplot as plt
import numpy as np
import time

x = np.arange(0, 2*np.pi, 0.1)
y = np.sin(x)

fig, axes = plt.subplots(nrows=6)

fig.show()

# We need to draw the canvas before we start animating...
fig.canvas.draw()

styles = ['r-', 'g-', 'y-', 'm-', 'k-', 'c-']
def plot(ax, style):
    return ax.plot(x, y, style, animated=True)[0]
lines = [plot(ax, style) for ax, style in zip(axes, styles)]

# Let's capture the background of the figure
backgrounds = [fig.canvas.copy_from_bbox(ax.bbox) for ax in axes]

tstart = time.time()
for i in range(1, 500):
    items = enumerate(zip(lines, axes, backgrounds), start=1)
    for j, (line, ax, background) in items:
        fig.canvas.restore_region(background)
        line.set_ydata(np.sin(j*x + i/10.0))
        ax.draw_artist(line)
        fig.canvas.blit(ax.bbox)
        plt.pause(0.00001)
    print(i)

print ('FPS:' , 2000/(time.time()-tstart))

#####################################################
#https://bastibe.de/2013-05-30-speeding-up-matplotlib.html
fig, ax = plt.subplots()
line, = ax.plot(np.random.randn(100))
plt.show(block=False)
fig.canvas.draw()
tstart = time.time()
num_plots = 0
while time.time()-tstart < 5:
    line.set_ydata(np.random.randn(100))
    ax.draw_artist(ax.patch)
    ax.draw_artist(line)
    fig.canvas.update()
    fig.canvas.flush_events()
    num_plots += 1
print(num_plots/5)



#####################################################
    fig, ax = plt.subplots()
#    line, = ax.plot(np.arange(9000), np.random.randn(9000))
    for i in range(110):
        line, = ax.plot(np.arange(450), np.random.randn(450))
    fig.canvas.draw()
    plt.show(block=False)
    
    tstart = time.time()
    num_plots = 0
    while time.time()-tstart < 5:
        i = 0
        for line in ax.lines: 
            line.set_ydata(np.random.randn(450))
        for line in ax.lines: 
            ax.draw_artist(ax.patch)
            ax.draw_artist(line)
            i += 1
        fig.canvas.update()
        fig.canvas.flush_events()
            
        num_plots += 1
    print(num_plots/5)

################################################################