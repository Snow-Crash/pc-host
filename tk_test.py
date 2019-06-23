# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 17:47:02 2019

@author: hw
"""

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkinter as tk
import tkinter.ttk as ttk
import sys
#
#class Application(tk.Frame):
#    def __init__(self, master=None):
#        tk.Frame.__init__(self,master)
#        self.createWidgets()
#
#    def createWidgets(self):
#        
#        fig, ax = plt.subplots()
#        for i in range(10):
#            line = ax.plot(np.random.randn(450))
#        plt.show(block=False)
#        fig.canvas.draw()
#        
#        canvas=FigureCanvasTkAgg(fig,master=root)
#        canvas.get_tk_widget().grid(row=0,column=1)
#        canvas.show()
#
#        self.plotbutton=tk.Button(master=root, text="plot", command=lambda: self.plot(canvas,ax, fig))
#        self.plotbutton.grid(row=0,column=0)
#
#    def plot(self,canvas,ax, fig):
#        for i in range(100):
#            theta=np.random.rand()
#            r=np.random.rand()
##            ax.plot(theta,r,linestyle="None")
##            canvas.draw()
##            ax.clear()
#            
#            
#            
#            #here set axes
#            ax.draw_artist(ax.patch)
#            for n, l in enumerate(ax.lines):
#                l.set_ydata( np.random.rand(450))
##                
#            ax.draw_artist(l)
#            ax.clear()
#            fig.canvas.update()
#            fig.canvas.flush_events()
            
def plot():
    for i in range(450):   
        #here set axes
#        ax_v.draw_artist(ax_v.patch)
        for n, l in enumerate(ax_v.lines):
            l.set_ydata( np.random.rand(450) + n)
#                
        ax_v.draw_artist(l)
#        ax.clear()
        fig_v.canvas.show()
        fig_v.canvas.flush_events()
#        print(i)
        
#        ax_psp.draw_artist(ax_psp.patch)
        for n, l in enumerate(ax_psp.lines):
            l.set_ydata( np.random.rand(450) + n)
#                
        ax_psp.draw_artist(l)
#        ax.clear()
        fig_psp.canvas.show()
        fig_psp.canvas.flush_events()
            

root=tk.Tk()
app=tk.Frame(root)


fig_v, ax_v = plt.subplots()
for i in range(10):
    line = ax_v.plot(np.random.randn(450))
plt.show(block=False)
fig_v.canvas.draw()

canvas_v=FigureCanvasTkAgg(fig_v,master=root)
canvas_v.get_tk_widget().grid(row=0,column=1)
canvas_v.show()

fig_psp, ax_psp = plt.subplots()
for i in range(22):
    line = ax_psp.plot(np.random.randn(450))
fig_psp.canvas.draw()

canvas_psp=FigureCanvasTkAgg(fig_psp,master=root)
canvas_psp.get_tk_widget().grid(row=0,column=2)
canvas_psp.show()

plotbutton=tk.Button(master=root, text="plot", command=lambda: plot())
plotbutton.grid(row=0,column=0)
app.mainloop()