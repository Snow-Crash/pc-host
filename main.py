import multiprocessing
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as Tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def write_only(input_array,n):
    for i in range (100):
        n = n + 1
        input_array.append(n)
        print("write append", n)

def read_only(input_array):
    for i in range(100):
        print("read print:", input_array)

#def draw(input_array):
    

if __name__ == '__main__':
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    manager = multiprocessing.Manager()
    shared_list = manager.list()
    n = 0
    process1 = multiprocessing.Process(
        target=write_only, args=[shared_list,n])
    process2 = multiprocessing.Process(
        target=read_only, args=[shared_list])
    
    process1.start()
    process2.start()

    for i in range(100):
        print('main:', shared_list)

    
    process1.join()

    process2.join()
    
    